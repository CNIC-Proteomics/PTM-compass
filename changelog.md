___
## 1.2
```
DATE: 2024_12
```

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

