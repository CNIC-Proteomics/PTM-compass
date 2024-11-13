## Test 1

Prueba Solver

Test from MSFragger results in open search. Heteroplasmia (heart)

Prepare workspace
```bash
mkdir tests/test1/results
```

### 1. SHIFTSadapter

```bash
python src/shifts/SHIFTSadapter.py -i "tests/test1/inputs/*_FrAll.tsv" -o tests/test1/results
```

### 2. DuplicateRemover

```bash
python src/shifts/DuplicateRemover.py -i "tests/test1/results/*_SHIFTS.feather" -c tests/test1/inputs/params.ini
```

### 3. DMcalibrator

```bash
python src/shifts/DMcalibrator.py -i "tests/test1/results/*_SHIFTS_Unique.feather" -c tests/test1/inputs/params.ini
```

### 4. PeakModeller

```bash
python src/shifts/PeakModeller.py -i "tests/test1/results/*_SHIFTS_Unique_calibrated.feather" -c tests/test1/inputs/params.ini
```

### 5. PeakSelector

```bash
python src/shifts/PeakSelector.py -i tests/test1/results/DMHistogram.tsv -c tests/test1/inputs/params.ini
```

### 6. PeakAssignator

```bash
python src/shifts/PeakAssignator.py -i tests/test1/results/DMTable.feather -a tests/test1/results/PeakSelector_ApexList.txt -c tests/test1/inputs/params.ini
```

### 7. PeakFDRer

```bash
python src/shifts/PeakFDRer.py -i tests/test1/results/DMTable_PeakAssignation.feather -e tests/test1/inputs/exp_table.tsv -c tests/test1/inputs/params.ini
```

___


### 1. DM0Solver

```bash
python src/solver/DM0Solver.py -i tests/test1/results/DMTable_PeakAssignation_FDRfiltered.tsv -a tests/test1/results/PeakSelector_ApexList.txt -c tests/test1/inputs/params.ini
```

### 2. ProteinAssigner

```bash
python src/tools/ProteinAssigner.py -i tests/test1/results/DMTable_PeakAssignation_FDRfiltered_DM0S.txt -f tests/test1/inputs/database.fasta -o tests/test1/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA.txt -c tests/test1/inputs/params.ini
```

### 3. ProteinAssigner

```bash
python src/tools/ProteinAssigner.py -i tests/test1/results/DMTable_PeakAssignation_FDRfiltered_DM0S.txt -f tests/test1/inputs/database.fasta -o tests/test1/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA.txt -c tests/test1/inputs/params.ini
```

### 2. ProteinAssigner

```bash
python src/tools/ProteinAssigner.py -i tests/test1/results/DMTable_PeakAssignation_FDRfiltered_DM0S.txt -f tests/test1/inputs/database.fasta -o tests/test1/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA.txt -c tests/test1/inputs/params.ini
```
