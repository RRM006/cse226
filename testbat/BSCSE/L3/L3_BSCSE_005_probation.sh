#!/bin/bash
# Test: L3_BSCSE_005_probation
# Level: 3 - Audit Engine
echo "NONE" | python3 "../../../src/level3_audit_engine.py" "../../../tests/BSCSE/L3/L3_BSCSE_005_probation.csv" "../../../program_knowledge/program_knowledge_BSCSE.md"
