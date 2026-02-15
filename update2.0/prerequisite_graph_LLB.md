# Prerequisite Graph - LL.B Honors Program
## North South University School of Law

---

## Prerequisite Relationships

### Foundation Courses (Year 1)

```
LLB101: Introduction to Legal System
  ├──→ LLB103: Law of Contract
  └──→ LLB104: Law of Torts

LLB102: Constitutional Laws of Bangladesh
  ├──→ LLB202: Law of Crime
  └──→ LLB206: Administrative Law
```

### Criminal Law Stream

```
LLB202: Law of Crime
  ├──→ LLB302: Law of Criminal Procedure (Part 1)
  └──→ LLB303: Law of Criminal Procedure (Part 2)
```

### Civil Law Stream

```
LLB103: Law of Contract
  ├──→ LLB304: Law of Civil Procedure (Part 1)
  └──→ LLB305: Law of Civil Procedure (Part 2)
```

### Research & Dissertation

```
LLB404: Legal Research
  └──→ LLB407: Law Dissertation [CRITICAL PREREQUISITE]
```

---

## Complete Prerequisite Table

| Course | Prerequisites | Dependents |
|--------|---------------|------------|
| LLB101 | None | LLB103, LLB104 |
| LLB102 | None | LLB202, LLB206 |
| LLB103 | LLB101 | LLB304, LLB305 |
| LLB104 | LLB101 | None |
| LLB201 | None | None |
| LLB202 | LLB102 | LLB302, LLB303 |
| LLB203 | None | None |
| LLB204 | None | None |
| LLB205 | None | None |
| LLB206 | LLB102 | None |
| LLB207 | None | None |
| LLB208 | None | None |
| LLB209 | None | None |
| LLB301 | None | None |
| LLB302 | LLB202 | None |
| LLB303 | LLB202 | None |
| LLB304 | LLB103 | None |
| LLB305 | LLB103 | None |
| LLB306 | None | None |
| LLB307 | None | None |
| LLB401 | None | None |
| LLB402 | None | None |
| LLB403 | None | None |
| LLB404 | None | LLB407 |
| LLB405 | None | None |
| LLB406 | None | None |
| **LLB407** | **LLB404** + **100 credits** | None |

---

## Prerequisite Chains

### Chain 1: Foundation → Contract → Civil Procedure
```
LLB101 → LLB103 → LLB304
                → LLB305
```

### Chain 2: Constitution → Crime → Criminal Procedure
```
LLB102 → LLB202 → LLB302
                → LLB303
```

### Chain 3: Research → Dissertation
```
LLB404 → LLB407 (+ 100 credits requirement)
```

---

## Validation Rules

### Rule 1: Foundation Prerequisites
- **Requirement**: LLB101 must be completed before LLB103, LLB104
- **Validation**: Check if LLB101 is in completed courses
- **Action**: Flag violation if dependent taken without prerequisite

### Rule 2: Constitutional Prerequisites
- **Requirement**: LLB102 must be completed before LLB202, LLB206
- **Validation**: Check if LLB102 is in completed courses
- **Action**: Flag violation if dependent taken without prerequisite

### Rule 3: Criminal Law Prerequisites
- **Requirement**: LLB202 must be completed before LLB302, LLB303
- **Validation**: Check if LLB202 is in completed courses
- **Action**: Flag violation if dependent taken without prerequisite

### Rule 4: Civil Law Prerequisites
- **Requirement**: LLB103 must be completed before LLB304, LLB305
- **Validation**: Check if LLB103 is in completed courses
- **Action**: Flag violation if dependent taken without prerequisite

### Rule 5: Dissertation Prerequisites (CRITICAL)
- **Requirement 1**: LLB404 must be completed before LLB407
- **Requirement 2**: Must have 100+ credits completed
- **Validation**: Check both conditions
- **Action**: **BLOCK** dissertation if prerequisites not met (not just flag)

---

## Prerequisite Violation Examples

### Example 1: Taking LLB103 without LLB101
```
Transcript:
- LLB103: Law of Contract (Spring 2023) ← VIOLATION
- LLB101: Not completed

Issue: LLB103 requires LLB101
Action: Flag "Prerequisite Violation: LLB103 requires LLB101"
```

### Example 2: Taking LLB302 without LLB202
```
Transcript:
- LLB302: Criminal Procedure Part 1 (Fall 2023) ← VIOLATION
- LLB202: Not completed

Issue: LLB302 requires LLB202
Action: Flag "Prerequisite Violation: LLB302 requires LLB202"
```

### Example 3: Taking LLB407 without LLB404
```
Transcript:
- LLB407: Law Dissertation (Spring 2025) ← CRITICAL VIOLATION
- LLB404: Not completed
- Total Credits: 110

Issue: LLB407 requires LLB404
Action: **BLOCK** "CRITICAL: Cannot take LLB407 without completing LLB404"
```

### Example 4: Taking LLB407 with < 100 Credits
```
Transcript:
- LLB407: Law Dissertation (Spring 2024) ← CRITICAL VIOLATION
- LLB404: Completed (Fall 2023)
- Total Credits: 85

Issue: LLB407 requires 100+ credits
Action: **BLOCK** "CRITICAL: Cannot take LLB407 with only 85 credits (need 100+)"
```

---

## Prerequisite Checking Logic

### Algorithm:

```python
def check_prerequisites(transcript):
    prerequisites = {
        'LLB103': ['LLB101'],
        'LLB104': ['LLB101'],
        'LLB202': ['LLB102'],
        'LLB206': ['LLB102'],
        'LLB302': ['LLB202'],
        'LLB303': ['LLB202'],
        'LLB304': ['LLB103'],
        'LLB305': ['LLB103'],
        'LLB407': ['LLB404']  # + 100 credits check
    }
    
    violations = []
    completed_courses = get_completed_courses(transcript)
    
    for course in transcript:
        if course.code in prerequisites:
            required = prerequisites[course.code]
            for prereq in required:
                if prereq not in completed_courses:
                    violations.append({
                        'course': course.code,
                        'prerequisite': prereq,
                        'severity': 'CRITICAL' if course.code == 'LLB407' else 'WARNING'
                    })
        
        # Special check for LLB407
        if course.code == 'LLB407':
            total_credits = calculate_credits(completed_courses)
            if total_credits < 100:
                violations.append({
                    'course': 'LLB407',
                    'issue': f'Requires 100+ credits, have {total_credits}',
                    'severity': 'CRITICAL'
                })
    
    return violations
```

---

## Recommended Course Sequence

### Following Prerequisite Chain:

**Year 1:**
- Semester 1: LLB101 (Foundation)
- Semester 2: LLB102 (Foundation)

**Year 2:**
- Semester 1: LLB103, LLB104 (requires LLB101)
- Semester 1: LLB202 (requires LLB102)
- Semester 2: LLB206 (requires LLB102)

**Year 3:**
- Semester 1: LLB302, LLB304 (requires LLB202, LLB103)
- Semester 2: LLB303, LLB305 (requires LLB202, LLB103)

**Year 4:**
- Semester 1: LLB404 (Legal Research)
- Semester 2: LLB407 (requires LLB404 + 100 credits)

---

## Critical vs. Warning Violations

### CRITICAL (Block Graduation):
- **LLB407 without LLB404**: Cannot complete dissertation
- **LLB407 with < 100 credits**: Not eligible for dissertation

### WARNING (Flag but Allow):
- **LLB103 without LLB101**: Administrative oversight
- **LLB302 without LLB202**: Sequence issue
- **LLB304 without LLB103**: Sequence issue

**Rationale**: 
- Most prerequisite violations are administrative issues
- Dissertation prerequisites are academic requirements
- Critical violations block graduation
- Warnings are flagged in audit report

---

## Prerequisite Waiver Policy

### Waivers Not Applicable:
- Prerequisite relationships are academic requirements
- Cannot be waived like course requirements (ENG102, MAT116)
- Students must complete prerequisites

### Exception:
- Transfer credits may satisfy prerequisites
- Department chair approval required
- Must be documented in transcript

---

**End of Document**
