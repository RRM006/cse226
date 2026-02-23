#!/bin/bash
# Test: L3_LLB_005_missing_electives
# Level: 3 - Audit Engine
echo "NONE" | python3 "../../../src/level3_audit_engine.py" "../../../tests/LLB/L3/L3_LLB_005_missing_electives.csv" "../../../program_knowledge/program_knowledge_LLB.md"
