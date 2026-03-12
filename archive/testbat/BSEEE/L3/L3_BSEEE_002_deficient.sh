#!/bin/bash
# Test: L3_BSEEE_002_deficient
# Level: 3 - Audit Engine
echo "NONE" | python3 "../../../src/level3_audit_engine.py" "../../../tests/BSEEE/L3/L3_BSEEE_002_deficient.csv" "../../../program_knowledge/program_knowledge_BSEEE.md"
