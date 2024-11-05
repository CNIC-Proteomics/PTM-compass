## Test 1

Test from MSFragger results in open search. Heteroplasmia (heart)


### 1. SHIFTSadapter

```bash
python src/shifts/SHIFTSadapter.py -i "tests/test1/inputs/RH_Heart_TMTHF_*.tsv" -o tests/test1/results
```

### 2. DuplicateRemover

```bash
python src/shifts/DuplicateRemover.py -i "tests/test1/results/*_SHIFTS.feather" -c config/fixed_params_msfragger.ini
```

### 3. DMcalibrator

```bash
python src/shifts/DMcalibrator.py -i "tests/test1/results/*_SHIFTS_Unique.feather" -c config/fixed_params_msfragger.ini
```

### 4. PeakModeller

```bash
python src/shifts/PeakModeller.py -i "tests/test1/results/*_SHIFTS_Unique_calibrated.feather" -c config/fixed_params_msfragger.ini
```

### 5. PeakSelector

```bash
python src/shifts/PeakSelector.py -i tests/test1/results/DMHistogram.tsv -c config/fixed_params_msfragger.ini
```

### 6. PeakAssignator


### 7. PeakFDRer

