@echo off
REM Test: TRANSFER_EEE_TO_LLB_001
REM Level: 3 - Audit Engine
echo NONE | python "../../src/level3_audit_engine.py" "../../tests/transfers/TRANSFER_EEE_TO_LLB_001.csv" "../../program_knowledge/program_knowledge_LLB.md"
pause
