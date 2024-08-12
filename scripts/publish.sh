#!/bin/bash
# Commands to publish the package to pypi
# This is a one-time command, and should be run from the root of the project

rm -rf dist/
pip install -r requirements.txt
python setup.py sdist bdist_wheel
twine upload dist/*
