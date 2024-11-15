#!/usr/bin/python

# -*- coding: utf-8 -*-

# Module metadata variables
__author__ = "Andrea Laguillo Gómez"
__credits__ = ["Andrea Laguillo Gómez", "Ana Martínez del Val", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.3.0"
__maintainer__ = "Jose Rodriguez"
__email__ = "andrea.laguillo@cnic.es;jmrodriguezc@cnic.es"
__status__ = "Development"

#########################
# Import local packages #
#########################
import os
import sys
import argparse
import logging
import glob
import pandas as pd
import math
import re
from pathlib import Path


#############
# Constants #
#############
SPECTRUM_FILE_NAME = 'Spectrum_File'
SCANID_NAME = 'ScanID'


###################
# Parse arguments #
###################

# Parse arguments
parser = argparse.ArgumentParser(
    description='''
    SHIFTSadapter: A tool for adapting search engine results.

    This tool processes the results from both the Comet-PTM and MSFragger search engines.
    For MSFragger inputs, it calculates the left/right positions of modifications.
    In both cases, a 'Spectrum_File' column is added.
    ''',
    epilog='''
    Example:
        python SHIFTSadapter.py -i path/to/input/file -o path/to/output/directory

    Notes:
        - Ensure that the input file follows the SHIFTS format.
        - If no output directory is specified, the current directory is used by default.
        - Use the -v flag to see detailed logging output for troubleshooting.

    For further assistance, please refer to the documentation or contact support.
    ''')

parser.add_argument('-i', '--infile', required=True, help='Path to input file')
parser.add_argument('-o', '--outdir', help='Output dir')

parser.add_argument('-v', dest='verbose', action='store_true', help='Increase output verbosity')
args = parser.parse_args()

# getting input parameters
ifile = args.infile

# get the output file
# if output directory is not defined, get the folder from given file
# get the base name of the input file
# construct output file path with "_XXX" appended to the filename
# log files
outdir = args.outdir if args.outdir else os.path.dirname(ifile)
basename = os.path.splitext(os.path.basename(ifile))[0]
ofile = os.path.join(outdir, f"{basename}_SHIFTS.feather")
log_file = os.path.join(outdir, "SHIFTSadapter_log.txt")
log_file_debug = os.path.join(outdir, f"SHIFTSadapter_log_debug.txt")

if args.verbose:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        handlers=[logging.FileHandler(log_file_debug),
                                    logging.StreamHandler()])
else:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        handlers=[logging.FileHandler(log_file),
                                    logging.StreamHandler()])


###################
# Local functions #
###################

# Function to find positions
def msf_pos(x):
    if re.search('[a-z]', x):
        pos = [i for i, c in enumerate(x) if c.islower()]
        aa = [x[p].upper() for p in pos]
        pos2 = [f"{a}{p}" for a, p in zip(aa, pos)]
        pos3 = ";".join(pos2)
    else:
        pos = len(x)
        pos3 = f"_{pos}"
    return pos3

def preprocessing_msfragger(input_df):

    # Process file
    logging.info("Calculating precursor_MH and precursor_MZ...")
    input_df['precursor_MH'] = (input_df.precursor_neutral_mass + 1.007276)
    input_df['precursor_MZ'] = (input_df.precursor_MH + (input_df.charge-1)*1.007276) / input_df.charge

    logging.info("Filling 'best_locs' where NaN values are present...")
    input_df['best_locs'] = input_df.apply(lambda row: row['peptide'] if pd.isna(row['best_locs']) else row['best_locs'], axis=1)

    logging.info("Applying msf_pos function to find modification sites...")
    input_df['m_MSF_positions'] = input_df['best_locs'].apply(msf_pos)

    logging.info("Selecting the modification site (center of aa distribution if multiple)...")
    input_df['m_MSF'] = input_df.apply(lambda row: row['m_MSF_positions'].split(";")[math.ceil(len(row['m_MSF_positions'].split(";"))/2)-1] if len(row['m_MSF_positions'].split(";"))>1 else row['m_MSF_positions'], axis=1)
    input_df['m_MSF'] = input_df['m_MSF'].str[1:].astype(int) + 1

    logging.info("Calculating left and right positions of modification...")
    input_df['m_MSF_left'] = input_df.apply(lambda row: len(row['m_MSF_positions'].split(";"))-(len(row['m_MSF_positions'].split(";"))-math.ceil(len(row['m_MSF_positions'].split(";"))/2))-1 if len(row['m_MSF_positions'].split(";"))>1 else 0, axis=1)
    input_df['m_MSF_right'] = input_df.apply(lambda row: len(row['m_MSF_positions'].split(";"))-math.ceil(len(row['m_MSF_positions'].split(";"))/2) if len(row['m_MSF_positions'].split(";"))>1 else 0, axis=1)

    logging.info("Updating 'delta_peptide' column based on positions...")
    input_df['delta_peptide'] = input_df['peptide']

    # Vectorized update of delta_peptide column
    logging.info("Updating peptides where modifications involve mass differences...")
    mask = input_df['m_MSF_positions'].str.contains('_')
    input_df.loc[mask, 'delta_peptide'] = input_df.loc[mask, 'peptide'] + '_' + input_df.loc[mask, 'massdiff'].astype(str)
    non_mask = ~mask
    input_df.loc[non_mask, 'delta_peptide'] = input_df.loc[non_mask].apply(
        lambda row: row['delta_peptide'][:row['m_MSF']] + f"[{row['massdiff']}]" + row['delta_peptide'][row['m_MSF']:], axis=1
    )

    return input_df

# Generate the Scan ID from the Spectrum File and the provided parameters
def add_scanId(df, ifile, ids):

    # add the file name without extension into 'Raw' column
    if SPECTRUM_FILE_NAME not in df.columns:
        df[SPECTRUM_FILE_NAME] = '.'.join(os.path.basename(Path(ifile)).split(".")[:-1])
        
    # generate the scan id from the spectrum file and the given parameters
    if SCANID_NAME not in df.columns:
        # validate that all columns in 'ids' exist in the DataFrame
        missing_columns = [col for col in ids if col not in df.columns]
        if missing_columns:
            logging.error(f"Missing columns in the input file: {', '.join(missing_columns)}")
            raise ValueError(f"Missing columns: {', '.join(missing_columns)}")
        # combine the specified columns to create the ScanID
        df[SCANID_NAME] = df[[SPECTRUM_FILE_NAME]+ids].astype(str).agg('-'.join, axis=1)

    return df


def main(ifile, ofile):
    '''
    Main function
    '''
    # obtain the first line
    logging.info('Giving the input file ' + str(ifile))
    with open(ifile) as f:
        first_line = f.readline().strip().split('\t')
    
    # read the data depending on the type of search engine
    if 'CometVersion' in first_line[0]:
        logging.info('Reading the "comet" data file...')
        df = pd.read_csv(ifile, sep='\t', skiprows=1, float_precision='high', low_memory=False, index_col=False)
        search_engine_name = 'comet'
        ids = ['scan','charge']
    else:
        logging.info('Reading the "msfragger" data file...')
        df = pd.read_csv(ifile, sep='\t', float_precision='high', low_memory=False, index_col=False)
        search_engine_name = 'msfragger'
        ids = ['scannum','charge']
    logging.info(f"File {ifile} loaded successfully with {len(df)} rows.")


    # if applicable, generate the Scan ID from the Spectrum File and the provided parameters
    logging.info('Generating ScanID')
    df = add_scanId(df, ifile, ids)


    # process the MSFragger results
    if search_engine_name == 'msfragger':
        df = preprocessing_msfragger(df)
    
    # write file
    logging.info(f"Output file will be saved as: {ofile}")
    # df.to_csv(outfile, index=False, sep='\t', encoding='utf-8')
    df = df.reset_index(drop=True)
    df.to_feather(ofile)
        

if __name__ == '__main__':

    if '*' in ifile: # wildcard
        flist = glob.glob(ifile)
        print( flist )
        for f in flist:
            # create ofiles
            of = os.path.join( outdir, os.path.basename(f) )
            basename = os.path.splitext(os.path.basename(of))[0]
            ofile = os.path.join(outdir, f"{basename}_SHIFTS.feather")
            # start main function
            logging.info('start script: '+'{0}'.format(' '.join([x for x in sys.argv])))
            main(f, ofile)
        logging.info('end script')
    else:
        # start main function
        logging.info('start script: '+'{0}'.format(' '.join([x for x in sys.argv])))
        main(ifile, ofile)
        logging.info('end script')
