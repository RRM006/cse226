# NSU Audit Core — Assumptions Log

## Assumption #1 — Program Detection

**Context:** The transcript CSV does not include a "program" field.
**Assumption:** The program is detected heuristically from course codes (LLB → LL.B, EEE major → BSEEE, CSE major → BSCSE). The scripts will also accept a `--program` flag or detect from metadata row.
**Reason:** The spec says the CSV columns are `course_code,course_name,credits,grade,semester` with no program field. We need a way to know which program to audit against.
**Impact:** If detection is wrong, the entire category breakdown would be incorrect. The `--program` CLI flag provides a reliable fallback.
**Source:** OpenCode assumption

## Assumption #2 — Student ID

**Context:** The spec output shows `Student: [Student ID]` but the CSV has no student ID column.
**Assumption:** The transcript CSV will include a metadata comment line `# Student: <ID>` and `# Program: <Name>` at the top, before the header row. If absent, defaults are used.
**Reason:** There's no other way to get this info from the CSV.
**Impact:** If the user provides a CSV without these lines, a default placeholder will appear.
**Source:** OpenCode assumption

## Assumption #3 — C+ Grade

**Context:** The NSU grading scale in the spec lists A, A-, B+, B, B-, C, C-, D+, D but does NOT list C+.
**Assumption:** C+ exists with grade point 2.3 (standard NSU scale). The spec's grade table is incomplete.
**Reason:** C+ is a standard grade at NSU between B- (2.7) and C (2.0). The prompt mentions "A through D" as valid which would include C+.
**Impact:** If C+ doesn't exist, any transcript entry with C+ would be treated as invalid.
**Source:** OpenCode assumption

## Assumption #4 — F Grade in CGPA

**Context:** The spec says "F, I, W, X are excluded from CGPA calculation entirely" but also says "F grade — 0 points, excluded from earned credits but shown in attempted."
**Assumption:** F grades are excluded from CGPA entirely (same as I, W, X). They count toward "attempted" in Level 1 reporting but do NOT contribute grade points or credits to the CGPA formula.
**Reason:** The spec's CGPA section is explicit: "Only grades A through D are counted in CGPA."
**Impact:** Including F in CGPA would lower the computed CGPA significantly.
**Source:** OpenCode assumption

## Assumption #5 — Semester Format

**Context:** The CSV has a `semester` column but no format is specified.
**Assumption:** Semester values are strings like "Fall2023", "Spring2024", "Summer2024". For prerequisite checking, we sort semesters chronologically.
**Reason:** Need to compare semesters for prerequisite validation in Level 3.
**Impact:** If semester format differs, prerequisite checking may fail.
**Source:** OpenCode assumption

## Assumption #6 — Category Mapping Embedded

**Context:** Level 1 needs to show credits by category but only Level 3 takes a program knowledge file as input.
**Assumption:** Levels 1 and 2 embed the course-to-category mappings internally (from the program knowledge files), since they only take the transcript CSV as input.
**Reason:** The CLI usage for L1 and L2 only takes `<transcript.csv>`, not a knowledge file.
**Impact:** If program requirements change, L1/L2 code must be updated.
**Source:** OpenCode assumption
