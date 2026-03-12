#!/bin/bash
# Test: TRANSFER_LLB_TO_BSCSE_001
# Level: 3 - Audit Engine
echo "NONE" | python3 "../../src/level3_audit_engine.py" "../../tests/transfers/TRANSFER_LLB_TO_BSCSE_001.csv" "../../program_knowledge/program_knowledge_BSCSE.md"
