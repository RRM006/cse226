@echo off
REM Test: L3_BSCSE_004_prereq_violation
REM Level: 3 - Audit Engine
echo NONE | python "../../../src/level3_audit_engine.py" "../../../tests/BSCSE/L3/L3_BSCSE_004_prereq_violation.csv" "../../../program_knowledge/program_knowledge_BSCSE.md"
pause
