#!/bin/bash
# Test: L3_BSCSE_004_prereq_violation
# Level: 3 - Audit Engine
echo "NONE" | python3 "../../../src/level3_audit_engine.py" "../../../tests/BSCSE/L3/L3_BSCSE_004_prereq_violation.csv" "../../../program_knowledge/program_knowledge_BSCSE.md"
