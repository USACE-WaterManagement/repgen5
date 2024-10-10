@echo off

@REM Get the first argument, which is the report name
set reportname=%1
echo %reportname%

@REM Check if no input is provided
if "%1"=="" (
    echo No input provided. Listing files in the 'tests/swt/testfiles' directory:
    
    @REM Loop through files and list those without extension
    for %%f in (tests\swt\testfiles\*.*) do (
        echo run.bat %%~nf
    )
    exit /b 1
)


@REM If a file extension is present, remove it
if "%reportname:~-4%" == ".frm" set reportname=%reportname:~0,-4%
if "%reportname:~-4%" == ".out" set reportname=%reportname:~0,-4%


python.exe . ^
    -a https://cwms-data.usace.army.mil/cwms-data ^
    -i tests/swt/testfiles/%reportname%.frm ^
    -O SWT ^
	-o tests/swt/output/%reportname%.out ^
    %*