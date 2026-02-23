@echo off
REM Test: L3_BSEEE_005_missing_capstone
REM Level: 3 - Audit Engine
echo NONE | python "../../../src/level3_audit_engine.py" "../../../tests/BSEEE/L3/L3_BSEEE_005_missing_capstone.csv" "../../../program_knowledge/program_knowledge_BSEEE.md"
pause
