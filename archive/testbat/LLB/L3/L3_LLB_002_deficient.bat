@echo off
REM Test: L3_LLB_002_deficient
REM Level: 3 - Audit Engine
echo NONE | python "../../../src/level3_audit_engine.py" "../../../tests/LLB/L3/L3_LLB_002_deficient.csv" "../../../program_knowledge/program_knowledge_LLB.md"
pause
