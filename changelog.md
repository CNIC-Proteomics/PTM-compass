___
## 1.7

### Date 📅 *2026_01*

### Changes in detail

+ PeakModeller: Added caldeltamh_column parameter.



____
## 1.6

### Date 📅 *2026_01*

### Changes in detail

**rc1**
+ Processing of refmod search results.
+ Fixed minor bugs.



___
## 1.5

### Date 📅 *2025_09*

### Changes in detail

**rc1**
+ Updated parameters. By default, show the unassigned modifications in the BinomialSiteListMaker.
+ DMcalibrator: Add calibrated dm column for refrag data.
+ SHIFTSadapter: Detect Refrag input and generate delta_peptide using modification site data from Refrag.
+ Updated documentation: Zenodo repository.


___
## 1.4

### Date 📅 *2025_04*

### Changes in detail

+ Rename the 'qf' column to 'qc' to maintain consistency with the manuscript's nomenclature.
+ The ReFrag (REFMOD) code is deprecated here. It will be used in the `nf-SearchEngine` pipeline.
+ Updated the documentation and test guide.
+ Fixing a minor bug: BinomialSiteListMaker now accepts comments in the given parameter file using the '#' character.
+ ProteinAssigner:
    - Fixing a bug: Remove this line because it deletes columns that are empty, but they are needed.


___
## 1.3

### Date 📅 *2025_02*

### Changes in detail

+ PeakSelector:
  - Fixed a bug in the 'PeakSelector' related to the bin width.
  - Duplicate bin params in config

___
## 1.2

### Date 📅 *2024_12*

### Highlights

+ PDMTableMaker is executed using Experiment column.

+ The 'FreqProcessor' has been added.

### Changes in detail

+ PDMTableMaker is executed using Experiment column.

+ The 'FreqProcessor' has been added to replace the old 'PGM_Processor' program. It extracts the PGM and PDM frequencies.

___
## 1.1
```
DATE: 2024_11
```

### Highlights

+ Fix a bug: Local FDR calculation for orphan PSMs

### Changes in detail

+ PeakFDRer: Fixing a bug. The Local FDR calculation for orphan PSMs.

___
## 1.0
```
DATE: 2024_11
```

### Highlights

+ The term 'Experiment' has been replaced with 'Batch' throughout the workflow.

+ All programs now utilize a unified configuration file.

+ A revamped file structure has been introduced.

### Changes in detail

+ PeakFDRer: use an updated 'experimental_table' that includes the columns 'Experiment','Batch' and 'Spectrum_File'. The FDR calculation is based on the information in the 'Batch' column.


___
## 0.X
```
DATE: 2024_XX
```

### Highlights

+ Incorporated the previous source code from SHIFTS and PTM-Solver.

