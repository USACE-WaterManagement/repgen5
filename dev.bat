@REM Sets up the repgen5 environment and loads the package in development mode
@REM This is useful for testing changes as a package without having to publish to pypi

python -m pip install -r requirements.txt
python -m pip install -e .