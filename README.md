# PTM-compass

PTM-compass is a toolset for adapting and analyzing search engine results from multiple proteomics tools such as Comet-PTM, ReCom, and MSFragger. It standardizes output files, allowing them to be processed in downstream analysis workflows.

# Installation

## Download the last release

+ Download the ReportAnalysis-vx.xx.zip from the last release and unzip the file:
https://github.com/CNIC-Proteomics/ReportAnalysis/releases

or

+ Clone the repository using the last release tag:

```bash
git clone https://github.com/CNIC-Proteomics/PTM-compass.git --branch {LAST_RELEASE_TAG}
```

## Install Python

Ensure Python is installed on your system along with the required dependencies.

For further information, consult the [INSTALLATION Guide](INSTALLATION.md).


# Modules

Each PTM-Compass module is designed with specific functionality and configurable parameters. Modules primarily use a configuration file in INI format but also support overriding parameters via the command line.

For comprehensive instructions on using each module, please refer to the **[Module Guide](MODULES.md)**.


# Example Commands

For additional examples and tests, please consult the **[Test Guide](TESTS.md)**.


# License

This application is licensed under a **Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0) License**. See the [LICENSE](LICENSE.md) file for details.
