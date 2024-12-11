import pandas as pd
import argparse

# Module metadata variables
__author__ = "Victor M. Guerrero-Sanchez"
__credits__ = ["Victor M. Guerrero-Sanchez", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.0.1"
__maintainer__ = "Jose Rodriguez"
__email__ = "vmguerrero@cnic.es;jmrodriguezc@cnic.es"
__status__ = "Development"

def main(input_file, output_file_pdm, output_file_pgm):

    df = pd.read_csv(input_file, sep="\t", low_memory=False)

    df['pgmFreq'] = df.groupby('pgm')['ScanFreq'].transform('sum')

    #PDM table
    df.to_csv(output_file_pdm, index=False, sep='\t', encoding='utf-8')

    #PGM table
    df = df.drop(columns=['pdm', 'pd', 'ScanFreq', 'qdna', 'qna', 'qdnaFreq', 'qnaFreq'])
    df = df.drop_duplicates('pgm', keep='first')
    df.to_csv(output_file_pgm, index=False, sep='\t', encoding='utf-8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate pgm frequencies and generate PDM and PGM tables", epilog="Example usage: python PGM_Processor.py input_file.tsv output_pdm_file output_pgm_file")
    parser.add_argument("-i", "--input_file", help="Input PDM Table")
    parser.add_argument("-od", "--output_pdm", help="Output PDM Table with pgmFreq", default="PDM_Table_pgmFreq.tsv")
    parser.add_argument("-og", "--output_pgm", help="Output PGM Table with pgmFreq", default="PGM_Table_pgmFreq.tsv")
    args = parser.parse_args()

    main(args.input_file, args.output_pdm, args.output_pgm)
