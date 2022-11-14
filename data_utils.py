import pandas as pd
import numpy as np
from collections import *
from itertools import combinations
import json, csv
from tqdm import tqdm
from matplotlib import pyplot as plt    
import seaborn as sns
import networkx as nx
import os

input_path = './data/DAC_NationalDownloadableFile.csv'
def data_preprocess(input_path: str, output_dir: str):
    '''
    :@param: input_path:   the original physician data file
    :@param: output_dir:   the output directory path
    
    - output:
        - hsptl2npi.json: 
            - key: hospital, value: set of physicians in this hospital
        -  npi2hsptl.json:
            - key: physcian id, value: set of hospitals in which the physician have worked 
        - spec2npi.json:
            - key: speciality, value: set of physicians in this speciality
        - npi2spec.json:
            - key: physcian id, value: set of specialties in which the physician specialized  
        - unweighted_hspt_spec.csv:
            - each line: npi1, npi2
            - each pair of physicians would have at least one common hospitals and at least one common specialities.
        - weighted_hspt_spec.csv:
            - each line: npi1, npi2, #commonHospital, #commonSpeciality

    '''

    hsptl2npi = defaultdict(set)  # {hospital: {physician}}
    npi2hsptl = defaultdict(set)  # {physician: {hospital}}
    spec2npi = defaultdict(set)   # {specialty: {physician}}
    npi2spec = defaultdict(set)   # {physician: {specialty}}

    print('preprocessing original data ...')
    with open(input_path,'r',encoding='ISO-8859-1') as f:
        reader = csv.reader(f)
        for i, line in tqdm(enumerate(reader)):
            if i == 0:
                continue
            npi = line[0]
            for j in range(11, 16):
                if len(line[j])>0:
                    spec2npi[line[j]].add(npi)
                    npi2spec[npi].add(line[j])
                else:
                    break
            for j in range(-13, -3, 2):
                if len(line[j])>0:
                    npi2hsptl[npi].add(line[j])
                    hsptl2npi[line[j]].add(npi)
                else:
                    break

    # save all the dict before
    print('Save dictionary ...')
    hsptl2npi_dict = {hsptl: list(npi_set) for hsptl, npi_set in hsptl2npi}
    npi2hsptl_dict = {npi: list(hsptl_set) for npi, hsptl_set in npi2hsptl}
    spec2npi_dict = {spec: list(npi_set) for spec, npi_set in spec2npi}
    npi2spec_dict = {npi: list(spec_set) for npi, spec_set in npi2spec}
    # os.path.join(output_dir, 'npi2spec.json')
    with open(os.path.join(output_dir, 'hsptl2npi.json'), 'w') as f:
        json.dump(hsptl2npi_dict, f)
    with open(os.path.join(output_dir, 'npi2hsptl.json'), 'w') as f:
        json.dump(npi2hsptl_dict, f)
    with open(os.path.join(output_dir, 'spec2npi.json'), 'w') as f:
        json.dump(spec2npi_dict, f)
    with open(os.path.join(output_dir, 'npi2spec.json'), 'w') as f:
        json.dump(npi2spec_dict, f)
    del hsptl2npi_dict, npi2hsptl_dict, spec2npi_dict, npi2spec_dict

    # output path
    print('save unweighted and weighted edges...')
    unweighted_path = os.path.join(output_dir, 'unweighted_hspt_spec.csv')  
    weighted_path = os.path.join(output_dir, 'weighted_hspt_spec.csv')
    with open(unweighted_path, 'w') as f1, open(weighted_path, 'w') as f2:
        unwght_writer = csv.writer(f1)
        wght_writer = csv.writer(f2)
    # find edge
        for hpstl, npi_set in tqdm(hsptl2npi.items()):
            for n1, n2 in combinations(npi_set,2):
                hpstl_inter = npi2hsptl[n1].intersection(npi2hsptl[n2])
                spec_inter = npi2spec[n1].intersection(npi2spec[n2])
                len_hpstl = len(hpstl_inter)
                len_spec = len(spec_inter)
                if len_hpstl>0 and len_spec>0:
                    unweighted_edge = sorted([n1, n2])
                    weighted_edge = unweighted_edge + [len_hpstl, len_spec]
                    unwght_writer.writerow(unweighted_edge)
                    wght_writer.writerow(weighted_edge)


def data_split(type: str, input_file: str, output_dir: str):
    '''
    :@param: type: 'spec' or 'hosp' 
        - which type we based on to split the data
    :@param: input_file: weighted_hspt_spec.csv file
        - the preprocessed file in which each line is a pair of physcians with number of common hospitals and number of common specialities
    :@param: output_dir
        - the output directory path

    - Output:
        - log degree plot 

    '''
    type_set = {'hosp', 'spec'}
    other_type = list(type_set-set(type))[0]

    output_part_files = [os.path.join(output_dir, f'diff_{type}_weight/{type}_edgeWeight_{i}') for i in range(5, 1, -1)]
    dir_name = os.path.dirname(output_part_files[0])
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


    with open(input_file, 'r') as f, open(output_part_files[0], 'w') as w0, open(output_part_files[1], 'w') as w1, \
         open(output_part_files[2], 'w') as w2, open(output_part_files[3], 'w') as w3:
        reader = csv.reader(f)
        writer0 = csv.writer(w0)
        writer1 = csv.writer(w1)
        writer2 = csv.writer(w2)
        writer3 = csv.writer(w3)
        for line in tqdm(reader):
            if len(line)==0:
                continue
            
            if type == 'spec':
                cur_weight = int(line[-1])
            elif type == 'hosp':
                cur_weight = int(line[-2])

            if cur_weight == 5:
                writer0.writerow(line[:2])
                writer1.writerow(line[:2])
                writer2.writerow(line[:2])
                writer3.writerow(line[:2])
            elif cur_weight == 4:
                writer1.writerow(line[:2])
                writer2.writerow(line[:2])
                writer3.writerow(line[:2])
            elif cur_weight == 3:
                writer2.writerow(line[:2])
                writer3.writerow(line[:2])
            elif cur_weight == 2:
                writer3.writerow(line[:2])

    for part_file in output_part_files:
        G = nx.read_edgelist(part_file, delimiter=',')
        degree_arr = dict(G.degree()).values()

        cnt = Counter(degree_arr) 
        plt.figure(figsize=(15,10))
        sns.scatterplot(np.log(list(cnt.keys())), np.log(list(cnt.values())))
        plt.xlabel('log degree')
        plt.ylabel('log count')
        title_name = f'Graph with edge with at least 1 common {other_type} and at least {nation_parts_files[3][-1]} common {type} \n NodeSize: {len(G.nodes)}, EdgeSize: {len(G.edges)}'
        plt.title(title_name)
        save_path = os.path.join(output_dir, title_name.split('\n')[0])
        plt.savefig(os.path.join())

        del G, degree_arr, cnt
