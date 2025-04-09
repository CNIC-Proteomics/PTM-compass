# Samples

Ensure Python is installed on your system along with the required dependencies.

For further information, consult the [INSTALLATION Guide](INSTALLATION.md).



## Samples 1: Open search using MSFragger for Mouse Heteroplasmia (Heart)

Input files for PTM-compass, derived from the study by Bagwan N, Bonzon-Kulichenko E, Calvo E, et al. [1], with results from an open search conducted using nf-SearchEngine (MSFragger[2]) results.

### Download the sample files:

+ On Linux:
```bash
cd samples && \
wget https://zenodo.org/records/15182445/files/heteroplasmic_heart.zip?download=1 -O heteroplasmic_heart.zip && \
unzip heteroplasmic_heart.zip && \
cd ..
```

or

+ On Windows:
```batch
@echo off
mkdir samples
cd samples
curl -L -o heteroplasmic_heart.zip https://zenodo.org/records/15182445/files/heteroplasmic_heart.zip?download=1 
powershell -Command "Expand-Archive -Path heteroplasmic_heart.zip -DestinationPath ."
cd ..
```

### Execute the programs for the current sample:

0. Prepare workspace:
```bash
mkdir samples/heteroplasmic_heart/results
```

1. SHIFTSadapter:
```bash
python src/shifts/SHIFTSadapter.py -i "samples/heteroplasmic_heart/inputs/msfragger/*.tsv" -o samples/heteroplasmic_heart/results
```

2. DuplicateRemover:
```bash
python src/shifts/DuplicateRemover.py -i "samples/heteroplasmic_heart/results/*_SHIFTS.feather" -c samples/heteroplasmic_heart/inputs/params.ini
```

3. DMcalibrator:
```bash
python src/shifts/DMcalibrator.py -i "samples/heteroplasmic_heart/results/*_SHIFTS_Unique.feather" -c samples/heteroplasmic_heart/inputs/params.ini
```

4. PeakModeller:
```bash
python src/shifts/PeakModeller.py -i "samples/heteroplasmic_heart/results/*_SHIFTS_Unique_calibrated.feather" -c samples/heteroplasmic_heart/inputs/params.ini
```

5. PeakSelector:
```bash
python src/shifts/PeakSelector.py -i samples/heteroplasmic_heart/results/DMHistogram.tsv -c samples/heteroplasmic_heart/inputs/params.ini
```

6. PeakInspector:
```bash
python src/shifts/PeakInspector.py -i samples/heteroplasmic_heart/results/DMHistogram.tsv -c samples/heteroplasmic_heart/inputs/params.ini
```

7. PeakAssignator:
```bash
python src/shifts/PeakAssignator.py -i samples/heteroplasmic_heart/results/DMTable.feather -a samples/heteroplasmic_heart/results/PeakSelector_ApexList.txt -c samples/heteroplasmic_heart/inputs/params.ini
```

8. PeakFDRer:
```bash
python src/shifts/PeakFDRer.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation.feather -e samples/heteroplasmic_heart/inputs/experimental_table.tsv -c samples/heteroplasmic_heart/inputs/params.ini
```

___

9. DM0Solver:
```bash
python src/solver/DM0Solver.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered.tsv -a samples/heteroplasmic_heart/results/PeakSelector_ApexList.txt -c samples/heteroplasmic_heart/inputs/params.ini
```

10. ProteinAssigner:
```bash
python src/tools/ProteinAssigner.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S.txt -f samples/heteroplasmic_heart/inputs/database.fasta -o samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA.txt -c samples/heteroplasmic_heart/inputs/params.ini
```

11. TrunkSolver:
```bash
python src/solver/TrunkSolver.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA.txt -f samples/heteroplasmic_heart/inputs/database.fasta -c samples/heteroplasmic_heart/inputs/params.ini
```

12. ProteinAssigner:
Important! Please note that there is a second parameter file (2nd round).
```bash
python src/tools/ProteinAssigner.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_TS.txt -f samples/heteroplasmic_heart/inputs/database.fasta -o samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_TS_PA.txt -c samples/heteroplasmic_heart/inputs/params_2_Round.ini
```

13. PeakAssignator:
Important! Please note that there is a second parameter file (2nd round).
```bash
python src/shifts/PeakAssignator.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_TS_PA.txt -a samples/heteroplasmic_heart/results/PeakSelector_ApexList.txt -c samples/heteroplasmic_heart/inputs/params_2_Round.ini
```

14. BinomialSiteListMaker:
```bash
python src/solver/BinomialSiteListMaker.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_T_PeakAssignation.tsv -o samples/heteroplasmic_heart/results/BinomialSiteListMaker_PEAKS_Output.xlsx -c samples/heteroplasmic_heart/inputs/params.ini
```

15. SiteSolver:
```bash
python src/solver/SiteSolver.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_T_PeakAssignation.tsv -pl samples/heteroplasmic_heart/inputs/site_solver_list.txt -c samples/heteroplasmic_heart/inputs/params.ini
```

16. ExperimentSeparator:
```bash
python src/tools/ExperimentSeparator.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_T_PeakAssignation_SS.txt -c "Experiment" -o samples/heteroplasmic_heart/results/
```

17. PDMTableMaker:
```bash
echo "samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_T_PeakAssignation_SS_Heart_FDR.tsv" > "samples/heteroplasmic_heart/results/experiment.txt"
python src/solver/PDMTableMaker.py -i samples/heteroplasmic_heart/results/experiment.txt -f samples/heteroplasmic_heart/inputs/database.fasta -c samples/heteroplasmic_heart/inputs/params.ini
```

18. GroupMaker:
```bash
python src/solver/GroupMaker.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_T_PeakAssignation_SS_Heart_FDR_PDMTable.txt -u samples/heteroplasmic_heart/inputs/group_maker_list.txt -c samples/heteroplasmic_heart/inputs/params.ini
```

19. Joiner:
```bash
python src/solver/Joiner.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_T_PeakAssignation_SS_Heart_FDR_PDMTable_GM.txt -c samples/heteroplasmic_heart/inputs/params.ini
```

20. FreqProcessor:
```bash
python src/solver/FreqProcessor.py -i samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_T_PeakAssignation_SS_Heart_FDR_PDMTable_GM_J.txt -od samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_T_PeakAssignation_SS_Heart_FDR_PDMTable_GM_J_PDM_Table_pgmFreq.tsv  -og samples/heteroplasmic_heart/results/DMTable_PeakAssignation_FDRfiltered_DM0S_PA_T_PeakAssignation_SS_Heart_FDR_PDMTable_GM_J_PGM_Table_pgmFreq.tsv
```



## Samples 2: Open search using MSFragger for Mouse Heteroplasmia (Liver)

You can download the input files for this `liver` sample from the study by Bagwan N, Bonzon-Kulichenko E, Calvo E, et al. [1] at the following URL:

https://zenodo.org/records/15182445/files/heteroplasmic_liver.zip?download=1

To execute the pipeline, follow the same steps as in Sample 1.



## Samples 3: Open search using MSFragger for Mouse Heteroplasmia (Muscle)

You can download the input files for this `muscle` sample from the study by Bagwan N, Bonzon-Kulichenko E, Calvo E, et al. [1] at the following URL:

https://zenodo.org/records/15182445/files/heteroplasmic_muscle.zip?download=1

To execute the pipeline, follow the same steps as in Sample 1.



# References

[1] Bagwan N, Bonzon-Kulichenko E, Calvo E, et al. Comprehensive Quantification of the Modified Proteome Reveals Oxidative Heart Damage in Mitochondrial Heteroplasmy. Cell Reports. 2018;23(12):3685-3697.e4. https://doi.org/10.1016/j.celrep.2018.05.080

[2] Kong, A., Leprevost, F., Avtonomov, D. et al. MSFragger: ultrafast and comprehensive peptide identification in mass spectrometry–based proteomics. Nat Methods 14, 513–520 (2017). https://doi.org/10.1038/nmeth.4256
