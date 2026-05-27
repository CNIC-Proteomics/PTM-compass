#!/usr/bin/env python
# coding: utf-8

# Module metadata variables
__author__ = "Cristina Amparo Devesa Arbiol", "Andrea Laguillo"
__credits__ = ["Cristina Amparo Devesa Arbiol", "Andrea Laguillo", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.1.0"
__maintainer__ = "Jose Rodriguez", "Andrea Laguillo"
__email__ = "cristinaamparo.devesa@cnic.es;jmrodriguezc@cnic.es;alaguillog@cnic.es"
__status__ = "Development"

# Import modules
import re
import pandas as pd
from Bio import SeqIO
import numpy as np
import configparser
import argparse
import os
import logging
import sys
from collections import OrderedDict

###################
# Local functions #
###################

def readInfile(infile, cal_Dm_mh_colum_name):
    '''    
    Read input file to dataframe.
    '''
    
    df = pd.read_csv(infile, sep="\t",
                     float_precision='high',
                     low_memory=False,
                     dtype={cal_Dm_mh_colum_name:str})
    df[cal_Dm_mh_colum_name].astype("float64").dtypes
    
    return df

def get_fasta_report(file):
    '''
    Create the FASTA report.
    ''' 
    
    def _create_key_id(rec):
        if (
            (rec.startswith("sp") or rec.startswith("tr") or
             rec.startswith("cRAP_sp")) and "|" in rec
        ):
            return rec.split("|")[1]
        else:
            return rec

    indb = SeqIO.index(file, "fasta", key_function=_create_key_id)
    
    return indb

def Obtain_n(MasterProtein, dicc_fasta, clean_seq, m, npos):

    MasterProtein = MasterProtein.strip()

    try:
        result = str(dicc_fasta[MasterProtein].seq).upper().replace("X", "L")
    except KeyError:
        return "", "", "", "NO", ""

    pattern = re.compile(
        clean_seq.replace("L", "l").replace("I", "[IL]").replace("l", "[IL]")
    )

    list_b = []
    list_e = []
    list_n = []
    b_e_parts = []
    final_q_pos = []

    for match in pattern.finditer(result):
        s = match.start()
        e = match.end()
        start_pos = s + 1
        list_b.append(start_pos)
        list_e.append(e)
        list_n.append(start_pos + npos - 1)
        b_e_parts.append(f"{start_pos}-{e}")
        final_q_pos.append(str(start_pos + m - 1))

    initial = ";".join(map(str, list_b))
    final = ";".join(map(str, list_e))
    ns = ";".join(map(str, list_n))
    initial_final = ";".join(b_e_parts)

    multiple_n = "YES" if len(list_b) > 1 else "NO"

    return initial, final, ns, multiple_n, initial_final

def ListMaker(seq, counts, dicc_fasta, master_prot):
    """
    ListMaker returns the frequency of the scan, the amino acid in the first
    position, cleaned sequence and m and l positions.
    """
    
    freq = int(counts.loc[seq])

    pos_hash = seq.find("#")
    pos_colon = seq.find(":")
    pos_underscore = seq.find("_")
    pos_lbr = seq.find("[")
    pos_rbr = seq.find("]")

    # Default values
    aa = "U"
    m = l = npos = 0

    if pos_hash != -1:
        clean_seq = seq[pos_hash + 1:]
        m, l, n = 0, -1, 0
        dqna = seq[pos_lbr + 1:pos_rbr]
        pd = f"{clean_seq}:{dqna}"

    elif pos_colon != -1:
        clean_seq = seq[:pos_colon]
        m, l = -1, 0
        dqna = seq[pos_lbr + 1:pos_rbr]
        pd = f"{clean_seq}:{seq[pos_colon + 1]}"
        n = len(clean_seq) + 1

    elif pos_underscore != -1:
        clean_seq = seq[:pos_underscore]
        m = l = np.nan
        dqna = seq[pos_underscore + 1:]
        pd = f"{clean_seq}:{dqna}"
        n = None

    else:
        clean_seq = seq[:pos_lbr] + seq[pos_rbr + 1:]
        npos = pos_lbr
        aa = seq[pos_lbr - 1]
        m = pos_lbr
        l = len(clean_seq) - m + 1
        dqna = seq[pos_lbr + 1:pos_rbr]
        pd = f"{clean_seq}:{dqna}"

    initial, final, ns, multiple_n, b_e = Obtain_n(
        master_prot, dicc_fasta, clean_seq, m, npos
    )

    if pos_hash != -1 or pos_colon != -1 or pos_underscore != -1:
        b = initial
        e = final
        n = b
    else:
        b = initial
        e = final
        n = ns

    # Multiple matches
    if multiple_n == "YES":
        first_b = b.split(";")[0]
        first_n = first_b if n == b else n.split(";")[0]
    else:
        first_b = b
        first_n = n if n != b else b

    return (
        clean_seq, seq, aa, freq, m, l, pd, n, dqna, b, e,
        first_b, first_n, b_e
    )

def qdna_qna(qId, dqna, n, aa, seq):
    if "_" not in seq:
        return (
            f"{qId}:{dqna}:{n}:{aa}",
            f"{qId}:{n}:{aa}"
        )
    else:
        return (
            f"{qId}:{dqna}:{n}:U",
            f"{qId}:{n}:U"
        )
    
def getA(df_res, mask_m_valid):
    p_arr = df_res.loc[mask_m_valid, "p"].to_numpy(dtype=object)
    m_arr = df_res.loc[mask_m_valid, "M"].to_numpy()
    idx = (m_arr - 1).astype(int)
    
    valid = (
        (m_arr >= 1) &
        (idx < np.vectorize(len)(p_arr))
    )
    
    res = np.full(len(p_arr), None, dtype=object)
    res[valid] = [s[i] for s, i in zip(p_arr[valid], idx[valid])]
    return res

def main(file, infile1, fastafile):
    config = configparser.ConfigParser(inline_comment_prefixes='#')
    config.read(file)
    logging.info("Reading PDMTableMaker configuration file")  
    
    params = "PDMTableMaker_Parameters"
    seq_column_name = config[params].get("sequence_column_name") # Seq. with DM
    DM_column_name = config[params].get("DM_column_name")
    Theo_mh_column_name = config[params].get("Theo_mh_column_name")
    MasterProtein_column_name =  config[params].get("MasterProtein_column_name")
    Outfile_suffix =  config[params].get("Outfile_suffix")
    Missing_Cleavage_column_name =  config[params].get("Missing_Cleavage_column_name")
    Truncated_column_name =  config[params].get("Truncated_column_name")
    Score_column_name =  config[params].get("Score_column_name")
    Score_parameter =  config[params].get("Score_parameter")
    ScanID_column_name =  config[params].get("ScanID_column_name")
    range_position_left_column_name =  config[params].get("range_position_left_column_name")
    range_position_right_column_name =  config[params].get("range_position_right_column_name")
    conditions = config["PDMTableMaker_Conditions"]
    nconditions =  conditions.getint("number_of_conditions")
    
    # Read fasta
    logging.info("Processing fasta file")
    dicc_fasta = get_fasta_report(fastafile)
    
    # Read table
    logging.info("Reading input file")
    with open(infile1, "r") as f:
        first_line = f.readline().strip('\n')
    if "\t" in first_line:
        # Read table
        df = readInfile(infile1, DM_column_name)
    else:
        # Read list of tables
        df = []
        with open(infile1, "r") as f:
            for i in f.readlines():
                df += [readInfile(i, DM_column_name)]
        df = pd.concat(df)
    out_name = infile1[:-4] + Outfile_suffix + ".txt"
    
    counts = df[seq_column_name].value_counts()
    
    # Filter table by conditions
    logging.info("Filtering by conditions")
    query = []
    if nconditions > 0: 
        for i in range(1, nconditions):
            query += [conditions.get("Condition" + str(i))
                      + '== "'
                      + conditions.get("Value" + str(i))
                      + '"']
        query = ' & '.join(query)
        df = df.query(query) # Should be faster for very large df
    
    logging.info("Processing")
    
    # Make score dictionary
    if int(Score_parameter) == 0: # lower = better
        df_f = df.loc[df.groupby(seq_column_name)[Score_column_name].idxmin()]
    else:  # higher = better
        df_f = df.loc[df.groupby(seq_column_name)[Score_column_name].idxmax()]
    scoredic = dict(zip(df_f[seq_column_name],
                        zip(df_f[ScanID_column_name],
                            df_f[Score_column_name])))
    
    # Make dicc_m_left and dicc_m_right dictionaries
    if range_position_left_column_name != "":
        # lower = better
        df_f = df.loc[df.groupby(seq_column_name)[range_position_left_column_name].idxmin()]
        dicc_m_left = dict(zip(df_f[seq_column_name],
                               df_f[range_position_left_column_name]))
        df_f = df.loc[df.groupby(seq_column_name)[range_position_right_column_name].idxmin()]
        dicc_m_right = dict(zip(df_f[seq_column_name],
                               df_f[range_position_right_column_name]))
    else: # keep empty
        dicc_m_left = dicc_m_right = dict(zip(df[seq_column_name].unique(),
                                              [""] * len(df)))
        
    # Make results 
    df_f = df[[seq_column_name,
               MasterProtein_column_name,
               DM_column_name,
               Missing_Cleavage_column_name,
               Truncated_column_name,
               Theo_mh_column_name]].drop_duplicates(subset=seq_column_name,
                                                     keep='first',
                                                     ignore_index=True)
    # Make: p, seq, aa, ScanFreq, m, l, pd, n, dqna, b, e, first_b, first_n, b_e
    # Make: qdna, qna
    # Add: d, Missing_Cleavage, Truncated, Theo_mh, pdm, qId
    seq_arr = df_f[seq_column_name].to_numpy()
    prot_arr = df_f[MasterProtein_column_name].to_numpy()
    d_arr = df_f[DM_column_name].to_numpy(dtype=float)
    mis_arr = df_f[Missing_Cleavage_column_name].to_numpy()
    trunc_arr = df_f[Truncated_column_name].to_numpy()
    theo_arr = df_f[Theo_mh_column_name].to_numpy()
    
    # results = [
    #     (*ListMaker(seq, counts, dicc_fasta, prot),
    #      d, mis_c, trunc, theo)
    #     for seq, prot, d, mis_c, trunc, theo in zip(
    #         seq_arr, prot_arr, d_arr, mis_arr, trunc_arr, theo_arr
    #     )
    # ]
    
    results = [
        (
            *res,
            *qdna_qna(prot, res[8], res[7], res[2], seq), #dqna, n, aa
            d, mis_c, trunc, theo, seq, prot
        )
        for seq, prot, d, mis_c, trunc, theo in zip(
            seq_arr, prot_arr, d_arr, mis_arr, trunc_arr, theo_arr
        )
        for res in [ListMaker(seq, counts, dicc_fasta, prot)]
    ]
    
    # Make results dataframe
    logging.info("Collecting results")
    cols = ["p", "seq", "a", "ScanFreq", "m", "l", "pd", "n", "dqna", "b",
            "e", "first_b", "first_n", "b_e", "qdna", "qna", "d",
            "Missing_Cleavage", "Truncated", "Theo_mh", "pdm", "q"
    ]
    df_res = pd.DataFrame(results, columns=cols)
    
    # Make dictionaries
    logging.info("Making dictionaries")
    dic_q_freq = df_res.groupby("q")["ScanFreq"].sum().to_dict()
    dic_p_freq = df_res.groupby("p")["ScanFreq"].sum().to_dict()
    
    dic_qdna_freq = df_res.groupby("qdna")["ScanFreq"].sum().to_dict()
    dic_qna_freq = df_res.groupby("qna")["ScanFreq"].sum().to_dict()
    
    df_pdM = (
        df_res[
            ~df_res["pdm"].str.contains(r"[_#:]")
        ]
        .sort_values("ScanFreq", ascending=False)
        .drop_duplicates(subset=["p", "d"])
    )
    
    # Keep entry with highest ScanFreq
    df_pdM = df_pdM.loc[df_pdM.groupby(["p", "d"])["ScanFreq"].idxmax()]
    
    dic_pd_M = {}
    
    for row in df_pdM.itertuples(index=False):
        dic_pd_M.setdefault(row.p, {})[row.d] = (
            row.ScanFreq,
            row.m,
            row.l,
            row.n,
            row.qdna,
            row.qna,
        )

    # dic_pd_M = {}
    # p_arr = df_pdM["p"].to_numpy()
    # d_arr = df_pdM["d"].to_numpy()
    # sf_arr   = df_pdM["ScanFreq"].to_numpy()
    # m_arr    = df_pdM["m"].to_numpy()
    # l_arr    = df_pdM["l"].to_numpy()
    # n_arr    = df_pdM["n"].to_numpy()
    # qdna_arr = df_pdM["qdna"].to_numpy()
    # qna_arr  = df_pdM["qna"].to_numpy()
    # for i in range(len(p_arr)):
    #     p = p_arr[i]
    #     d = d_arr[i]
    
    #     sub = dic_pd_M.get(p)
    #     if sub is None:
    #         sub = {}
    #         dic_pd_M[p] = sub
    
    #     sub[d] = (
    #         sf_arr[i],
    #         m_arr[i],
    #         l_arr[i],
    #         n_arr[i],
    #         qdna_arr[i],
    #         qna_arr[i],
    #     )

    # Make dic_b_e (just one b value)
    df_single_b = df_res[~df_res["b"].str.contains(";")]
    dic_b_e = {
        q: dict(zip(group["p"], zip(group["b"].astype(int), group["e"].astype(int))))
        for q, group in df_single_b.groupby("q")
    }
    
    # Make dic_b_e (multiple b values)
    df_multi_b = df_res[df_res["b"].str.contains(";")]
    dic_b_e_mn = {
        q: {
            p: dict(zip(group["pdm"], group["b_e"]))
            for p, group in q_group.groupby("p")
        }
        for q, q_group in df_multi_b.groupby("q")
    }
    
    # Make dic_qna_p (just one n value)
    df_single_n = df_res[~df_res["n"].str.contains(";")]
    dic_qna_p = {}
    q_arr = df_single_n["q"].to_numpy()
    p_arr = df_single_n["p"].to_numpy()
    n_arr = df_single_n["n"].to_numpy()
    for i in range(len(q_arr)):
        q = q_arr[i]
        p = p_arr[i]
        n = n_arr[i]
        sub_q = dic_qna_p.get(q)
        if sub_q is None:
            sub_q = {}
            dic_qna_p[q] = sub_q
        if p in sub_q:
            sub_q[p] += "," + str(n)
        else:
            sub_q[p] = str(n)
    
    # Make dic_qna_p_mn (multiple n values)
    df_multi_n = df_res[df_res["n"].str.contains(";")]
    dic_qna_p_mn = {}
    q_arr = df_multi_n["q"].to_numpy()
    p_arr = df_multi_n["p"].to_numpy()
    pdm_arr = df_multi_n["pdm"].to_numpy()
    n_arr = df_multi_n["n"].to_numpy()
    for i in range(len(q_arr)):
        q = q_arr[i]
        p = p_arr[i]
        sub_q = dic_qna_p_mn.get(q)
        if sub_q is None:
            sub_q = {}
            dic_qna_p_mn[q] = sub_q
        sub_p = sub_q.get(p)
        if sub_p is None:
            sub_p = {}
            sub_q[p] = sub_p
        sub_p[pdm_arr[i]] = n_arr[i]
        
    # Sort dic_qna_p
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
    
    # Make dic_qna_cluster
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
                # new_cluster= "yes"
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
                    
    # Make dic_cluster
    dic_cluster={}
    for q in dic_b_e:
        min_b = 2000000000
        max_e = 0 
        lista= []
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
                # new_cluster= "yes"
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

    # Make dic_qk_freq and dic_qc_freq
    # Add these results to df
    mask_b_multi = df_res["b"].str.contains(";", regex=False)
    mask_n_multi = df_res["n"].str.contains(";", regex=False)
    mask_pdm = df_res["pdm"].str.contains("_", regex=False)
    mask_aa = df_res["a"] == "U"
    
    df_res["m_right"] = df_res["pdm"].map(dicc_m_right).fillna(0)
    df_res["m_left"] = df_res["pdm"].map(dicc_m_left).fillna(0)
    df_res.loc[mask_aa, ["m_right", "m_left"]] = 0
    
    flat_cluster = {
        (q, p): v
        for q, inner in dic_cluster.items()
        for p, v in inner.items()
    }
    
    flat_b_e_mn = {
        (q, p, pdm): v
        for q, inner in dic_b_e_mn.items()
        for p, inner2 in inner.items()
        for pdm, v in inner2.items()
    }
    
    df_res["c"] = None
    # single b
    df_res.loc[~mask_b_multi, "c"] = [
        flat_cluster.get((q, p))
        for q, p in zip(
            df_res.loc[~mask_b_multi, "q"],
            df_res.loc[~mask_b_multi, "p"]
        )
    ]
    
    # multi b
    df_res.loc[mask_b_multi, "c"] = [
        flat_b_e_mn.get((q, p, pdm))
        for q, p, pdm in zip(
            df_res.loc[mask_b_multi, "q"],
            df_res.loc[mask_b_multi, "p"],
            df_res.loc[mask_b_multi, "pdm"]
        )
    ]
    
    df_res["c"] = df_res["c"].str.replace("ene", "1")
    df_res["qc"] = df_res["q"] + ":" + df_res["c"]
    
    flat_qna_cluster = {
        (q, p): v
        for q, inner in dic_qna_cluster.items()
        for p, v in inner.items()
    }
    
    flat_qna_p_mn = {
        (q, p, pdm): v
        for q, inner in dic_qna_p_mn.items()
        for p, inner2 in inner.items()
        for pdm, v in inner2.items()
    }
    
    df_res["k"] = None
    
    df_res.loc[~mask_n_multi, "k"] = [
        flat_qna_cluster.get((q, p))
        for q, p in zip(
            df_res.loc[~mask_n_multi, "q"],
            df_res.loc[~mask_n_multi, "p"]
        )
    ]
    
    df_res.loc[mask_n_multi, "k"] = [
        flat_qna_p_mn.get((q, p, pdm))
        for q, p, pdm in zip(
            df_res.loc[mask_n_multi, "q"],
            df_res.loc[mask_n_multi, "p"],
            df_res.loc[mask_n_multi, "pdm"]
        )
    ]
    
    df_res["qk"] = df_res["q"] + ":" + df_res["k"]
    
    df_res["qdnaFreq"] = df_res["qdna"].map(dic_qdna_freq)
    df_res["qnaFreq"] = df_res["qna"].map(dic_qna_freq)
    df_res["qFreq"]   = df_res["q"].map(dic_q_freq)
    df_res["pFreq"]   = df_res["p"].map(dic_p_freq)

    dic_qk_freq = df_res.groupby("qk")["ScanFreq"].sum().to_dict()
    dic_qc_freq = df_res.groupby("qc")["ScanFreq"].sum().to_dict()
    
    flat_pd_M = {
        (p, d): vals
        for p, inner in dic_pd_M.items()
        for d, vals in inner.items()
    }
    
    df_res["A"] = None
    df_res["M"] = np.nan
    df_res["L"] = np.nan
    df_res["N"] = None
    df_res["qdNA"] = None
    df_res["qNA"] = None
    
    mask_valid = ~mask_pdm
    
    vals = [
        flat_pd_M.get((p, d))
        for p, d in zip(
            df_res.loc[mask_valid, "p"],
            df_res.loc[mask_valid, "d"]
        )
    ]
    
    df_res.loc[mask_valid, "M"] = [v[1] if v else None for v in vals]
    df_res.loc[mask_valid, "L"] = [v[2] if v else None for v in vals]
    df_res.loc[mask_valid, "N"] = [v[3] if v else None for v in vals]
    df_res.loc[mask_valid, "qdNA"] = [v[4] if v else None for v in vals]
    df_res.loc[mask_valid, "qNA"] = [v[5] if v else None for v in vals]
    
    mask_m_valid = df_res["M"].notna()
    df_res.loc[mask_m_valid, "A"] = getA(df_res, mask_m_valid)
    
    # Default values for invalid cases
    df_res.loc[mask_pdm, "M"] = np.nan
    df_res.loc[mask_pdm, "A"] = "U"
    df_res.loc[mask_pdm, "L"] = np.nan
    df_res.loc[mask_pdm, "N"] = np.nan
    df_res.loc[mask_pdm, "qdNA"] = (
        df_res["q"] + ":" +
        df_res["d"].round(6).astype(str) +
        "::U"
    )
    df_res.loc[mask_pdm, "qNA"] = df_res["q"] + "::U"
    
    # best_scan (take first element of tuple)
    df_res["best_scan"] = df_res["pdm"].map(
        lambda x: scoredic.get(x, (None,))[0]
    )
    
    # qkFreq and qcFreq
    df_res["qkFreq"] = df_res["qk"].map(dic_qk_freq)
    df_res["qcFreq"] = df_res["qc"].map(dic_qc_freq)
    
    # cleanup
    df_res.M = df_res.M.astype(int)
    df_res.L = df_res.L.astype(int)
    df_res = df_res[[
        "p", "pdm", "q", "qFreq", "pFreq", "pd", "d", "Missing_Cleavage",
        "Truncated", "best_scan", "Theo_mh", "ScanFreq", "a", "m", "n", "l",
        "b", "e", "first_b", "first_n", "c", "k", "qdna", "qna", "qc", "qk",
        "qdnaFreq", "qnaFreq", "qkFreq", "qcFreq", "A", "M", "L", "N", "qdNA",
        "m_left", "m_right", "qNA"
        ]]
    # TODO A is empty, L and N are different by 1 sometimes, qdNA and qNA also different from joining the other ones
    
    logging.info("Writing output file")
    df_res.to_csv(out_name, index=False, sep='\t', encoding='utf-8')
    logging.info('end script')
    return

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
    defaultconfig = os.path.join(os.path.dirname(__file__),
                                 "config/Solver.ini")
    
    parser.add_argument('-i', '--infile', required=True,
                        help='Input file with paths of the file(s) ')
    parser.add_argument('-f', '--fastafile', required=True,
                        help='Path to input file')
    parser.add_argument('-c', '--config', default=defaultconfig,
                        help='Path to custom config.ini file')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help="Increase output verbosity")
    
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

