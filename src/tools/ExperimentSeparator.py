# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 10:32:39 2021

@author: Andrea
"""

# Module metadata variables
__author__ = "Andrea Laguillo Gómez"
__credits__ = ["Andrea Laguillo Gómez", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.3.0"
__maintainer__ = "Andrea Laguillo Gómez"
__email__ = "jmrodriguezc@cnic.es;andrea.laguillo@cnic.es"
__status__ = "Development"

import argparse
import logging
import os
import pandas as pd
from pathlib import Path
import sys

def main(args):
    '''
    Main function
    '''
    # Main variables
    logging.info('Read input file...')
    df = pd.read_csv(args.infile, sep="\t", float_precision='high', low_memory=False)

    logging.info('Prepare workspace...')
    if args.output:
        group_path = args.output
    else:
        group_path = os.path.dirname(args.infile)
    if not os.path.exists(group_path):
        os.makedirs(group_path)

    logging.info(f"Write output files grouping by {args.column}:")        
    dfs = df.groupby(str(args.column))
    for group, group_df in dfs:
        if group == 'N/A':
            outfile = os.path.join(group_path, Path(args.infile).stem + '_Unassigned_FDR.tsv')
        else:
            outfile = os.path.join(group_path, Path(args.infile).stem + '_' + str(group) + '_FDR.tsv')
        
        logging.info('\t' + str(group) + ': ' + str(outfile))
        # Write the group to a file without duplicating headers
        group_df.to_csv(outfile, index=False, sep='\t', encoding='utf-8')
        


if __name__ == '__main__':

    # multiprocessing.freeze_support()

    # parse arguments
    parser = argparse.ArgumentParser(
        description='Split the file into Experiment values',
        epilog='''
        Example:
            python EXperimentSeparator.py

        ''')
    
    parser.add_argument('-i',  '--infile', required=True, help='Input file with the peak assignation')
    parser.add_argument('-c',  '--column', required=False, default='Experiment', help='Name of column to separate by')
    parser.add_argument('-o',  '--output', required=False, help='Output directory. Will be created if it does not exist')
   
    parser.add_argument('-v', dest='verbose', action='store_true', help="Increase output verbosity")
    args = parser.parse_args()
    
    created = 0
    try:
        if not os.path.exists(args.output):
            os.makedirs(args.output)
            created = 1
    except OSError:
        sys.exit("Could not create output directory at %s" % args.output)

    # logging debug level. By default, info level
    #log_file = args.infile[:-4] + '_FDR_log.txt'
    log_file = os.path.join(args.output, args.infile.split('\\')[-1].split('/')[-1][:-4] + '_FDR_log.txt')
    log_file_debug = os.path.join(args.output, args.infile.split('\\')[-1].split('/')[-1][:-4] + '_FDR_log_debug.txt')
    #log_file_debug = args.infile[:-4] + '_FDR_log_debug.txt'
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

    # start main function
    logging.info('start script: '+"{0}".format(" ".join([x for x in sys.argv])))
    if created == 1:
        logging.info("Created output directory at %s " % args.output)
    main(args)
    logging.info('end script')