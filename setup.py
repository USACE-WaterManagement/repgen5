from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Repgen5",  
    version="5.1.0", 
    author="USACE-HEC", 
    description='''This is a partial copy of HEC's (Hydrologic Engineering Center) repgen program.
The program creates fixed form text reports from a time series database, and textfiles.''',
    long_description=long_description,
    long_description_content_type="text/markdown", 
    url="https://github.com/USACE-WaterManagement/repgen5", 
    packages=find_packages(where="repgen"),
    package_dir={"": "repgen"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8', 
    install_requires=[
        "sphinx>=3.0.0",
        "myst-parser", 
    ],
    extras_require={
        "dev": [
            "sphinx",
            "sphinx_rtd_theme",
            "myst-parser",
        ],
    },
    entry_points={
        "console_scripts": [
            "repgen5=repgen5:main",  
        ],
    },
)
