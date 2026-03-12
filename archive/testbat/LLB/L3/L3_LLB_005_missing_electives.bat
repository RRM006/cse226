@echo off
REM Test: L3_LLB_005_missing_electives
REM Level: 3 - Audit Engine
echo NONE | python "../../../src/level3_audit_engine.py" "../../../tests/LLB/L3/L3_LLB_005_missing_electives.csv" "../../../program_knowledge/program_knowledge_LLB.md"
pause
