# PTM-compass

PTM-compass is a toolset for adapting and analyzing search engine results from multiple proteomics tools such as Comet-PTM, ReCom, and MSFragger. It standardizes output files, allowing them to be processed in downstream analysis workflows.

## Installation

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

The SHIFTS toolset requires Python 3.6 or above. All other dependencies are listed in the `python_requirements.txt` file.

## Usage

Each PTM-compass module has specific functionality and parameters. Modules use a configuration file (INI format) but also allow parameters to be specified via the command line. 

For detailed instructions on each module, please refer to the **[USAGE Guide](USAGE.md)**.

## Modules Overview

- **SHIFTSadapter**: Adapts output files from Comet-PTM, ReCom, and MSFragger search engines, standardizing them for SHIFTS analysis.
- **DMcalibrator**: Calibrates mass delta values.
- *(Additional modules would be listed here)*

## Example Commands

```bash
# Run the SHIFTSadapter module
python SHIFTSadapter.py -i path/to/input/file -o path/to/output/directory

# Run the DMcalibrator module
python DMcalibrator.py -c path/to/config.ini
```

---

For further examples and a detailed breakdown of available parameters, refer to the **[USAGE Guide](USAGE.md)**.

---

## License

This application is licensed under a **Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0) License**. See the [LICENSE](LICENSE.md) file for details.
