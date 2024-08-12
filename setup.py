from setuptools import setup, find_packages
from repgen.__main__ import version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cwms-repgen",  
    version=version, 
    license="MIT",
    author="USACE-HEC", 
    description='''This is a partial copy of HEC's (Hydrologic Engineering Center) repgen program.
The program creates fixed form text reports from a time series database, and textfiles.''',
    long_description=long_description,
    long_description_content_type="text/markdown", 
    url="https://github.com/USACE-WaterManagement/repgen5", 
    packages=find_packages(exclude=["tests", "docs"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8', 
    install_requires=[
        "sphinx>=3.0.0",
        "myst-parser", 
        "pytz>=2022.1",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "sphinx",
            "sphinx_rtd_theme",
            "myst-parser",
            "twine",
            "wheel"
        ],
    },
    entry_points={
        'console_scripts': [
            'repgen5=repgen.__main__:main',
            'repgen=repgen.__main__:main',
        ],
    },
)