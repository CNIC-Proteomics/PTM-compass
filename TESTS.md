## Test 1

Test from MSFragger results in open search. Heteroplasmia (muscle)

Dowloand test

```
cd tests && \
wget https://zenodo.org/records/14531166/files/heteroplasmic_muscle.zip?download=1 -O heteroplasmic_muscle.zip && \
unzip heteroplasmic_muscle.zip && \
cd ..
```

Prepare workspace
```bash
mkdir tests/heteroplasmic_muscle/results
```

### 1. SHIFTSadapter

```bash
python src/shifts/SHIFTSadapter.py -i "tests/heteroplasmic_muscle/inputs/msfragger/*.tsv" -o tests/heteroplasmic_muscle/results
```

### 2. DuplicateRemover

```bash
python src/shifts/DuplicateRemover.py -i "tests/heteroplasmic_muscle/results/*_SHIFTS.feather" -c tests/heteroplasmic_muscle/inputs/params.ini
```

### 3. DMcalibrator

```bash
python src/shifts/DMcalibrator.py -i "tests/heteroplasmic_muscle/results/*_SHIFTS_Unique.feather" -c tests/heteroplasmic_muscle/inputs/params.ini
```

### 4. PeakModeller

```bash
python src/shifts/PeakModeller.py -i "tests/heteroplasmic_muscle/results/*_SHIFTS_Unique_calibrated.feather" -c tests/heteroplasmic_muscle/inputs/params.ini
```

### 5. PeakSelector

```bash
python src/shifts/PeakSelector.py -i tests/heteroplasmic_muscle/results/DMHistogram.tsv -c tests/heteroplasmic_muscle/inputs/params.ini
```

### 6. PeakAssignator

```bash
python src/shifts/PeakAssignator.py -i tests/heteroplasmic_muscle/results/DMTable.feather -a tests/heteroplasmic_muscle/results/PeakSelector_ApexList.txt -c tests/heteroplasmic_muscle/inputs/params.ini
```

### 7. PeakFDRer

```bash
python src/shifts/PeakFDRer.py -i tests/heteroplasmic_muscle/results/DMTable_PeakAssignation.feather -e tests/heteroplasmic_muscle/inputs/exp_table.tsv -c tests/heteroplasmic_muscle/inputs/params.ini
```

___


### 1. DM0Solver

```bash
python src/solver/DM0Solver.py -i tests/heteroplasmic_muscle/results/DMTable_PeakAssignation_FDRfiltered.tsv -a tests/heteroplasmic_muscle/results/PeakSelector_ApexList.txt -c tests/heteroplasmic_muscle/inputs/params.ini
```

### 2. ProteinAssigner

```bash
python src/tools/ProteinAssigner.py -i tests/heteroplasmic_muscle/results/DMTable_PeakAssignation_FDRfiltered_DM0S.txt -f tests/heteroplasmic_muscle/inputs/database.fasta -o tests/heteroplasmic_muscle/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA.txt -c tests/heteroplasmic_muscle/inputs/params.ini
```

### 3. ProteinAssigner

```bash
python src/tools/ProteinAssigner.py -i tests/heteroplasmic_muscle/results/DMTable_PeakAssignation_FDRfiltered_DM0S.txt -f tests/heteroplasmic_muscle/inputs/database.fasta -o tests/heteroplasmic_muscle/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA.txt -c tests/heteroplasmic_muscle/inputs/params.ini
```

### 2. ProteinAssigner

```bash
python src/tools/ProteinAssigner.py -i tests/heteroplasmic_muscle/results/DMTable_PeakAssignation_FDRfiltered_DM0S.txt -f tests/heteroplasmic_muscle/inputs/database.fasta -o tests/heteroplasmic_muscle/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA.txt -c tests/heteroplasmic_muscle/inputs/params.ini
```
