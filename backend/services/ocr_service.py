import csv
import io
import re
from dataclasses import dataclass
from typing import Any

import cv2
import easyocr
import numpy as np

_easyocr_reader = None

def _get_ocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        _easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    return _easyocr_reader

VALID_GRADES = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F', 'W', 'I', 'X'}
# Lenient pattern to catch OCR mistakes like MAT I16, CSE 2I5
COURSE_CODE_PATTERN = re.compile(r'^[A-Z]{2,4}\s*[\dIOlSZ]{2,4}$')


@dataclass
class OCRResult:
    rows: list[dict[str, Any]]
    csv_text: str
    warnings: list[str]
    confidence_avg: float
    extracted_row_count: int


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    img_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    coords = np.column_stack(np.where(enhanced > 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        if abs(angle) > 0.5:
            (h, w) = enhanced.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            enhanced = cv2.warpAffine(enhanced, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return enhanced


def get_text_center(box):
    x_coords = [point[0] for point in box]
    y_coords = [point[1] for point in box]
    return (sum(x_coords) / 4, sum(y_coords) / 4)


async def process_ocr(image_bytes: bytes) -> OCRResult:
    preprocessed = preprocess_image(image_bytes)
    
    reader = _get_ocr_reader()
    results = reader.readtext(preprocessed)
    
    processed_results = []
    for box, text, conf in results:
        x_center, y_center = get_text_center(box)
        processed_results.append({
            'text': text.strip(),
            'conf': conf,
            'x': x_center,
            'y': y_center,
            'box': box
        })
    
    # Calculate page midpoint for column detection
    max_x = max(item['x'] for item in processed_results) if processed_results else 1000
    page_midpoint = max_x / 2
    
    rows = []
    warnings = []
    confidences = []
    used_indices = set()
    
    for i, item in enumerate(processed_results):
        if i in used_indices:
            continue
            
        text = item['text'].upper().replace(' ', '')
        if not COURSE_CODE_PATTERN.match(text):
            continue
        
        # Normalize common OCR digit mistakes inside the course code
        prefix_match = re.match(r'^([A-Z]{2,4}?)([\dIOlSZ]{2,4})$', text)
        if prefix_match:
            prefix, suffix = prefix_match.groups()
            suffix = suffix.replace('I', '1').replace('L', '1').replace('O', '0').replace('S', '5').replace('Z', '2')
            if len(suffix) == 2:
                # If only 2 digits, maybe a 1 was missed in the middle
                suffix = suffix[0] + '1' + suffix[1] 
            course_code = prefix + suffix
        else:
            course_code = text
        course_conf = item['conf']
        row_y = item['y']
        
        row_items = [item]
        used_indices.add(i)
        
        for j, other in enumerate(processed_results):
            if j in used_indices:
                continue
            # Must be on the same vertical line
            if abs(other['y'] - row_y) <= 20:
                # Check if they are in the same half of the page
                is_left = item['x'] < page_midpoint
                other_is_left = other['x'] < page_midpoint
                if is_left == other_is_left:
                    row_items.append(other)
                    used_indices.add(j)
        
        row_items.sort(key=lambda x: x['x'])
        
        course_name_parts = []
        credits = ""
        grade = ""
        semester = ""
        
        for item in row_items:
            t = item['text']
            t_upper = t.upper()
            
            if t_upper == course_code:
                continue
            
            # Split by space to handle cases where grade/credits merge with noise e.g. '3.0 D' or '[13.0TTI D'
            tokens = t_upper.split()
            
            for token in tokens:
                if token in VALID_GRADES:
                    if not grade:
                        grade = token
                    continue
                
                # Try to extract credits if it's a number
                if re.match(r'^\d+\.?\d*$', token):
                    if not credits:
                        credits = token
                    continue
                
                sem_match = re.search(r'(FA\d{2}|SP\d{2}|SU\d{2}|\d{4})', token)
                if sem_match:
                    if not semester:
                        semester = sem_match.group(1)
                    continue
                
                if token in {'FALL', 'SPRING', 'SUMMER', 'JAN', 'JUL'}:
                    if not semester:
                        semester = token
                    continue
            
            # Reconstruct course name from original text, trying to strip noise
            # Skip appending if this entire text block was just a grade or credit
            if len(tokens) == 1 and (tokens[0] in VALID_GRADES or re.match(r'^\d+\.?\d*$', tokens[0])):
                continue
            course_name_parts.append(t)
        
        course_name = " ".join(course_name_parts[:5])
        
        if course_conf < 0.30:
            warnings.append(f"Row {len(rows)+1}: Low confidence ({course_conf:.2f}) for {course_code} - excluded")
            continue
        elif course_conf < 0.60:
            warnings.append(f"Row {len(rows)+1}: Medium confidence ({course_conf:.2f}) for {course_code}")
        
        confidences.append(course_conf)
        
        rows.append({
            "course_code": course_code,
            "course_name": course_name,
            "credits": credits,
            "grade": grade,
            "semester": semester
        })
    
    confidence_avg = sum(confidences) / len(confidences) if confidences else 0.0
    
    csv_text = extract_csv_text(rows)
    
    return OCRResult(
        rows=rows,
        csv_text=csv_text,
        warnings=warnings,
        confidence_avg=confidence_avg,
        extracted_row_count=len(rows)
    )


def extract_csv_text(rows: list[dict]) -> str:
    if not rows:
        return ""
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["course_code", "course_name", "credits", "grade", "semester"])
    
    for row in rows:
        writer.writerow([
            row.get("course_code", ""),
            row.get("course_name", ""),
            row.get("credits", ""),
            row.get("grade", ""),
            row.get("semester", "")
        ])
    
    return output.getvalue()


async def process_pdf_first_page(pdf_bytes: bytes) -> bytes:
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=300)
        if images:
            img = images[0]
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    except Exception:
        pass
    raise ValueError("Could not convert PDF to image. Please upload as PNG or JPG instead.")
