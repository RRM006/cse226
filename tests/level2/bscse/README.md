# Level 2 - BSCSE Test Files

## Description
These test files are for Level 2 (CGPA Calculator) testing with BSCSE program.

## Test Files

### test_bscse_standard.csv
- **Purpose**: Test basic CGPA calculation for BSCSE
- **Expected CGPA**: ~3.64
- **What it tests**: Weighted CGPA calculation with standard grades

### test_bscse_retakes.csv
- **Purpose**: Test retake handling - uses best grade
- **Expected CGPA**: Based on best grades
- **What it tests**: 
  - ENG103: D(1.0) -> A(4.0) uses A
  - MAT120: C(2.0) -> B(3.0) uses B
  - CSE115: F(0.0) -> A(4.0) uses A
