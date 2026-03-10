import pytest
import asyncio
from backend.services.ocr_service import process_ocr, process_pdf_first_page


@pytest.fixture
def sample_image_path():
    return "tests/nsu_transcript_ocr/Screenshot_20260309_214956.png"


@pytest.fixture
def sample_pdf_path():
    return "tests/nsu_transcript_ocr/681844277-Transcript.pdf"


@pytest.fixture
def sample_pdf2_path():
    return "tests/nsu_transcript_ocr/585057865-Riyadh.pdf"


class TestOCR:
    
    @pytest.mark.asyncio
    async def test_png_extracts_rows(self, sample_image_path):
        with open(sample_image_path, 'rb') as f:
            img_bytes = f.read()
        
        result = await process_ocr(img_bytes)
        
        assert result.extracted_row_count > 0
        assert result.confidence_avg > 0.5
        assert "course_code" in result.csv_text
    
    @pytest.mark.asyncio
    async def test_pdf_extracts_rows(self, sample_pdf_path):
        with open(sample_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        img_bytes = await process_pdf_first_page(pdf_bytes)
        result = await process_ocr(img_bytes)
        
        assert result.extracted_row_count > 0
        assert result.confidence_avg > 0.5
    
    @pytest.mark.asyncio
    async def test_pdf_conversion(self, sample_pdf_path):
        with open(sample_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        img_bytes = await process_pdf_first_page(pdf_bytes)
        
        assert img_bytes is not None
        assert len(img_bytes) > 0
    
    @pytest.mark.asyncio
    async def test_confidence_warning(self, sample_pdf_path):
        with open(sample_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        img_bytes = await process_pdf_first_page(pdf_bytes)
        result = await process_ocr(img_bytes)
        
        # Should have some warnings about low confidence
        assert len(result.warnings) > 0
    
    @pytest.mark.asyncio
    async def test_csv_format(self, sample_image_path):
        with open(sample_image_path, 'rb') as f:
            img_bytes = f.read()
        
        result = await process_ocr(img_bytes)
        
        lines = result.csv_text.strip().split('\n')
        assert len(lines) > 1
        assert lines[0] == "course_code,course_name,credits,grade,semester"


class TestOCRWithAudit:
    
    @pytest.mark.asyncio
    async def test_ocr_feeds_audit(self, sample_pdf_path):
        from backend.services.audit_service import run_audit
        
        with open(sample_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        img_bytes = await process_pdf_first_page(pdf_bytes)
        ocr_result = await process_ocr(img_bytes)
        
        if ocr_result.extracted_row_count > 0:
            audit_result = await run_audit(
                csv_text=ocr_result.csv_text,
                program="BSEEE",
                audit_level=1,
                waivers=[],
                knowledge_file=""
            )
            
            assert "total_credits" in audit_result
            assert audit_result["total_credits"] > 0
