# Installation

Ensure Python is installed on your system along with the required dependencies.


## Install Python

Here's how you can install Python on **Linux (Ubuntu)** and **Windows**.

### Installing Python on Linux (Ubuntu distribution)

Ubuntu usually comes with Python pre-installed. However, if you need to install a specific version of Python or update it, follow these steps:

1. Update the package list:
```bash
sudo apt update
```

2. Install Python:
You can install Python and pip (Python package manager) using `apt`. For example, to install Python 3.x, run:
```bash
sudo apt install python3 python3-pip python3-tk
```

3. Verify the installation:
Check the installed Python and pip version:
```bash
python3 --version && pip3 --version
```

### Installing Python on Windows

1. Download the Python installer:
Go to the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/) and download the latest version of Python for Windows.

2. Run the installer:
    1. Double-click the downloaded `.exe` file to run the installer.
    2. **Important**: Check the box that says **"Add Python to PATH"** and install Tkinter package.
    3. Choose **Install Now** to install Python with the default settings, or customize the installation if needed.

3. Verify the installation
Once installed, open **Command Prompt** and verify the installation by running:
```bash
python --version
pip --version
```


## Install Python dependencies

Ensure Python is installed on your system along with the required dependencies. The pipeline requires Python 3.6 or higher. All other dependencies are listed in the `python_requirements.txt` file.

To install the necessary dependencies, it is recommended to create a **virtual environment**:

1. Create a virtual environment:
    ```bash
    python -m venv env
    ```

2. Activate the virtual environment:
   - On **Windows**:
     ```bash
     .\env\Scripts\activate
     ```
   - On **macOS and Linux**:
     ```bash
     source env/bin/activate
     ```

3. Install required dependencies:
    ```bash
    pip install -r python_requirements.txt
    ```
