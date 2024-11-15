# PTM-compass

PTM-compass is a toolset for adapting and analyzing search engine results from multiple proteomics tools such as Comet-PTM, ReCom, and MSFragger. It standardizes output files, allowing them to be processed in downstream analysis workflows.

# Installation

To install PTM-compass, clone this repository and ensure you have Python installed:

```bash
git clone https://github.com/CNIC-Proteomics/PTM-compass.git
cd PTM-compass
```

## Setting Up a Virtual Environment

It’s recommended to create a virtual environment to manage dependencies for SHIFTS.

1. **Create a virtual environment**:

    ```bash
    python -m venv env
    ```

2. **Activate the virtual environment**:

   - On **Windows**:
     ```bash
     .\env\Scripts\activate
     ```
   - On **macOS and Linux**:
     ```bash
     source env/bin/activate
     ```

3. **Install required dependencies**:

    ```bash
    pip install -r python_requirements.txt
    ```

## Requirements

The PTM-compass programs require Python 3.6 or above. All other dependencies are listed in the `python_requirements.txt` file.


# Modules

Each PTM-Compass module is designed with specific functionality and configurable parameters. Modules primarily use a configuration file in INI format but also support overriding parameters via the command line.

For comprehensive instructions on using each module, please refer to the **[Module Guide](MODULES.md)**.

## Example Commands

For additional examples and tests, please consult the **[Test Guide](TEST.md)**.


# License

This application is licensed under a **Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0) License**. See the [LICENSE](LICENSE.md) file for details.
