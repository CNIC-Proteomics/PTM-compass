#!/usr/bin/python

# -*- coding: utf-8 -*-

# Module metadata variables
__author__ = "Andrea Laguillo Gómez"
__credits__ = ["Andrea Laguillo Gómez", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.3.0"
__maintainer__ = "Jose Rodriguez"
__email__ = "andrea.laguillo@cnic.es;jmrodriguezc@cnic.es"
__status__ = "Development"

# import modules
import argparse
import configparser
import logging
import pandas as pd
import sys
import os

def main(args):
    '''
    Main function
    '''
    # Main variables
    filename = config._sections['ScanId_Parameters']['filename']
    scan = config._sections['ScanId_Parameters']['scan']
    charge = config._sections['ScanId_Parameters']['charge']

    # Main variables
    logging.info('Reading input file')
    with open(args.infile) as f:
        first_line = f.readline().strip().split('\t')
    df = pd.read_csv(args.infile, sep='\t', skiprows=0, float_precision='high', low_memory=False, index_col=False)
    
    logging.info('Cleaning up filename')
    df[filename] = df.apply(lambda x: str(x[filename]).replace(str(args.remove), ''), axis = 1)
    
    logging.info('Generating ScanID')
    df['ScanID'] = str(df[filename]) + '-' + str(df[scan]) + '-' + str(df[charge])
    df['ScanID'] = df.apply(lambda x: str(x[filename]) + '-' +
                                      str(x[scan]) + '-' +
                                      str(x[charge]), axis = 1)
    
    logging.info('Writing output file')
    outfile = args.infile[:-4] + '_ScanID.txt'
    df.to_csv(outfile, index=False, sep='\t', encoding='utf-8')
    
    logging.info('Done')
    

if __name__ == '__main__':

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='ScanIDgenerator',
        epilog='''
        Example:
            python ScanIDgenerator.py

        ''')
    
    defaultconfig = os.path.join(os.path.dirname(__file__), "../config/ScanID.ini")

    parser.add_argument('-i', '--infile', required=True, help='Path to input file')
    parser.add_argument('-r', '--remove', required=False, default='_SHIFTS_Unique_calibrated', help='String to remove from Filename')
    parser.add_argument('-c', '--config', help='Path to custom config.ini file')

    # these will overwrite the config if specified
    parser.add_argument('-f', '--filename', default=None, help='Filename column')
    parser.add_argument('-s', '--scan', default=None, help='Scan num column')
    parser.add_argument('-a', '--charge', default=None, help='Charge column')

    parser.add_argument('-v', dest='verbose', action='store_true', help='Increase output verbosity')
    args = parser.parse_args() 

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            handlers=[logging.StreamHandler()])
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            handlers=[logging.StreamHandler()])
        
    # parse config
    config = configparser.ConfigParser(inline_comment_prefixes='#')
    config.read(args.config)
    if args.filename is not None:
        config.set('ScanId', 'filename', str(args.filename))
        config.set('Logging', 'create_ini', '1')
    if args.scan is not None:
        config.set('ScanId', 'scan', str(args.scan))
        config.set('Logging', 'create_ini', '1')
    if args.charge is not None:
        config.set('ScanId', 'charge', str(args.charge))
        config.set('Logging', 'create_ini', '1')
    # if something is changed, write a copy of ini
    if config.getint('Logging', 'create_ini') == 1:
        with open(os.path.dirname(args.infile) + '/ScanId.ini', 'w') as newconfig:
            config.write(newconfig)


    # start main function
    logging.info('start script: '+'{0}'.format(' '.join([x for x in sys.argv])))
    main(args)
    logging.info('end script')