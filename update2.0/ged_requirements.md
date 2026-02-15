# General Education Development (GED) Requirements
## North South University

---

## Overview

GED courses are foundational general education courses required for all undergraduate programs. The structure varies by program:

- **Engineering Programs** (BSCSE, BSEEE): Fixed 34 credits
- **Law Program** (LL.B): 25 credits (Group 1 + Group 2)
- **Other Programs**: Varies by department

---

## LL.B Honors GED Structure

### Group 1 (16 Credits - All Required)

| Course | Name | Credits | Category |
|--------|------|---------|----------|
| ENG102 | Introduction to Composition | 3 | English |
| ENG103 | Intermediate Composition | 3 | English |
| BEN205 | Bangla Language | 3 | Language |
| HIS103 | Emergence of Bangladesh | 3 | Social Science |
| [Science] | Choose 1 Science Course | 4 | Science |

**Science Options (Choose 1):**
- PBH101: Public Health (4)
- CHE101: Chemistry I (4)
- PHY107: Physics I (4)
- BIO103: Biology (4)

**Validation Rules:**
1. All 5 courses required
2. Exactly 1 science course
3. Cannot skip any fixed courses
4. Total: 16 credits

---

### Group 2 (9 Credits - Choose Any 3)

| Course | Name | Credits | Category | Notes |
|--------|------|---------|----------|-------|
| ECO101 | Principles of Economics | 3 | Economics | Alternative |
| ECO104 | Principles of Macroeconomics | 3 | Economics | Alternative |
| POL101 | Introduction to Political Science | 3 | Political Science | Alternative |
| POL104 | Government and Politics in Bangladesh | 3 | Political Science | Alternative |
| ENG111 | Public Speaking | 3 | English | |
| PHI101 | Introduction to Philosophy | 3 | Philosophy | |
| ENV203 | Environmental Science | 3 | Environment | Alternative |
| GEO205 | Introduction to Geography | 3 | Geography | Alternative |
| BUS112 | Principles of Management | 3 | Business | |
| SOC101 | Introduction to Sociology | 3 | Sociology | Alternative |
| ANT101 | Introduction to Anthropology | 3 | Anthropology | Alternative |

**Alternative Course Rules:**
- ECO101 OR ECO104 (not both)
- POL101 OR POL104 (not both)
- ENV203 OR GEO205 (not both)
- SOC101 OR ANT101 (not both)

**Validation Rules:**
1. Exactly 3 courses required
2. Any combination allowed (respecting alternatives)
3. No duplicates
4. Total: 9 credits

---

## Engineering GED Structure (BSCSE, BSEEE)

### University Core (34 Credits - All Required)

**Languages (12 Credits):**
- ENG102: Introduction to Composition (3)
- ENG103: Intermediate Composition (3)
- ENG111: Public Speaking (3)
- BEN205: Bangla Language (3)

**Humanities (9 Credits):**
- PHI104: Introduction to Ethics (3)
- HIS102: Introduction to World Civilization (3)
- HIS103: Emergence of Bangladesh (3)

**Social Sciences (9 Credits):**
- ECO101 or ECO104: Economics (3)
- POL101 or POL104: Political Science/Governance (3)
- SOC101 or ANT101 or ENV203 or GEO205: Sociology/Anthropology/Environment/Geography (3)

**Sciences (4 Credits - Choose 1):**
- BIO103: Biology (4)
- PHY107: Physics I (4)
- CHE101: Chemistry I (4)

**Validation Rules:**
1. All courses required (some with alternatives)
2. Total: 34 credits

---

## GED Validation Logic

### For LL.B Program:

```python
def validate_llb_ged(transcript):
    # Group 1 Validation
    group1_required = ['ENG102', 'ENG103', 'BEN205', 'HIS103']
    science_options = ['PBH101', 'CHE101', 'PHY107', 'BIO103']
    
    group1_complete = all(course in transcript for course in group1_required)
    science_complete = any(course in transcript for course in science_options)
    
    if not group1_complete or not science_complete:
        return False, "GED Group 1 incomplete"
    
    # Group 2 Validation
    group2_options = [
        'ECO101', 'ECO104', 'POL101', 'POL104', 
        'ENG111', 'PHI101', 'ENV203', 'GEO205', 
        'BUS112', 'SOC101', 'ANT101'
    ]
    
    group2_taken = [c for c in transcript if c in group2_options]
    
    # Check alternatives (can't take both)
    alternatives = [
        ('ECO101', 'ECO104'),
        ('POL101', 'POL104'),
        ('ENV203', 'GEO205'),
        ('SOC101', 'ANT101')
    ]
    
    for alt1, alt2 in alternatives:
        if alt1 in group2_taken and alt2 in group2_taken:
            return False, f"Cannot take both {alt1} and {alt2}"
    
    if len(group2_taken) != 3:
        return False, f"GED Group 2: Need 3 courses, have {len(group2_taken)}"
    
    return True, "GED requirements met"
```

---

## Common GED Issues

### Issue 1: Missing Group 2 Selection
**Problem**: Student completed < 3 courses from Group 2  
**Solution**: Select additional courses from Group 2 options  
**Example**: Only took ECO101, POL101 → Need 1 more (e.g., PHI101)

### Issue 2: Alternative Course Conflict
**Problem**: Student took both ECO101 and ECO104  
**Solution**: Exclude one course (choose which to drop)  
**Example**: Keep ECO101, drop ECO104, select different Group 2 course

### Issue 3: Missing Science Course
**Problem**: Student didn't complete any science from Group 1  
**Solution**: Must complete one of: PBH101, CHE101, PHY107, BIO103  
**Example**: Take BIO103 in next semester

### Issue 4: Total Credit Mismatch
**Problem**: GED credits don't add up to 25 (Law)  
**Solution**: Verify all Group 1 and Group 2 courses  
**Example**: Missing BEN205 → Need to complete

---

## GED Completion Timeline

### Recommended for Law Students:

**Year 1:**
- Complete all GED Group 1 (16 credits)
- Complete all GED Group 2 (9 credits)
- Total: 25 credits by end of Year 1

**Rationale:**
- GED courses are foundational
- Required for advanced law courses
- Should be completed early in program

**Flexibility:**
- Can be spread across Year 1 semesters
- Semester 1: 3-4 GED courses
- Semester 2: Remaining GED courses

---

## GED vs. Core Distinction

### GED Courses:
- General education (broad knowledge)
- Required for all programs
- Foundation for specialized study
- Examples: ENG102, HIS103, BIO103

### Core Courses:
- Program-specific (Law, Engineering)
- Build on GED foundation
- Specialized knowledge
- Examples: LLB101, CSE115, EEE111

---

**End of Document**
