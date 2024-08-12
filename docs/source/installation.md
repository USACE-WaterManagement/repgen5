# Installation Guide

This page provides step-by-step instructions to install `repgen5`.

## System Requirements

- **Python 3.8+**: Ensure you have Python installed.
- **Pip**: The Python package manager.

## Installation Steps

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/usace-watermanagement/repgen5.git
    ```

2. **Navigate to the Directory**:

    ```bash
    cd repgen5
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Initial Setup**:

    ```bash
    python setup.py install
    ```

## Troubleshooting Installation

- **Common Issue #1**: Missing dependencies.
    - **Solution**: Ensure all dependencies in `requirements.txt` are installed.

- **Common Issue #2**: Permission errors.
    - **Solution**: Make sure any shell or run files have execute permissions with `chmod +x file`.

