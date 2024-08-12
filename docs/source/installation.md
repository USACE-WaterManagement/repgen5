# Installation Guide

This page provides step-by-step instructions to install `repgen5`.

## System Requirements

- **Python 3.8+**: Ensure you have Python installed.
- **Pip**: The Python package manager.

## Installation Steps

1. **Install the Repgen5 Package from PyPI**:

    ```bash
    pip install cwms-repgen
    ```


2. **Test Repgen Installation**:

    ```bash
    repgen -h
    ```
    This should show the help message for Repgen. 

    If you see an error, please see the Troubleshooting section below.

## Updating Repgen

  - Update Repgen5 with the following command:  
    _(Install command with **-U** flag to upgrade Repgen5 to the latest version)_
    ```bash
    pip install -U cwms-repgen
    ```
  - If you would like to target a specific version, use the following command:
    ```bash
    pip install -U cwms-repgen==5.1.6
    ``` 



## Troubleshooting Installation

- **Common Issue #1**: Repgen5 / Repgen is not found.
  - ```'repgen5' is not recognized as an internal or external command, operable program or batch file.```
    - **Windows Solution**:  
      - Ensure if you are installing to your global python installation, you have added the path to the python installation to your PATH environment variable. 
      - Search in the start menu for "Edit user environment variables" and add the path to the python installation to the PATH variable. Normally the "Scripts" folder is added to the PATH variable.
  - ```-bash: repgen5: command not found```
    - **Linux/Solaris Solution**: In your terminal, run the following command to add the path to the python installation to the PATH variable.
      - `vim ~/.bashrc`
      - Add the following line to the end of the file:
        - ```export PATH=$PATH:/path/to/python/installation```
      - Exit vim and save with `:wq`
      - Run the following command to reload the bashrc file:
        - ```source ~/.bashrc```

- **Common Issue #2**: Permission errors.
    - **Solution**: Make sure any shell or run files have execute permissions with `chmod +x file`.

<!-- - **Common Issue #3**: Custom user made module are not found.
  - ```ImportError: No module named 'customModule'```
    - **Solution**: Ensure the custom module is in the same directory as the `.frm` file you made. Then import with
    - ```from customModule import functionName``` -->