import os
import sys
import pytest
import subprocess
import platform

sys.path.append("../")

INPUT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "various", "tsid", "testfiles")
)
EXPECT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "various", "tsid", "expect")
)
ACTUAL_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "various", "tsid", "actual")
)
LOG_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "various", "tsid", "output")
)
SCRIPT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "various", "tsid", "scripts")
)

os.makedirs(ACTUAL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


@pytest.mark.parametrize(
    "reportname, office",
    [
        ("swt.keystone", "SWT"),
        ("spk.flow_out", "SPK"),
    ]
)
def test_repgen(capsys, reportname: str, office: str):
    print(f"office: {office} reportname: {reportname}")
    actualname = os.path.join(
        ACTUAL_DIR, reportname + ".txt"
    )  # Assuming output is .txt
    expectname = os.path.join(EXPECT_DIR, reportname + ".txt")
    outputname = os.path.join(LOG_DIR, reportname + ".out.log")
    errname = os.path.join(LOG_DIR, reportname + ".err.log")

    # Determine the operating system and choose the script accordingly
    _rg_args = ["python", ".", "-a", "https://cwms-data.usace.army.mil/cwms-data", "-i", f"./tests/various/tsid/testfiles/{reportname}.frm", "-O", office.upper(), "-o", f"./tests/various/tsid/actual/{reportname}.txt"]

    if platform.system() == "Windows":
        script = os.path.join(SCRIPT_DIR, "run.bat")
        cmd = ["cmd.exe", "/c"] + _rg_args
    else:
        script = os.path.join(SCRIPT_DIR, "run.sh")
        cmd = [script] + _rg_args

    output = None
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout
        error_output = result.stderr
    except subprocess.TimeoutExpired as e:
        error_output = str(e)
    except subprocess.CalledProcessError as e:
        error_output = e.stderr
    except Exception as e:
        error_output = str(e)
        
    # Write captured output to files
    if output:
        with open(outputname, "wt") as output_fd:
            output_fd.write(output)

    if error_output:
        with open(errname, "wt") as output_fd:
            output_fd.write(error_output)

    # Read expected and actual output
    with open(expectname, "+rt") as expect_fd:
        expect_content = expect_fd.readlines()

    with open(actualname, "+rt") as actual_fd:
        actual_content = actual_fd.readlines()

    # Assert that the expected and actual output match
    assert len(actual_content) == len(expect_content)

    for x in range(len(expect_content)):
        assert expect_content[x] == actual_content[x]