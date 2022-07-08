import pytest
import sys
import os
sys.path.append("../")

from converter import convert_report;

INPUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "testfiles"))
EXPECT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "expect"))
ACTUAL_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "actual"))
LOG_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "output"))

os.makedirs(ACTUAL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

@pytest.mark.parametrize("value,expect", [
	("ZD AAA YYYY @ ZZZT", "%d %b %Y @ %K%M"),
	("ZZZTbbZDAAAYYYY", "%K%M  %d%b%Y"),
	("BBAA", "  AA"),
	("ZDAAAZZZYB@BZZ:ZT", "%d%b%Y @ %K:%M"),
	("NNNNNZ.Z", "%8.1f"),
	("NNN,NNZ ac-ft", "%7,.0f ac-ft"),
	("ZM/ZD/ZY", "%m/%d/%y"),
])
def test_convert_picture_format(value, expect):
	result = convert_report.convert_picture_format(value)
	assert result == expect

def test_value_builder_unquoted():
	value = convert_report.Value()
	value["DBLOC"] = "Markers-Placeholder"
	value["DBPAR"] = "Count"
	value["DBTYP"] = "Inst"
	value["DBINT"] = "~1Day"
	value["DBDUR"] = "0"
	value["DBVER"] = "ALL"
	value["DBUNITS"] = "units"

	expected = """Value(
	DBLOC=Markers-Placeholder,
	DBPAR=Count,
	DBTYP=Inst,
	DBINT=~1Day,
	DBDUR=0,
	DBVER=ALL,
	DBUNITS=units,
)
"""
	assert str(value) == expected

def test_value_builder_quoted():
	value = convert_report.Value()
	value["DBLOC"] = '"Markers-Placeholder"'
	value["DBPAR"] = '"Count"'
	value["DBTYP"] = '"Inst"'
	value["DBINT"] = '"~1Day"'
	value["DBDUR"] = "0"
	value["DBVER"] = '"ALL"'
	value["DBUNITS"] = '"units"'

	expected = """Value(
	DBLOC="Markers-Placeholder",
	DBPAR="Count",
	DBTYP="Inst",
	DBINT="~1Day",
	DBDUR=0,
	DBVER="ALL",
	DBUNITS="units",
)
"""
	assert str(value) == expected
	

@pytest.mark.parametrize("reportname,hack_flags", [
	("i-ucb", 0),
	("i-resstat", 0),
	("i-blb", 0),
	("i-base.battery", 6),
])
def test_converter_file(capsys, reportname: str, hack_flags: int):

	inputname = os.path.join(INPUT_DIR, reportname)
	actualname = os.path.join(ACTUAL_DIR, reportname)
	expectname = os.path.join(EXPECT_DIR, reportname)
	outputname = os.path.join(LOG_DIR, reportname + ".out.log")
	errname = os.path.join(LOG_DIR, reportname + ".err.log")

	# Apply the DATE_HACK flags
	glbls = globals()
	glbls["convert_report"].DATE_HACK = hack_flags
	
	exec(f'convert_report.main(r"{inputname}", r"{actualname}")', glbls, None)

	captured = capsys.readouterr()

	if captured.out:
		with open(outputname, "wt") as output_fd:
			output_fd.write(captured.out)

	if captured.err:
		with open(errname, "wt") as output_fd:
			output_fd.write(captured.err)

	expect_content = None
	actual_content = None

	with open(expectname, "+rt") as expect_fd:
		expect_content = expect_fd.readlines()

	with open(actualname, "+rt") as actual_fd:
		actual_content = actual_fd.readlines()

	assert len(actual_content) == len(expect_content)

	for x in range(len(expect_content)):
		assert expect_content[x] == actual_content[x]
