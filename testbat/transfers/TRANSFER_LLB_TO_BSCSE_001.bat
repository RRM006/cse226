@echo off
REM Test: TRANSFER_LLB_TO_BSCSE_001
REM Level: 3 - Audit Engine
echo NONE | python "../../src/level3_audit_engine.py" "../../tests/transfers/TRANSFER_LLB_TO_BSCSE_001.csv" "../../program_knowledge/program_knowledge_LLB.md"
pause
