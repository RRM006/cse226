@echo off
REM Test: L3_BSCSE_001_complete
REM Level: 3 - Audit Engine
echo NONE | python "../../../src/level3_audit_engine.py" "../../../tests/BSCSE/L3/L3_BSCSE_001_complete.csv" "../../../program_knowledge/program_knowledge_BSCSE.md"
pause
