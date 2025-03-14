# Modules

+ [SHIFTS Modules](#shifts-modules)
+ [SOLVER Modules](#solver-modules)
+ [PTM quantification Modules](#ptm-quantification-modules)

Each module uses a configuration file (INI format), but some of the parameters it contains can also be specified through the command line. To see the parameters available through the command line and their descriptions, run each module with the help option, `-h` (e.g., `python DMcalibrator.py -h`).


## SHIFTS Modules

1. [SHIFTSadapter](#1-shiftadapter)
2. [DuplicateRemover](#2-duplicateremover)
3. [DMcalibrator](#3-dmcalibrator)
4. [PeakModeller](#4-peakmodeller)
5. [PeakSelector](#5-peakselector)
6. [PeakAssignator](#6-peakassignator)
7. [PeakFDRer](#7-peakfdrer)


### 1. SHIFTSadapter

This module adapts search engine results from Comet-PTM, ReCom, and MSFragger for analysis with SHIFTS. It removes any extra lines before the column headers and adds a column containing the input file name. If the input file type does not have extra lines before the headers and already includes an input file name column, this step can be skipped. Every subsequent module assumes that the first line of the input file contains the column headers.

For MSFragger inputs, the module calculates the left and right positions of modifications.

In all cases, a 'Spectrum_File' column is added.

* **Example:**
  ```bash
  python SHIFTSadapter.py -i path/to/input/file -o path/to/output/directory
  ```

  - **Input:**
    - A tab-separated file containing results from Comet-PTM, ReCom, or MSFragger search engines.

  - **Output:**
    - A tab-separated/Feather file (without extra header lines).
    - A log file containing header information.


[Go to top](#modules)
___


### 2. DuplicateRemover

This module will remove scan duplicates, keeping only the scan candidate that meets the following criteria: highest rank, highest score (if there are several with the same rank), highest sp_score (if there are several with the same score).

* **Example:**
  ```bash
  python DuplicateRemover.py -i path/to/input/file -c path/to/config/file
  ```

  - **Input:**
    - A file from SHIFTSadapter output.
    - Command-line or Config INI file with the parameters:
    ```
      -s (--scan) = ScanID column name (case sensitive, column must contain an unique ID for each scan)
      -n (--num) = Rank column name (case sensitive)
      -x (--score) = Score column name (case sensitive) 
      -p (--spscore) = SpScore column name (case sensitive)
    ```

  - **Output:**
    - The same file, with duplicates removed.
    - A log file.


[Go to top](#modules)
___


### 3. DMcalibrator

This module calculates the calibrated values for experimental masses and deltamasses. The dataset is filtered by a user-defined minimum score and maximum ppm, to obtain a subset of high-quality identifications that can be used for calibration. The median relative error (median of the absolute error column divided by the MZ column) is calculated to obtain the ‘alpha’ value:
alpha = (df_filtered[abs_error]/df_filtered[mzcolumn]).median()
Then, this value is used to calibrate the experimental MZ values of the entire dataset as follows:

```
cal_exp_mz = exp_mz * (1  - alpha)
```

* **Example:**
  ```bash
  python DMcalibrator.py -i path/to/input/file -c path/to/config/file
  ```

  - **Input:**
    - A file from SHIFTSadapter or DuplicateRemover output.
    - A configuration file (INI). The following parameters are used:
    ```
      score_min: Minimum score to filter by
      ppm_max: Maximum PPM error to filter by
      scorecolumn: Name of column containing score (case-sensitive)
      zcolumn: Name of column containing charge (case-sensitive)
      mzcolumn: Name of column containing experimental M/Z (case-sensitive)
      seqcolumn: Name of column containing sequence (case-sensitive)
      seqdmcolumn: Name of column containing sequence with deltamass within square brackets (case-sensitive)
      proteincolumn: Name of column containing protein IDs (case-sensitive)
      decoyprefix: Prefix used for decoy protein IDs (case-sensitive)
      calseqcolumn: Name of output column containing sequence with calibrated deltamass (case-sensitive)
      decimal_places: Number of decimal places to use in sequence+deltamass output columns
    ```
    Also, the "config" ini file has the three sections:
    ```
      Aminoacid masses
      Fixed modifications for each aminoacid (if there are any)
      Other masses (Hydrogen, Oxygen, proton)
    ```

  - **Output:**
    - The same file with additional columns for theoretical MH and MZ, calibrated MH and MZ, calibrated deltamass MH and MZ, absolute error, ppm error, sequence with calibrated deltamass.
    - A log file containing systematic error before and after calibration, alpha, StdDevMAD_ppm (the mean absolute deviation for the ppm error), number of PSMs before and after filtering (size of the filtered, high quality dataset that was used for calibration)


[Go to top](#modules)
___


### 4. PeakModeller

This module concatenates a group of files, generates a histogram grouped by deltamass bins of a user-specified width, and calculates the frequency and slopes (first and second derivatives) for each bin, using linear regression.

* **Example:**
  ```bash
  python PeakModeller.py -i path/to/input/file -c path/to/config/file
  ```

  - **Input:**
    - A text file containing a list of calibrated files to be modelled together
    - A configuration file (INI). The following parameters are used:
    ```
      bins: Width of the bins
      slope_points: Number of points (bins) to use for slope calculation
      smooth_points: Number of points (bins) to use for smoothing
      separate_modelling: Flag to model histograms of target and decoy separately or together.
    ```

  - **Output:**
    - A tab-separated file containing all the input files together (DMTable), including a new ‘Filename’ column that tracks the origin of each PSM.
    - A tab-separated file containing the histogram (DMHistogram). This table contains columns with the bin, bin midpoint, frequency, slope1 (first derivative) and slope2 (second derivative).
    - A log file.


[Go to top](#modules)
___


### 5. PeakSelector

This module filters a DMHistogram table (as generated by PeakModeller) according to user-specified thresholds for the columns containing slope and frequency. This filtered dataset is used to calculate a list of apexes. For each bin (row) where the value of the first derivative (slope) changes from positive to negative, the exact DM value where the first derivative is 0 is interpolated using a user-defined number of points surrounding the apex bin.
Taking the x (bin midpoint) and y (first derivative) values for those points it will identify the apex as the x value where y equals 0.

* **Example:**
  ```bash
  python PeakSelector.py -i path/to/input/file -c path/to/config/file
  ```

  - **Input:**
    - A DMHistogram table (as generated by PeakModeller) to be filtered.
    - A configuration file (INI). The following parameters are used:
    ```
        frequency = 0              # Threshold for number of PSMs
        apex_points = 4            # Number of points (bins) to use for apex calculation
        x2= -0.0000006             # Quadratic term of the function to calculate the zones to search max slope
        m= 1.0002                  # Lineal term of the function to calculate the zones to search max slope
        intercept= -0.0367         # Intercept of the function to calculate the zones to search max slope
        dm0= -230                  # Minimum mass of the spectra
        dm1= 500                   # Maximum mass of the spectra
        ci_interval= 84.13         # % of 1-tailed CI for removing outliers (84.13% recommended)
    ```

  - **Output:**
    - A text file containing the apex list.
    - A log file containing the number of apexes that were calculated.


[Go to top](#modules)
___


### 6. PeakAssignator

This module will assign every PSM to the closest deltamass peak found in the provided apex list and identify it as either belonging to that peak, or as an orphan. To do so, it will calculate the absolute distance between the deltamass value and the assigned peak and then the error in ppm:
```
distance = abs(assigned_peak - delta_MH)
distance_ppm = (distance / (theoretical_mass + assigned_peak)) * 1e6
```
If that value is larger than the user-defined threshold, it will be considered an orphan.

* **Example:**
  ```bash
  python PeakAssignator.py -i path/to/input/file -c path/to/config/file
  ```

  - **Input:**
    - A DMtable.
    - An apex list.
    - A configuration file (INI). The following parameters are used:
    ```
			ppm_max: Maximum ppm difference for peak assignation
			peak_label: Label for peaks
			orphan_label: Label for orphans
			caldeltamh_column: Name of column containing calibrated Delta MH
			theomh_column: Name of column containing theoretical MH for ppm error calculation
			closestpeak_column: Output column that will contain the closest peak
			peak_column: Output column that will contain the peak/orphan labels
			deltamass_column: Output column that will contain the assigned deltamass
			ppm_column: Output column that will contain the ppm error
			mod_peptide_column: Name of column containing sequence with deltamass in XXX[DM]XXX or XXXXXX_DM format (case-sensitive)
			assign_seq_column: Name of output column containing sequence with assigned deltamass (case-sensitive)
			decimal_places: Number of decimal places to use in sequence+deltamass output columns
    ```

  - **Output:**
    - A DMtable with additional columns for the closest peak, assignation as peak or orphan, assigned deltamass, ppm error, sequence with assigned deltamass.
    - A log file.


[Go to top](#modules)
___


### 7. PeakFDRer

This module will calculate global, local, and peak FDR values for a DMtable subdivided by experiment. Global FDR is calculated per experiment, local and peak FDR is calculated for the whole dataset. Experiment groups are created using the information in the “Filename” column (created by the DMcalibrator module) of the DMTable, and a user-provided list that assigns each filename to a group. For the global FDR, rather than taking an entire experiment, this module will separate it in two deltamass regions (defined by the parameter dm_region_limit, default value -56) and calculate a global FDR for each region.

* **Example:**
  ```bash
  python PeakFDRer.py -i path/to/input/file -c path/to/config/file
  ```

  - **Input:**
    - A DMtable.
    - A tab-separated file containing, in order:
    ```
      A column with the batch name
      A column with the experiment name
      A column with the file path (must match the file paths in the Filename column of your DMtable).
    ```
    - A configuration file (INI). The following parameters are used:
    ```
      score_column: Name of column containing score (case-sensitive)
      dm_region_limit: Deltamass region limit for Global FDR. Two regions will be created, DM equal to or above and DM below this value
      dm_column: Name of column containing deltamass for region limits (case-sensitive)
      peak_outlier_value: Peak FDR value to be assigned to orphans (default=1)
      peak_label: Label for peaks
      peak_column: Output column that will contain the peak/orphan labels
      caldeltamh_column: Name of column containing calibrated Delta MH
      closestpeak_column: Output column that will contain the closest peak
    ```

  - **Output:**
    - One DMtable for each batch with additional columns for the global, local and peak FDR ranks and values.
    - A log file.


[Go to top](#modules)
___


## SOLVER Modules

1. [DM0Solver](#1-dm0solver)
2. [TrunkSolver](#2-trunksolver)
3. [SiteListMaker](#3-sitelistmaker)
4. [SiteSolver](#4-sitesolver)


### 1. DM0Solver

DM0Solver is a module that detects if a modified peptide has a Δmass belonging to a list provided by the user (Table 1), for that purpose absolute error is calculated. In such a case, the Δmass is appended at the end of the clean sequence (DM0Sequence output column) and the corresponding label is added in an additional column named DM0Label. If Δmass does not belong to the list, the module passes the modified sequence without any modification to the output columns.

* **Example:**
  ```bash
  python DM0Solver.py -i path/to/input/file -c path/to/config/file
  ```

  - **Input:**
    - A DMtable.
    - A tab-separated file containing, in order:
    ```
      A column with the batch name
      A column with the experiment name
      A column with the file path (must match the file paths in the Filename column of your DMtable).
    ```
    - A configuration file (INI). The following parameters are used:
    ```
      score_column: Name of column containing score (case-sensitive)
      dm_region_limit: Deltamass region limit for Global FDR. Two regions will be created, DM equal to or above and DM below this value
      dm_column: Name of column containing deltamass for region limits (case-sensitive)
      peak_outlier_value: Peak FDR value to be assigned to orphans (default=1)
      peak_label: Label for peaks
      peak_column: Output column that will contain the peak/orphan labels
      caldeltamh_column: Name of column containing calibrated Delta MH
      closestpeak_column: Output column that will contain the closest peak
    ```

  - **Output:**
    - DM0Solver output (default suffix: “DM0S”). New columns:
        + DM0Sequence_output_column_name: sequence corrected by DM0Solver.
        + DM0Label_output_column_name: selected label of the list provided by the user.
        + DM0Label_error_output_column_name: absolute error resulting from the selection of the label that appears in DM0Label_output_colummn_name.
    - A log file.


[Go to top](#modules)
___


### 2. TrunkSolver

TrunkSolver is a module developed with the aim of detecting whether the Δmass, in a modified peptide, may be explained by a truncation or tryptic cut of a non-modified peptide inside the sequence of the corresponding protein, and its possible combination with the presence of a Δmass belonging to a list provided by the user. In such a case, the Δmass is appended at the end of the clean sequence (TrunkSequence output column), the corresponding label is added in an additional column named TrunkLabel, and recalculated Δmass (TrunkDM output column). If TrunkSolver is unable to explain the Δmass by a truncation, then it passes the modified sequence and its original Deltamass without any modification to the output columns. In both cases, five extra columns (New_DM, New_Theo_mh, Trunk_stats_mods) will be created for subsequent PeakAssignatior execution if it is desired. The relative error is calculated as follows:

**𝑅𝑒𝑙𝑎𝑡𝑖𝑣𝑒 𝑒𝑟𝑟𝑜𝑟(𝑝𝑝𝑚) = abs(((𝑇ℎ𝑒𝑜𝑟𝑒𝑡𝑖𝑐𝑎𝑙_𝑚ℎ + 𝐿𝑎𝑏𝑒𝑙_𝑚𝑎𝑠𝑠) − 𝐸𝑥𝑝_𝑚ℎ) ∗ 1000000 / (𝑇ℎ𝑒𝑜𝑟𝑒𝑡𝑖𝑐𝑎𝑙_𝑚ℎ + 𝐿𝑎𝑏𝑒𝑙_𝑚𝑎𝑠𝑠))**

* **Example:**
  ```bash
  python TrunkSolver.py -i path/to/input/file -c path/to/config/file
  ```

  - **Input:**
    - A .tsv file.
    - A .fasta file.
    - A MassMod configuration file.
    - A configuration file (INI). The following parameters are used:
    ```
      Relative_Error_ppm: relative error (ppm) allowed.
      Exp_mh_column_name: calibrated experimental mh column name.
      Theo_mh_column_name: theoretical mh column name.
      Sequence_column_name: sequence with Δmass column name.
      Calibrated_Delta_MH_column_name: calibrated Δmass mh column name.
      MasterProtein_column_name: Master Protein accession code column name.
      static_modifications_column_name: static modifications column name.
      Decnum: decimals points required in TrunkSequence column.
      X: parameter indicating the extension allowed for TrunkSolver to extend from the original Δmass position residue.
      New_Deltamass_output_column_name: new Δmass column name.
      New_Theo_mh_output_column_name: new theoretical mh column name.
      TrunkSequence_output_column_name: column name where the chosen sequence is annotated.
      TrunkDM_output_column_name: column name where the recalculated Δmass is annotated, considering the label.
      TrunkLabel_output_column_name: column name where the chosen label is annotated.
      TrunkLabel_ppm_output_column_name: column name where the calculated error in ppm is annotated.
      Static_modifications_position_output_column_name: column name where the new fix modifications positions are annotated.
      output_file_suffix: chosen suffix for output file.
      Missing_cleavages_output_column_name: output column name for the number of missing cleavages.
      Truncation_output_column_name: column where truncations are annotated.
      TrunkPlainPeptide_output_column_name: column where the peptide without Δmass is annotated.
    ```
    - A TrunkSolver list (list of masses with its corresponding label): An example of input list for TrunkSolver configuration file can be observed in Table 2. The first column shows examples of labels, TMT: Δmass of tandem mass tag, 2TMT; two Δmasses of tandem mass tags; -TMT: minus Δmass of tandem mass tag ,-2TMT: minus two Δmasses of tandem mass tags. The second column contains de mass in Da of each label. TrunkSolver uses this list to assign a label, as long as it meets the error threshold.

      Table 2. Example of input list for TrunkSolver configuration file
        | **Label** | **Mass (Da)**  |
        |-----------|----------------|
        | TMT       | 229.162932     |
        | 2TMT      | 458.325864     |
        | -TMT      | -229.162932    |
        | -2TMT     | -458.325864    |


  - **Output:**
    - TrunkSolver output (default suffix: "_TS"). New columns:
      + TrunkSequence_output_column_name: column where reassigned sequence is annotated.
      + TrunkDM_output_column_name: column where recalculated Δmass is annotated, considering the labels.
      + TrunkLabel_output_column_name: column where the selected label is saved. If the Δmass corresponds to a combination of a label from the configuration file and a cut, the type of cut is noted (TrypticCut for tryptic cuts, Truncation for non-tryptic cuts).
      + TrunkLabel_ppm_output_column_name: column where the calculated error (ppm) from selecting the label is annotated.
      + New_Theo_mh_output_column_name: column where the recalculated theoretical mass is annotated.
      + New_Deltamass_output_column_name: column where the recalculated Δmass is saved.
      + Static_modifications_position_output_column_name: column where new static modification positions are saved, as changes in the sequence may affect them.
      + TrunkPlainPeptide_output_column_name: column where the peptide without Δmass is annotated.
      + Missing_cleavages_output_column_name: column where the number of missing cleavages is annotated.
      + Truncation_output_column_name: column where truncations are annotated as “1” (0: No truncation, 1: Truncation).

    - A log file (default suffix: "TS_logFile").

      Table 3. Example of TrunkSolver output file columns, considering input file
        | **DM0Sequence**                            | **Thoeretical_mh** | **Modifications**                                 |
        |--------------------------------------------|--------------------|---------------------------------------------------|
        | LGEHNLDVLEGNEQFLNA[-499.331973]AK          | 2669.42            | 1_S_0.0000_N                                      |
        | GTFASLS[229.141559]ELHCDK                  | 1923.00            | 1_S_0.0000_N, 11_S_57.021464, 13_S_229.162932     |
        | TLER[-499.281621]EACLLNANK                 | 1990.115           | 1_S_0.0000_N, 7_S_57.021464, 13_S_229.162932      |

    Output file columns
      | **TrunkSequence**                    | **TrunkDM** | **TrunkLabel**     | **TrunkLabel_ppm** | **New_theoretical_mh** | **New_DM** | **Static_modifications_position**                 |
      |--------------------------------------|-------------|--------------------|--------------------|------------------------|------------|---------------------------------------------------|
      | LGEHNLDVLEGNEQFLN_-0.00015           | -0.00015    | Truncation; DM0    | 0.06               | 2170.09                | -0.00015   | 1_L_229.162932_N                                  |
      | GTFASLSELHCDK_229.141                | 229.141     | +TMT               | 9.93               | 2152.167               | -0.02      | 1_G_229.162932_N, 11_S_57.021464, 13_S_229.162932 |
      | EACLLNANK_-0.006                     | -0.006      | Trypticcut; DM0    | 4.14               | 1490.84012             | -0.006     | 1_E_229.162932_N, 3_S_57.021464, 9_S_229.162932   |


[Go to top](#modules)
___


### 3. SiteListMaker

SiteListMaker is a module developed with the objective of acquiring a comprehensive overview of identified modifications within the proteome under analysis. This includes the frequency of each modification, as well as the precise residues where these modifications are localized. Three tables are generated as a result.

i. The first table presents the **raw frequencies** of each modification (Δmass), detailing how frequently Δmass X occurs on amino acid Y at positions [-5,5], with zero denoting the position where the modification is specifically localized.

ii. The second table mirrors the first but incorporates a **correction to eliminate background noise** according to the following equation:
   
   **Expected = Observed − (ΣPositionᵢ * ΣResidueⱼ) / Total of ΔMassᵧ**

   For each observed point, the sum of the frequencies for that position (i) is multiplied by the sum of the frequency of that residue (j) across all positions, divided by the total sum of frequencies for that Δmass (y).

iii. The third table exclusively focuses on the **frequencies of modifications at residues in position zero**, signifying instances where modifications are localized on that particular residue. This final table provides a detailed insight into the proteome, specifically identifying which residues are modified, proving invaluable for another module in this study, namely **SiteSolver**.

- **Input:**
  - `.tsv` file
  - Configuration file:
    - SiteListMaker parameters:
      ```
      Relative_Error_ppm: relative error (ppm) allowed.
      Theo_mh_column_name: theoretical mh column name.
      Sequence_column_name: sequence with Δmass column name.
      Calibrated_Delta_MH_column_name: calibrated Δmass mh column name.
      PeakAssignation_column_name: output column containing peak/orphan labels.
      PeakNaming: parameter indicating how decoys are named.
      Frequency_Table: name for the output file of the frequency table.
      Clean_Frequency_Table: name for the output file of the clean frequency table.
      Clean_P0_Frequency_Table: name for the output file of the clean position-zero frequency table.
      ```

- **Output:**
  - Three tables:
    1. **Frequency_Table**: Contains the unprocessed occurrences of each modification, showing how frequently Δmass X appears on amino acid Y at positions [-5,5], with zero marking the exact localization of the modification.

    2. **Clean_Frequency_Table**: This table is similar to the first one but includes a correction mechanism to eliminate background noise.

    3. **Clean_P0_Frequency_Table**: This table focuses on modifications at position zero, indicating instances where the modification occurs on that particular residue.

  - Log file (default suffix: "SLM_logFile").


[Go to top](#modules)
___


### 4. SiteSolver

**SiteSolver** is a module designed to detect if a modified peptide has its Δmass in an incorrect position. In such cases, the Δmass location within the sequence is corrected in the "SiteSequence" column. If the module does not find any possible position, it passes the modified sequence without any modification to the output column.

The process works by first determining if the amino acid position where the Δmass is originally located is **prohibited**. This is verified using a list based on **SiteListMaker**. If the amino acid is allowed for that Δmass, the modified sequence is passed without any modification. However, if the amino acid is prohibited, **SiteSolver** analyzes the contiguous amino acids to find a suitable relocation.

- If only one of the neighboring amino acids is prohibited, the Δmass is corrected by assigning it to an allowed amino acid based on **SiteListMaker**.
- If both neighboring amino acids are allowed, the order of appearance of the residues is taken into account.
  
This process repeats until the number of positions analyzed, on either side, exceeds the maximum allowed by the **X parameter**. To do so, the **relative error** will be calculated:

```
Relative_error(ppm) = abs(((Labelmass + Δmass_user_selection) − Exp_mh) * 1000000 / (Theoretical_mh + Labelmass))
```

- **Input:**
  - `.tsv` file
  - `UserList.txt` file (provided by the user) The user file contains two columns, as shown in Table 4. The first column lists all the Δmass values that the user wishes to relocate, and the second column lists all permissible residues for each Δmass, arranged in descending order of occurrence of the Δmass-residue combination in the proteome under study. This information is provided by **SiteListMaker**.

    Table 4: Example of input user list for SiteSolver
    | Δmass     | Residue     |
    |-----------|-------------|
    | 15.99492  | W, P, Y     |
    | 14.01565  | D, E        |
    | 3.994915  | W           |

- Configuration file:
  - SiteSolver parameters:
    ```
    Theo_mh_column_name: theoretical mh column name.
    Relative_Error_ppm: relative error (ppm).
    Sequence_column_name: peptide sequence with Δmass column name.
    cal_Dm_mh_column_name: calibrated Δmass name.
    x: parameter that indicates the extension (left and right from the original residue) of the amino acids to analyze.
    SiteSequence_column_name: output column for the sequence with corrected Δmass position.
    SiteCorrection_column_name: output column where correction site is annotated.
    SiteDM_column_name: output column where selected Δmass is annotated.
    SiteDMError_ppm_column_name: output column for the error of the selected Δmass.
    Output_file_suffix: chosen suffix for output file.
    ```

- **Output**:
  - SiteSolver output (default suffix: "SS"). New columns:
    - **SiteSequence_column_name**: sequence with the Δmass positioned in the correct residue.
    - **SiteCorrection_column_name**: amino acid change, showing the previous residue where Δmass was located and the new residue where it is relocated.
    - **SiteDM_column_name**: selected Δmass from the user list.
    - **SiteDMError_ppm_column_name**: error of the selected Δmass.

  - Log file (default suffix: "SS_logFile").

  
[Go to top](#modules)
___


## PTM quantification Modules

1. [PDMTableMaker](#1-pdmtablemaker)
2. [GroupMaker](#2-groupmaker)
3. [Joiner](#3-joiner)


### 1. PDMTableMaker

PDMTableMaker computes several indispensable parameters for the subsequent program execution and the ensuing implementation of newly developed quantification workflows crucial for the accurate interpretation of data.

- **Input:**
  - `.tsv` file
  - `.fasta` file
  - Configuration file:
    - PDMTableMaker parameters:
      ```
      Sequence_column_name: sequence with Δmass column name.
      DM_column_name: Δmass column name.
      Theo_mh_column_name: theoretical mh column name.
      MasterProtein_column_name: Master Protein accession code column name.
      output_file_suffix: chosen suffix for output file.
      Missing_Cleavage_column_name: missing cleavage number column name.
      Truncated_column_name: column name in which truncations are annotated column name.
      Score_parameter: score parameter to select best scan identifier. 1 if the best score is the highest and 0 if the best score is the lowest.
      Score_column_name: column in which scores for the best scan identifier are annotated.
      ScanID_column_name: column name in which best scan identifier is annotated.
      ```
    - PDMTableMaker conditions:
      ```
      number_of_conditions: Number of conditions
      Conditioni: Column name of conditioni (i: condition numeration)
      Valuei : Chosen value for conditioni (i: value numeration)
      ```
      In this section, as many conditions as desired can be specified. The condition should serve as a header in the input file, indicating the parameter to be associated with the desired value.

- **Output:**
  - **PDMTableMaker output** (default suffix: "PDM"), that contains the following columns:
    ```
    p: peptide
    pdm: peptidoform defined by peptide sequence, Δmass, and position (e.g., ABCD[xxx]EFGHK).
    pd: peptide sequence (includes a set of pdm elements).
    d: modification (Δmass)
    m: position in peptide (C-Terminus = -1, N-Terminus = 0)
    l: position in peptide, from right to left (C-Terminus = 0, N-Terminus = -1)
    n: position in protein. Contains all `n` if the peptide appears several times in the sequence.
    first_n: first occurrence of `n` in the protein.
    b: position of the first residue of the peptide in the protein. Contains all `b`.
    first_b: position of the first residue of the peptide in the protein (first occurrence).
    e: position of the last residue of the peptide in the protein. Contains all `e`.
    a: modified residue.
    q: protein.
    M: razor `m`, property of the pdm with the highest PSM frequency.
    L: razor `l`, corresponds with razor `m`.
    N: razor `n`, corresponds with razor `m`.
    A: razor `a`, corresponds with razor `m`.
    qdna: information of `q`, `d`, `n`, and `a` (e.g., HPT: Δmass:300:M).
    qdNA: razor qdna, property of a pd.
    Theo_mh: theoretical mh.
    ScanFreq: count of PSMs for each pdm.
    k: minimum cluster of `qna` elements contained in overlapping peptides.
    c: minimum cluster of peptide elements contained in overlapping peptides.
    qFreq: count of PSMs for each protein.
    pFreq: count of PSMs for each peptide.
    qK: `q` and `k` concatenation.
    qc: `q` and `c` concatenation.
    qKFreq: count of PSMs for each qk.
    qcFreq: count of PSMs for each qc.
    qdnaFreq: count of PSMs for each qdna.
    qnaFreq: count of PSMs for each qna.
    BestScanID: identifier of the best-scored scan.
    MissingCleavages: number of missing cleavages calculated by trunkSolver for each pdm.
    Truncation_output_column_name: contains 0 if there is no truncation and 1 if there is a truncation (previously obtained by TrunkSolver).
    ```
  - Log file (default suffix: "PDM_logFile").


[Go to top](#modules)
___


### 2. GroupMaker

GroupMaker is a module developed with the purpose of grouping information to enhance the interpretation of results in subsequent quantification. In this manner, GroupMaker forms groups as long as they meet all the specified criteria outlined in an input table created by the user and based on the SiteListMaker output table. If one of the conditions is numerical, a relative error will be computed. If it surpasses the user-defined error threshold, the condition will be deemed valid. To do so, the relative error will be calculated:

```
Relative_error(ppm) = abs((Δmass_user_selection − Δmass_of_pdm) * 1000000 / (Theoretical_mh + Δmass_user_selection))
```

- **Input:**
  - `.tsv` file
  - Configuration file:
    - GroupMaker parameters:
      ```
      Relative_Error: relative error.
      Output_file_suffix: chosen suffix for output file.
      Theo_mh_column_name: theoretical mh column name.
      Decnum: decimal points required if the group is numerical.
      ```
  - GroupMaker user input table: This table will be composed of as many columns as there are desired conditions. The column headers of this table must match those of the input `.tsv` file. If the information in each column matches, a group will be created; otherwise, the group column will remain empty. In the case where a condition is numerical, it will be checked against the user-defined threshold as absolute error. The last column in this table will be the group column, and in the output file, a new column with the same name will record the different groups.

- **Output:**
  - **GroupMaker output** (default suffix: "GM"). New columns:
    ```
    Group_output: this column contains the group.
    ```

  - Log file (default suffix: "GM_logFile").


[Go to top](#modules)
___


### 3. Joiner

Joiner is a module that joins the labels of the columns indicated by the user without repetitions.

- **Input:**
  - `.tsv` file
  - Configuration file (`.ini`): There is a default `.ini` in the “config” folder:
    - Joiner parameters:
      ```
      Output_column_name: output column name in which all labels will be joined.
      Output_file_suffix: chosen suffix for output file.
      Decnum: decimal points required if Δmass is one of the parameters.
      group_column_name: column name that contains the group name.
      Non_modified_name: parameter that indicates how unmodified peptidoforms are named.
      ```
    - Joiner columns: Use `;` to select the columns Joiner must join if the first column is empty. Example:
      ```
      1 = p
      2 = g;d
      3 = m
      ```

- **Output:**
  - **Joiner output** (default suffix: "Joined"). New columns:
    ```
    Output_column_name: this column contains all the labels of the columns indicated by the user, without repetitions.
    ```

  - Log file (default suffix: "Joined_logFile").


[Go to top](#modules)
___

