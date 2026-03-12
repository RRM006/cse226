#!/bin/bash

# NSU Audit Core - Test Runner Script
# This script runs all tests for BSCSE, BSEEE, and LLB programs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_DIR/src"
TESTS_DIR="$PROJECT_DIR/tests"
PROG_KNOWLEDGE_DIR="$PROJECT_DIR/program_knowledge"

echo "=============================================="
echo "NSU AUDIT CORE - TEST RUNNER"
echo "=============================================="
echo ""

run_level1() {
    echo ">>> Running Level 1 Tests (Credit Tally)"
    echo "------------------------------------------"
    
    for test_file in "$TESTS_DIR"/BSCSE/L1/*.csv; do
        if [ -f "$test_file" ]; then
            echo "Testing: $(basename "$test_file")"
            python3 "$SRC_DIR/level1_credit_tally.py" "$test_file"
            echo ""
        fi
    done
    
    for test_file in "$TESTS_DIR"/BSEEE/L1/*.csv; do
        if [ -f "$test_file" ]; then
            echo "Testing: $(basename "$test_file")"
            python3 "$SRC_DIR/level1_credit_tally.py" "$test_file"
            echo ""
        fi
    done
    
    for test_file in "$TESTS_DIR"/LLB/L1/*.csv; do
        if [ -f "$test_file" ]; then
            echo "Testing: $(basename "$test_file")"
            python3 "$SRC_DIR/level1_credit_tally.py" "$test_file"
            echo ""
        fi
    done
}

run_level2() {
    echo ">>> Running Level 2 Tests (CGPA Calculator)"
    echo "------------------------------------------"
    
    for test_file in "$TESTS_DIR"/BSCSE/L2/*.csv; do
        if [ -f "$test_file" ]; then
            echo "Testing: $(basename "$test_file")"
            echo "NONE" | python3 "$SRC_DIR/level2_cgpa_calculator.py" "$test_file"
            echo ""
        fi
    done
    
    for test_file in "$TESTS_DIR"/BSEEE/L2/*.csv; do
        if [ -f "$test_file" ]; then
            echo "Testing: $(basename "$test_file")"
            echo "NONE" | python3 "$SRC_DIR/level2_cgpa_calculator.py" "$test_file"
            echo ""
        fi
    done
    
    for test_file in "$TESTS_DIR"/LLB/L2/*.csv; do
        if [ -f "$test_file" ]; then
            echo "Testing: $(basename "$test_file")"
            echo "NONE" | python3 "$SRC_DIR/level2_cgpa_calculator.py" "$test_file"
            echo ""
        fi
    done
}

run_level3() {
    echo ">>> Running Level 3 Tests (Audit Engine)"
    echo "------------------------------------------"
    
    for test_file in "$TESTS_DIR"/BSCSE/L3/*.csv; do
        if [ -f "$test_file" ]; then
            echo "Testing: $(basename "$test_file")"
            echo "NONE" | python3 "$SRC_DIR/level3_audit_engine.py" "$test_file" "$PROG_KNOWLEDGE_DIR/program_knowledge_BSCSE.md"
            echo ""
        fi
    done
    
    for test_file in "$TESTS_DIR"/BSEEE/L3/*.csv; do
        if [ -f "$test_file" ]; then
            echo "Testing: $(basename "$test_file")"
            echo "NONE" | python3 "$SRC_DIR/level3_audit_engine.py" "$test_file" "$PROG_KNOWLEDGE_DIR/program_knowledge_BSEEE.md"
            echo ""
        fi
    done
    
    for test_file in "$TESTS_DIR"/LLB/L3/*.csv; do
        if [ -f "$test_file" ]; then
            echo "Testing: $(basename "$test_file")"
            echo "NONE" | python3 "$SRC_DIR/level3_audit_engine.py" "$test_file" "$PROG_KNOWLEDGE_DIR/program_knowledge_LLB.md"
            echo ""
        fi
    done
}

run_transfer_tests() {
    echo ">>> Running Department Transfer Tests"
    echo "------------------------------------------"
    
    for test_file in "$TESTS_DIR"/transfers/*.csv; do
        if [ -f "$test_file" ]; then
            echo "Testing: $(basename "$test_file")"
            echo "NONE" | python3 "$SRC_DIR/level3_audit_engine.py" "$test_file" "$PROG_KNOWLEDGE_DIR/program_knowledge_LLB.md"
            echo ""
        fi
    done
}

case "$1" in
    l1)
        run_level1
        ;;
    l2)
        run_level2
        ;;
    l3)
        run_level3
        ;;
    transfer)
        run_transfer_tests
        ;;
    all)
        run_level1
        run_level2
        run_level3
        run_transfer_tests
        ;;
    *)
        echo "Usage: $0 {l1|l2|l3|transfer|all}"
        echo ""
        echo "  l1       - Run Level 1 (Credit Tally) tests"
        echo "  l2       - Run Level 2 (CGPA Calculator) tests"
        echo "  l3       - Run Level 3 (Audit Engine) tests"
        echo "  transfer - Run department transfer tests"
        echo "  all      - Run all tests"
        exit 1
        ;;
esac

echo "=============================================="
echo "TEST RUN COMPLETE"
echo "=============================================="
