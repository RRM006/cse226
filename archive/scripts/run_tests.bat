@echo off
REM NSU Audit Core - Test Runner Batch File
REM This batch file runs all tests for BSCSE, BSEEE, and LLB programs

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..
set SRC_DIR=%PROJECT_DIR%\src
set TESTS_DIR=%PROJECT_DIR%\tests
set PROG_KNOWLEDGE_DIR=%PROJECT_DIR%\program_knowledge

echo ==============================================
echo NSU AUDIT CORE - TEST RUNNER
echo ==============================================
echo.

if "%1"=="" goto usage
if "%1"=="l1" goto run_l1
if "%1"=="l2" goto run_l2
if "%1"=="l3" goto run_l3
if "%1"=="transfer" goto run_transfer
if "%1"=="all" goto run_all
goto usage

:run_l1
echo ^>^>^> Running Level 1 Tests (Credit Tally)
echo ------------------------------------------
for %%f in (%TESTS_DIR%\BSCSE\L1\*.csv) do (
    echo Testing: %%~nxf
    python "%SRC_DIR%\level1_credit_tally.py" "%%f"
    echo.
)
for %%f in (%TESTS_DIR%\BSEEE\L1\*.csv) do (
    echo Testing: %%~nxf
    python "%SRC_DIR%\level1_credit_tally.py" "%%f"
    echo.
)
for %%f in (%TESTS_DIR%\LLB\L1\*.csv) do (
    echo Testing: %%~nxf
    python "%SRC_DIR%\level1_credit_tally.py" "%%f"
    echo.
)
goto done

:run_l2
echo ^>^>^> Running Level 2 Tests (CGPA Calculator)
echo ------------------------------------------
for %%f in (%TESTS_DIR%\BSCSE\L2\*.csv) do (
    echo Testing: %%~nxf
    echo NONE | python "%SRC_DIR%\level2_cgpa_calculator.py" "%%f"
    echo.
)
for %%f in (%TESTS_DIR%\BSEEE\L2\*.csv) do (
    echo Testing: %%~nxf
    echo NONE | python "%SRC_DIR%\level2_cgpa_calculator.py" "%%f"
    echo.
)
for %%f in (%TESTS_DIR%\LLB\L2\*.csv) do (
    echo Testing: %%~nxf
    echo NONE | python "%SRC_DIR%\level2_cgpa_calculator.py" "%%f"
    echo.
)
goto done

:run_l3
echo ^>^>^> Running Level 3 Tests (Audit Engine)
echo ------------------------------------------
for %%f in (%TESTS_DIR%\BSCSE\L3\*.csv) do (
    echo Testing: %%~nxf
    echo NONE | python "%SRC_DIR%\level3_audit_engine.py" "%%f" "%PROG_KNOWLEDGE_DIR%\program_knowledge_BSCSE.md"
    echo.
)
for %%f in (%TESTS_DIR%\BSEEE\L3\*.csv) do (
    echo Testing: %%~nxf
    echo NONE | python "%SRC_DIR%\level3_audit_engine.py" "%%f" "%PROG_KNOWLEDGE_DIR%\program_knowledge_BSEEE.md"
    echo.
)
for %%f in (%TESTS_DIR%\LLB\L3\*.csv) do (
    echo Testing: %%~nxf
    echo NONE | python "%SRC_DIR%\level3_audit_engine.py" "%%f" "%PROG_KNOWLEDGE_DIR%\program_knowledge_LLB.md"
    echo.
)
goto done

:run_transfer
echo ^>^>^> Running Department Transfer Tests
echo ------------------------------------------
for %%f in (%TESTS_DIR%\transfers\*.csv) do (
    echo Testing: %%~nxf
    echo NONE | python "%SRC_DIR%\level3_audit_engine.py" "%%f" "%PROG_KNOWLEDGE_DIR%\program_knowledge_LLB.md"
    echo.
)
goto done

:run_all
call :run_l1
call :run_l2
call :run_l3
call :run_transfer
goto done

:usage
echo Usage: run_tests.bat {l1^l|l2^l|l3^l|transfer^l|all}
echo.
echo   l1       - Run Level 1 (Credit Tally) tests
echo   l2       - Run Level 2 (CGPA Calculator) tests
echo   l3       - Run Level 3 (Audit Engine) tests
echo   transfer - Run department transfer tests
echo   all      - Run all tests
exit /b 1

:done
echo ==============================================
echo TEST RUN COMPLETE
echo ==============================================
endlocal
