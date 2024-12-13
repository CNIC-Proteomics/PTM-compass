import pandas as pd
import argparse
import os
import logging

# Module metadata variables
__author__ = "Victor M. Guerrero-Sanchez"
__credits__ = ["Victor M. Guerrero-Sanchez", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.0.2"
__maintainer__ = "Jose Rodriguez"
__email__ = "vmguerrero@cnic.es;jmrodriguezc@cnic.es"
__status__ = "Development"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main(input_file, output_file_pdm, output_file_pgm):
    if not os.path.exists(input_file):
        logging.error(f"Input file '{input_file}' does not exist.")
        raise FileNotFoundError(f"Input file '{input_file}' not found.")
    
    try:
        # Read the input file
        logging.info(f"Reading input file: {input_file}")
        df = pd.read_csv(input_file, sep="\t", low_memory=False)
        
        # Check if required columns exist
        required_columns = ['pgm', 'ScanFreq']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column '{col}' in the input file.")

        # Calculate 'pgmFreq'
        df['pgmFreq'] = df.groupby('pgm')['ScanFreq'].transform('sum')
        logging.info("Calculated 'pgmFreq' column.")

        # Save PDM table
        logging.info(f"Saving PDM table to: {output_file_pdm}")
        df.to_csv(output_file_pdm, index=False, sep='\t', encoding='utf-8')

        # Generate and save PGM table
        columns_to_drop = ['pdm', 'pd', 'ScanFreq', 'qdna', 'qna', 'qdnaFreq', 'qnaFreq']
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')
        df = df.drop_duplicates('pgm', keep='first')
        logging.info(f"Saving PGM table to: {output_file_pgm}")
        df.to_csv(output_file_pgm, index=False, sep='\t', encoding='utf-8')

        logging.info("Processing completed successfully.")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate pgm frequencies and generate PDM and PGM tables.",
        epilog="Example usage: python FreqProcessor.py -i input_file.tsv -od output_pdm_file -og output_pgm_file"
    )
    parser.add_argument("-i", "--input_file", required=True, help="Input PDM Table (Required)")
    parser.add_argument("-od", "--output_pdm", help="Output PDM Table with pgmFreq", default="PDM_Table_pgmFreq.tsv")
    parser.add_argument("-og", "--output_pgm", help="Output PGM Table with pgmFreq", default="PGM_Table_pgmFreq.tsv")
    args = parser.parse_args()

    try:
        main(args.input_file, args.output_pdm, args.output_pgm)
    except Exception as e:
        logging.error(f"Script execution failed: {e}")
