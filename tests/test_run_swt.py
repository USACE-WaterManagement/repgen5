import os
import sys
import pytest
import subprocess
import platform

sys.path.append("../")

INPUT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "swt", "testfiles")
)
EXPECT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "swt", "expect")
)
ACTUAL_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "swt", "actual")
)
LOG_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "swt", "output")
)
SCRIPT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "swt", "scripts")
)

os.makedirs(ACTUAL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


@pytest.mark.parametrize(
    "reportname",
    [
        ("test.frm"),
    ],
)
def test_repgen(capsys, reportname: str):
    actualname = os.path.join(
        ACTUAL_DIR, reportname 
    )  # Assuming output is .txt
    expectname = os.path.join(EXPECT_DIR, reportname )
    outputname = os.path.join(LOG_DIR, reportname + ".out.log")
    errname = os.path.join(LOG_DIR, reportname + ".err.log")

    # Determine the operating system and choose the script accordingly
    if platform.system() == "Windows":
        script = os.path.join(SCRIPT_DIR, "run.bat")
        cmd = ["cmd.exe", "/c", script]
    else:
        script = os.path.join(SCRIPT_DIR, "run.sh")
        cmd = [script]

    # Run the command and capture the output
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Write captured output to files
    if result.stdout:
        with open(outputname, "wt") as output_fd:
            output_fd.write(result.stdout)

    if result.stderr:
        with open(errname, "wt") as output_fd:
            output_fd.write(result.stderr)

    # Read expected and actual output
    with open(expectname, "+rt") as expect_fd:
        expect_content = expect_fd.readlines()

    with open(actualname, "+rt") as actual_fd:
        actual_content = actual_fd.readlines()

    # Assert that the expected and actual output match
    assert len(actual_content) == len(expect_content)

    for x in range(len(expect_content)):
        assert expect_content[x] == actual_content[x]
