#!/usr/bin/env python
# coding: utf-8



# Module metadata variables
__author__ = "Cristina Amparo Devesa Arbiol"
__credits__ = ["Cristina Amparo Devesa Arbiol", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.0.1"
__maintainer__ = "Jose Rodriguez"
__email__ = "cristinaamparo.devesa@cnic.es;jmrodriguezc@cnic.es"
__status__ = "Development"

# Import modules
import re
import pandas as pd
from Bio import SeqIO
import math
import numpy as np
from optparse import OptionParser
import configparser
import argparse
import os
import logging
from pathlib import Path
import sys
import operator
from collections import OrderedDict  



###################
# Local functions #
###################
def readInfile(infile,cal_Dm_mh_colum_name):
    '''    
    Read input file to dataframe.
    '''
    df = pd.read_csv(infile, sep="\t",                               
    float_precision='high',low_memory=False,dtype={cal_Dm_mh_colum_name:str})
    df[cal_Dm_mh_colum_name].astype("float64").dtypes
    return df

def get_fasta_report(file):
    '''
    Create the FASTA report
    '''
    def _create_key_id(rec):
        if (rec.startswith("sp") or rec.startswith("tr") or rec.startswith("cRAP_sp")) and "|" in rec:
            return rec.split("|")[1]
        else:
            return rec
    indb = SeqIO.index(file, "fasta", key_function=_create_key_id)
    return indb




def Obtain_n (MasterProtein, dicc_fasta,clean_seq,m,npos) : 

    MasterProtein = MasterProtein.strip(" ")
    
    final_q_pos = ""
    #The fasta sequence corresponding to this identifier is saved 
    for iden in dicc_fasta:
        if MasterProtein == iden:
            result=str(dicc_fasta[iden].seq.upper()).replace("X","L")
            break
    
    

    
    pattern=re.compile(clean_seq.replace("L","l").replace("I","[IL]").replace("l","[IL]")) # Problems that may exist with leucine and isoleucine are solved
    
    dicc_seqs={}
    pos = 0
    
    # The corresponding fasta sequence is rigorously scrutinized so that no chance is missed  
    listab=[]
    listae = []
    listan = []
    while True:
        match = pattern.search(result, pos)


        if not match:
            break
        s = match.start()
        e = match.end()
        s = s+1
        if s-1 == 0:
            pos1 = 0
        else:
            pos1 = s-2
            
        try:
            p2 = result[e+1]
            pos2 = e+1
        except:
            pos2 = e
        s=s-1
        listab.append(str(s+1))
        listae.append(str(e))
        
        final_pos = s+1
        if final_q_pos == "":
            final_q_pos = str(final_pos+m-1)
            initial_q_pos = final_pos
        else: 
            final_q_pos = final_q_pos+";"+str(final_pos+m-1)
            initial_q_pos = final_pos
            
        
        pos = e #  Move forward in text for the next search


    for position in listab: 
        listan.append(str(int(position)+npos-1))

    b_e_list =  [val for pair in zip(listab, listae) for val in pair] 
    new_b_e_list = []
    for i in range(len(b_e_list)): 
        if float(i)%2 ==0: 
            new_b_e_list.append(b_e_list[i]+"-"+b_e_list[i+1])
    initial_final =";".join(new_b_e_list )
    initial = ";".join(listab)
    final = ";".join(listae)
    ns = ";".join(listan)
    multiple_n = "NO"
    if initial.find(";")!=-1:
        multiple_n = "YES"

    return initial, final, ns, multiple_n,initial_final

def ListMaker(df,seq,counts,dicc_fasta,MasterProtein):
    
    """
    ListMaker returns the frequency of the scan, the amino acid in the first position, cleaned sequence and m and l positions.
    """

    if seq.find("#")!=-1: 
        npos = 0
        clean_seq = seq[seq.find("#")+1:] # Clean sequence is obtained.
        aa = "U" # Aminoacid first position
        freq=int(counts.loc[seq]) # Frecuency of the scan
        m = 0 # Position starting from N-term
        l = -1 # Position starting from C-term
        n = 0 # Protein position
        pd = clean_seq+":"+seq[seq.find("[")+1:seq.find("]")] # Amino acid positions and DM
        dqna = seq[seq.find("[")+1:seq.find("]")]
        b = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[0] # Protein positions
        e = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[1]
        n = b 
        b_e = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[4]
        multiple_n = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[3]
        if multiple_n=="YES":
            first_b = b.split(";")[0]
            first_n = first_b
        else:
            first_b = b 
            first_n = b 
                               
    elif seq.find(":")!=-1:
        npos = 0 
        clean_seq = seq[:seq.find(":")] # Clean sequence is obtained.
        aa = "U" # Aminoacid first position
        freq=int(counts.loc[seq]) # Frecuency of the scan
        m = -1 # Position starting from N-term
        l = 0 # Position starting from C-term
        pd = clean_seq+":"+seq[seq.find(":")+1]  # peptide and DM
        n = len(clean_seq)+1 # Protein position
        dqna = seq[seq.find("[")+1:seq.find("]")]
        b = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[0] # Protein positions
        e = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[1]
        n = b 
        b_e = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[4]
        multiple_n = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[3]
        if multiple_n=="YES":
            fisrt_b = b.split(";")[0]
            first_n = first_b
        else:
            first_b = b 
            first_n = b 
                               
    elif seq.find("_") != -1 :
        clean_seq = seq[:seq.find("_")]
        npos = 0 
        aa = "U" # Aminoacid first position
        freq=int(counts.loc[seq]) # Frecuency of the scan
        m = np.nan # Position starting from N-term
        l = np.nan # Position starting from C-ter
        pd = (seq[:seq.find("_")])+":"+(seq[seq.find("_")+1:]) # Peptide and DM
        dqna = (seq[seq.find("_")+1:])
        b = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[0] # Protein positions
        e = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[1]
        n = b
        b_e = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[4]
        multiple_n = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[3]
        if multiple_n=="YES":
            first_b = b.split(";")[0]
            first_n = first_b
        else:
            first_b = b 
            first_n = b 
                                 
    else:
        clean_seq = seq[:seq.find("[")]+seq[seq.find("]")+1:] # Clean sequence is obtained.
        npos = seq.find("[")
        aa = seq[seq.find("[")-1] # Aminoacid first position
        freq=int(counts.loc[seq]) # Frecuency of the scan
        m = int(seq.find("[")) # Position starting from N-term
        l = int(len(clean_seq)-m+1) # Position starting from C-term
        pd = clean_seq+":"+seq[seq.find("[")+1:seq.find("]")] # peptide and DM
        dqna = seq[seq.find("[")+1:seq.find("]")] 
        n = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[2] # Protein positions
        b = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[0] # Protein positions
        e = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[1]
        multiple_n = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[3]
        b_e = Obtain_n(MasterProtein,dicc_fasta,clean_seq,m,npos)[4]
        if multiple_n=="YES":
            first_n = n.split(";")[0]
            first_b = b.split(";")[0]
        else:
            first_n = n 
            first_b = b 
        

    return clean_seq,seq,aa,freq,m,l,pd,n,dqna,b,e,first_b,first_n,b_e


##################
# Main functions #
##################
def main(file,infile1,fastafile):
    
    """
    Reading configuration file
    """
    import pandas as pd
    config = configparser.ConfigParser(inline_comment_prefixes='#')
    config.read(file)
    logging.info("Reading PDMTableMaker configuration file")  
    
    seq_column_name = config["PDMTableMaker_Parameters"].get("sequence_column_name") # Sequence with DM column name
    DM_column_name = config["PDMTableMaker_Parameters"].get("DM_column_name") # DM column name
    Theo_mh_column_name = config["PDMTableMaker_Parameters"].get("Theo_mh_column_name") # Theoretical column name
    MasterProtein_column_name =  config["PDMTableMaker_Parameters"].get("MasterProtein_column_name") # Master protien name column name 
    Outfile_suffix =  config["PDMTableMaker_Parameters"].get("Outfile_suffix") # Chosen suffix for output file
    nconditions =  config["PDMTableMaker_Conditions"].getint("number_of_conditions") # Number of conditions
    Missing_Cleavage_column_name =  config["PDMTableMaker_Parameters"].get("Missing_Cleavage_column_name") # Missing cleavage number column name
    Truncated_column_name =  config["PDMTableMaker_Parameters"].get("Truncated_column_name") # Truncated  column name 
    Score_column_name =  config["PDMTableMaker_Parameters"].get("Score_column_name") # Score  column name 
    Score_parameter =  config["PDMTableMaker_Parameters"].get("Score_parameter") # Score parameter column name 
    ScanID_column_name =  config["PDMTableMaker_Parameters"].get("ScanID_column_name") # ScanID  column name 
    range_position_left_column_name =  config["PDMTableMaker_Parameters"].get("range_position_left_column_name") # range_position_left_column_name
    range_position_right_column_name =  config["PDMTableMaker_Parameters"].get("range_position_right_column_name") # range_position_right_column_name


    logging.info("Processing input file")
    
    dicc_fasta = get_fasta_report(fastafile)
    nfile = 0
    output = infile1
    for file in open(infile1,"r"): 
        
        nfile = nfile+1
        file =file.strip("\n")
        if nfile == 1: 
    
            dfinitial = readInfile(file,DM_column_name) # A dataframe is created based on input file
            dfinitial
        elif nfile ==2: 
            df = pd.concat([dfinitial,readInfile(file,DM_column_name)]) 
        else:
            df = pd.concat([df,readInfile(file,DM_column_name)]) 
    
    
    if nfile == 1:
        df = dfinitial
        output = file

    counts = df[seq_column_name].value_counts() # The number of times that the species appear is saved in the variable count
    df2 = pd.DataFrame(columns=["p","pdm","q","qFreq","pFreq","pd","d","Missing_Cleavage","Truncated","best_scan","Theo_mh","ScanFreq","a","m","n","l","b","e","first_b","first_n","c","k","qdna","qna","qk","qc","qdnaFreq","qnaFreq","qkFreq","qcFreq","A","M","L","N","qdNA","m_left", "m_right"],dtype=float) # Dataframe 2 is created with the aim of 

    cont = 0
    seqlist = [] # In this list it will be saved the sequences already analyzed
    seqlist1 = [] # In this list it will be saved the sequences already analyzed
    dic_pd_M = {}
    dic_b_e = {}
    dic_b_e_mn = {}
    dic_qna_p = {}
    dic_qna_p_mn = {}
    dic_qdna_freq = {}
    dic_qna_freq = {}
    dic_q_freq = {}
    dic_p_freq = {}
    scoredic ={}
    dicc_m_left={}
    dicc_m_right={}
    for index, row in df.iterrows():

        meet = 0 
        if nconditions > 0: # if there are any conditions 
            for i in range(nconditions):
                i = i+1
                if row[config["PDMTableMaker_Conditions"].get("Condition"+str(i))] == config["PDMTableMaker_Conditions"].get("Value"+str(i)): # Each condition is checked
                    meet = meet+1

        if nconditions == meet: #If all conditions are met
            if row[seq_column_name] not in scoredic.keys():
                scoredic[row[seq_column_name]]=row[ScanID_column_name], row[Score_column_name]
            else: 
                if int(Score_parameter) == 0: 

                    if float(scoredic[row[seq_column_name]][1])> float(row[Score_column_name]):
                        scoredic[row[seq_column_name]]=row[ScanID_column_name], row[Score_column_name]

                if int(Score_parameter) == 1: 
                    if float(scoredic[row[seq_column_name]][1])< float(row[Score_column_name]):
                        scoredic[row[seq_column_name]]=row[ScanID_column_name], row[Score_column_name]
            if range_position_left_column_name=="": 

                dicc_m_left[row[seq_column_name]]=""
                dicc_m_right[row[seq_column_name]]=""
            else: 
                if  row[seq_column_name] not in seqlist1:
                    seqlist1.append(row[seq_column_name])


                    dicc_m_left[row[seq_column_name]]=row[range_position_left_column_name]
                    dicc_m_right[row[seq_column_name]]=row[range_position_right_column_name]
                else:
                    if row[range_position_left_column_name]<dicc_m_left[row[seq_column_name]]:
                        dicc_m_left[row[seq_column_name]]=row[range_position_left_column_name]
                    if row[range_position_right_column_name]<dicc_m_right[row[seq_column_name]]:
                        dicc_m_right[row[seq_column_name]]=row[range_position_right_column_name]

            if  row[seq_column_name] not in seqlist:

                seqlist.append(row[seq_column_name])
                p,seq,aa,ScanFreq,m,l,pd,n,dqna,b,e,first_b,first_n,b_e= ListMaker(df,row[seq_column_name],counts,dicc_fasta,row[MasterProtein_column_name])              
                d = float(row[DM_column_name])
                pdm = row[seq_column_name]
                qId = row[MasterProtein_column_name]

                df2.loc[cont,"p"] = p
                df2.loc[cont,"q"] = qId
                df2.loc[cont,"pdm"] = pdm
                df2.loc[cont,"pd"] = pd
                df2.loc[cont,"d"] = d
                df2.loc[cont,"a"] = aa
                df2.loc[cont,"m"] = m
                df2.loc[cont,"l"] = l
                df2.loc[cont,"n"] = n
                df2.loc[cont,"b"] = b
                df2.loc[cont,"e"] = e
                df2.loc[cont,"first_b"] = first_b
                df2.loc[cont,"first_n"] = first_n
                df2.loc[cont,"Missing_Cleavage"] = row[Missing_Cleavage_column_name]
                df2.loc[cont,"Truncated"] = row[Truncated_column_name]

                df2.loc[cont,"ScanFreq"] =  int(ScanFreq)
                df2.loc[cont,"Theo_mh"] =  row[Theo_mh_column_name]


                if row[seq_column_name].find("_")==-1: 
                    qdna = qId+":"+str(dqna)+":"+str(n)+":"+aa
                    df2.loc[cont,"qdna"] = qdna
                    qna = qId+":"+str(n)+":"+aa
                    df2.loc[cont,"qna"] = qna
                else:
                    qdna = qId+":"+str(dqna)+":"+str(n)+":"+"U"
                    df2.loc[cont,"qdna"] = qdna
                    qna = qId+":"+str(n)+":"+"U"
                    df2.loc[cont,"qna"] = qna

                cont = cont+1
                # The M and L positions with maximun ScanFreq are saved ina dictionary
                if row[seq_column_name].find("_")==-1 and row[seq_column_name].find("#")==-1 and row[seq_column_name].find(":")==-1:
                    if p not in dic_pd_M.keys():
                        dic_pd_M[p] = {}
                    if d not in dic_pd_M[p].keys():
                        dic_pd_M[p][d] = {}
                        dic_pd_M[p][d] = ScanFreq,m,l,n,qdna,qna
                    if ScanFreq > dic_pd_M[p][d][0]:
                        dic_pd_M[p][d] = ScanFreq,m,l,n,qdna,qna

                # Just one b value 
                if  b.find(";")==-1:
                    if qId not in dic_b_e.keys() : 
                        dic_b_e[qId]={}

                    if p not in dic_b_e[qId].keys() :
                        dic_b_e[qId][p]=int(b),int(e)

                # More than one b value 
                if b.find(";")!=-1:  
                    if qId not in dic_b_e_mn.keys(): 
                        dic_b_e_mn[qId]={}

                    if p not in dic_b_e_mn[qId].keys() :
                        dic_b_e_mn[qId][p]={}
                    if pdm not in dic_b_e_mn[qId][p].keys():
                        dic_b_e_mn[qId][p][pdm]=b_e


                # Just one n value 
                if n.find(";")==-1:
                    if qId not in  dic_qna_p.keys()and n.find(";")==-1:
                        dic_qna_p[qId]={}
                    if p not in  dic_qna_p[qId].keys():

                        dic_qna_p[qId][p]=""

                        dic_qna_p[qId][p]=dic_qna_p[qId][p]+str(n)
                    else:
                        dic_qna_p[qId][p]=dic_qna_p[qId][p]+","+str(n)


                # More than one n value 
                if n.find(";")!=-1:
                    if qId not in  dic_qna_p_mn.keys() and n.find(";")!=-1:
                        dic_qna_p_mn[qId]={}
                    if p not in  dic_qna_p_mn[qId].keys():

                        dic_qna_p_mn[qId][p]={}

                    if pdm not in  dic_qna_p_mn[qId][p].keys():
                        dic_qna_p_mn[qId][p][pdm]=n

                    
              

                if qId not in  dic_q_freq.keys():
                    dic_q_freq[qId]={}
                    dic_q_freq[qId]=int(ScanFreq)

                else:
                    dic_q_freq[qId]=  dic_q_freq[qId]+int(ScanFreq)


                if p not in  dic_p_freq.keys():
                    dic_p_freq[p]=int(ScanFreq)

                else:
                    dic_p_freq[p]=  dic_p_freq[p]+int(ScanFreq)

                if qdna not in  dic_qdna_freq.keys():
                    dic_qdna_freq[qdna]=int(ScanFreq)

                else:
                    dic_qdna_freq[qdna]=  dic_qdna_freq[qdna]+int(ScanFreq)
                if qna not in  dic_qna_freq.keys():
                    dic_qna_freq[qna]=int(ScanFreq)

                else:
                    dic_qna_freq[qna]=  dic_qna_freq[qna]+int(ScanFreq)
                    


    dic_qna_p_sort = {}           
    for q in dic_qna_p:
        dic_qna_p_sort[q]= {}

        
        for p in dic_qna_p[q]:
            
            listqna = dic_qna_p[q][p].split(",")
            listqna = list(map(int, listqna))
            listqna = sorted(listqna)

            longitud = len(listqna)
            if longitud ==1: 
                nb= listqna[0]
                ne = listqna[0]
            else: 
                nb = listqna[0]
                ne = listqna[longitud-1]
            dic_qna_p_sort[q][p]= nb,ne


   



    dic_qna_cluster={}
    for q in dic_qna_p_sort:
        min_nb = 2000000000
        max_ne = 0 
        lista= []

        sorted_q_b_e_qna = OrderedDict(sorted(dic_qna_p_sort[q].items(), key=lambda x: x[1]))

        p_number = 0 
        dic_qna_cluster[q]={}
        longitud = len(dic_qna_p_sort[q].values())

        number_of_p = 0
        for p in sorted_q_b_e_qna: 

            number_of_p = number_of_p+1

                
            if sorted_q_b_e_qna[p][0]<=min_nb:
                min_nb = sorted_q_b_e_qna[p][0]
                max_ne = sorted_q_b_e_qna[p][1]
                clusterb = min_nb
                clustere = max_ne
                p_number = p_number+1
                lista.append(p)
            elif sorted_q_b_e_qna[p][0]<=max_ne:
                
                p_number = p_number+1
                lista.append(p)
                
                if sorted_q_b_e_qna[p][1]>=max_ne: 
                    clustere = sorted_q_b_e_qna[p][1]
                    max_ne = sorted_q_b_e_qna[p][1]

            
            else: 
                for element in lista: 
                    dic_qna_cluster[q][element]=str(clusterb)+"_"+str(clustere)

                lista = []
                new_cluster= "yes"
                min_nb = 2000000000
                max_ne = 0
                p_number = 0
                if sorted_q_b_e_qna[p][0]<=min_nb:
                    min_nb = sorted_q_b_e_qna[p][0]
                    max_ne = sorted_q_b_e_qna[p][1]
                    clusterb = min_nb
                    clustere = max_ne
                    p_number = p_number+1
                    lista.append(p)
                if sorted_q_b_e_qna[p][0]<=max_ne:
                    p_number = p_number+1
                    lista.append(p)

                    if sorted_q_b_e_qna[p][1]>=max_ne: 
                        clustere = sorted_q_b_e_qna[p][1]
                        max_ne = sorted_q_b_e_qna[p][1]
            if number_of_p == longitud: 
                for element in lista: 
                    if clusterb ==1:
                        clusterb="1"

                    dic_qna_cluster[q][element]=str(clusterb)+"_"+str(clustere)

    dic_cluster={}
    for q in dic_b_e:
        min_b = 2000000000
        max_e = 0 
        lista= []
        #sortedDict = sorted(dic_b_e[q].values())
        sorted_q_b_e = OrderedDict(sorted(dic_b_e[q].items(), key=lambda x: x[1]))

        p_number = 0 
        dic_cluster[q]={}
        longitud = len(dic_b_e[q].values())
        number_of_p = 0
        for p in sorted_q_b_e:

            number_of_p = number_of_p+1

                
            if sorted_q_b_e[p][0]<=min_b:
                min_b = sorted_q_b_e[p][0]
                max_e = sorted_q_b_e[p][1]
                clusterb = min_b
                clustere = max_e
                p_number = p_number+1
                lista.append(p)
            elif sorted_q_b_e[p][0]<=max_e:
                p_number = p_number+1
                lista.append(p)
                
                if sorted_q_b_e[p][1]>=max_e: 
                    clustere = sorted_q_b_e[p][1]
                    max_e = sorted_q_b_e[p][1]

                    
            
            else: 
                for element in lista: 
                    dic_cluster[q][element]=str(clusterb)+"_"+str(clustere)

                lista = []
                new_cluster= "yes"
                min_b = 2000000000
                max_e = 0
                p_number = 0
                if sorted_q_b_e[p][0]<=min_b:
                    min_b = sorted_q_b_e[p][0]
                    max_e = sorted_q_b_e[p][1]
                    clusterb = min_b
                    clustere = max_e
                    p_number = p_number+1
                    lista.append(p)
                if sorted_q_b_e[p][0]<=max_e:
                    p_number = p_number+1
                    lista.append(p)

                    if sorted_q_b_e[p][1]>=max_e: 
                        clustere = sorted_q_b_e[p][1]
                        max_e = sorted_q_b_e[p][1]
            if number_of_p == longitud: 
                for element in lista: 
                    if clusterb ==1:
                        clusterb="1"

                    dic_cluster[q][element]=str(clusterb)+"_"+str(clustere)

                
    dic_qk_freq = {}
    dic_qc_freq = {}
    cont2 = 0
    for index, row in df2.iterrows(): # A M and  L columns are added 
        d = row["d"] 
        if row["a"]=="U":
            df2.loc[cont2,"m_right"]= 0
            df2.loc[cont2,"m_left"]= 0
        else:
            df2.loc[cont2,"m_right"]= dicc_m_right[row["pdm"]]
            df2.loc[cont2,"m_left"]= dicc_m_left[row["pdm"]]
        try:

        
            if row["b"].find(";")!=-1: 

                c = dic_b_e_mn[row["q"]][row["p"]][row["pdm"]]
            else: 

                c = dic_cluster[row["q"]][row["p"]]


            df2.loc[cont2,"c"]= c.replace("ene","1")
            qc = row["q"]+":"+c 
            df2.loc[cont2,"qc"]= qc



        
            if row["n"].find(";")!=-1: 

                k = dic_qna_p_mn[row["q"]][row["p"]][row["pdm"]]
            else: 

                k = dic_qna_cluster[row["q"]][row["p"]]


            df2.loc[cont2,"k"]= k
            qk = row["q"]+":"+k
            df2.loc[cont2,"qk"]= qk

            if qk not in  dic_qk_freq.keys():
                dic_qk_freq[qk]=row["ScanFreq"]


            else:
                 dic_qk_freq[qk]=dic_qk_freq[qk]+row["ScanFreq"]


            if qc not in  dic_qc_freq.keys():
                dic_qc_freq[qc]=row["ScanFreq"]


            else:
                 dic_qc_freq[qc]=dic_qc_freq[qc]+row["ScanFreq"]

            df2.loc[cont2,"qdnaFreq"]= dic_qdna_freq[row["qdna"]]
            df2.loc[cont2,"qnaFreq"]= dic_qna_freq[row["qna"]]
            df2.loc[cont2,"qFreq"]=  dic_q_freq[row["q"]]
            df2.loc[cont2,"pFreq"]= dic_p_freq[row["p"]]

 
           
            if row["pdm"].find("_") == -1:
                M = dic_pd_M[row["p"]][row["d"]][1]
                L = dic_pd_M[row["p"]][row["d"]][2]
                N = dic_pd_M[row["p"]][row["d"]][3]
                qdNA = dic_pd_M[row["p"]][row["d"]][4]
                qNA = dic_pd_M[row["p"]][row["d"]][5]
                
      
                df2.loc[cont2,"M"] = M
                df2.loc[cont2,"A"]=row["p"][M-1]
                df2.loc[cont2,"L"]= L
                df2.loc[cont2,"N"]= N
                df2.loc[cont2,"qdNA"]= qdNA
                df2.loc[cont2,"qNA"]= qNA

	
        
            else:
                df2.loc[cont2,"M"] = np.nan
                df2.loc[cont2,"A"] = "U"
                df2.loc[cont2,"L"] = np.nan
                df2.loc[cont2,"N"]= np.nan
                df2.loc[cont2,"qdNA"]= row["q"]+":"+str(round(row["d"],6))+"::"+"U"
                df2.loc[cont2,"qNA"]= row["q"]+"::"+"U"
            cont2 = cont2+1
        except: 
            pass

    cont3 = 0
    for index, row in df2.iterrows():
        try:
      
            df2.loc[cont3,"best_scan"]= scoredic[row["pdm"]][0]
            df2.loc[cont3,"qkFreq"]= dic_qk_freq[row["qk"]]
            df2.loc[cont3,"qcFreq"]= dic_qc_freq[row["qc"]]
            cont3 = cont3+1
        except: 
            pass


    logging.info("Writing output file")
    name = output[:-4]
    df2.to_csv(name+Outfile_suffix+".txt", index=False, sep='\t', encoding='utf-8')
    logging.info('end script')


if __name__ == '__main__':
    
    # multiprocessing.freeze_support()

    # parse arguments
    parser = argparse.ArgumentParser(
        description='PDMTableMaker',
        epilog='''
        Example:
            python PDMTbleMaker.py
        ''')
      
    # default DM0Solver configuration file
    defaultconfig = os.path.join(os.path.dirname(__file__), "config/Solver.ini")
    
    parser.add_argument('-i', '--infile', required=True, help='Input file with paths of the file(s) ')
    parser.add_argument('-f', '--fastafile', required=True, help='Path to input file')
    parser.add_argument('-c', '--config', default=defaultconfig, help='Path to custom config.ini file')
    parser.add_argument('-v', dest='verbose', action='store_true', help="Increase output verbosity")
    
    args = parser.parse_args()
    # logging debug level. By default, info level
    log_file = outfile = args.infile[:-4] + 'PDMTable_log.txt'
    log_file_debug = outfile = args.infile[:-4] + 'PDMTable_log_debug.txt'
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

    
    

    
    
    #start main function
    logging.info('start script: '+"{0}".format(" ".join([x for x in sys.argv])))
    

        
    main(args.config, args.infile, args.fastafile)

