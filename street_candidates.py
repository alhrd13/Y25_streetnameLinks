
'''
------------------
Original comment:
Create street-candidate-pairs for streets in Bremen or Nordrhein-Westfalen
You can user other files as long as the csv data has the correct format
Additionally, you can generate candidates only for streets that have a Wikidata Etymology attribute

------------------
Additional comments:
This function takes a CSV file with two compulsory columns (name, district) and one optionally column (etymology_wikidata).
Name should be the root of each street (Batman for John Batman Street). The function extracts in the one hot vector all 
the characteristics related to this name in wikidata; for each street, N candidates from wiki wikidata are extracted.
The resulting CSV file can then be processed with a random forest classifier for each candidate, and we can select the top K answers.

The input CSV file is created from OSM in the original paper (as we have the pair street-origin). However, It is possible
to create our own CSV file manually and to evaluate manually.
'''

import os
import pandas
import pickledb
import json
import re
from shapely import geometry
import sys

#.................................
import os, sys
from IPython.core.ultratb import ColorTB
import yaml

sys.excepthook = ColorTB()

WKSPACE = os.path.dirname(os.path.abspath(__file__))
PATH_CFG = './config.yml'

sys.path.append(WKSPACE)
PATH_CFG = os.path.join(WKSPACE, PATH_CFG)

with open(PATH_CFG, 'r') as file:
    PARAMS = yaml.safe_load(file)
#.................................

from data.wikidata import candidates

#---------------------------------

# Import
path_named_location = PARAMS['path']['named_location']
    # Columns must contain: name, district
    # Columns optionnaly contain: etymology_wikidata
    # All other column is useless

# Export
path_street_candidates = PARAMS['path']['street_candidates']

do_etymology_only = False
max_candidates = PARAMS['predict']['max_cand']

################################################################################

if __name__ == "__main__":

    #---------------------------------
    print('Begin loading necessary files')
    #---------------------------------

    arg = sys.argv
    # try:
    #     if arg[1] == "bremen":
    #         df_data = pandas.read_csv(WKSPACE + '/data/osm/named_bremen.csv')
    #     elif arg[1] == "nrw":
    #         df_data = pandas.read_csv(WKSPACE +'/data/osm/named_nrw.csv')
    #     else:
    #         df_data = pandas.read_csv(arg[1])
    # except:
    #     print('Please select an option [bremen | nrw] or one of your own files')
    #     exit()
    df_data = pandas.read_csv(path_named_location)

    with open(PARAMS['path']['json_suffix'], encoding='utf-8') as file:
        suffix = json.load(file)
    with open(PARAMS['path']['json_prefix'], encoding='utf-8') as file:
        prefix = json.load(file)

    path = PARAMS['path']['tsv_links']
    links = pandas.read_csv(path,sep='\t',index_col=0)

    path = PARAMS['path']['db_new_index']
    index = pickledb.load(path, False)

    path = PARAMS['path']['db_all_new_places'] 
    person_places = pickledb.load(path, False)

    # places = pickledb.load(ROOT_DIR + '/data/wikidata/places02.db', False)
    path = PARAMS['path']['db_all_new_places'] 
    places = pickledb.load(path, False)                   # Not present

    path = PARAMS['path']['db_all_new_occs'] 
    occDB = pickledb.load(path, False)

    #---------------------------------
    print('Begin extracting features')
    #---------------------------------

    feature_list = [
        'street','candidate','correct','link_count','full','first','last','alias',
        'occ1','occ2','occ3','occ4','occ5','occ6','occ7','occ8','occ9','occ10','occ11','occ12','occ13','occ14','occ15','occ16','occ17','occ18','occ19','occ20',
        'rel_born','rel_died','rel_buried','rel_edu','rel_work', 'district',
    ]

    # Avoid redundant streets
    df_data = df_data.drop_duplicates(subset=['name','district'])

    # try:
    #     if arg[2] == 'etymology_only':
    #         df_data = df_data.dropna(axis=0,subset=['etymology_wikidata'])
    #     else:
    #         print('Did you mean "etymology only" as your second argument?')
    # except:
    #     pass

    # Only keep streets with an etymology
    if do_etymology_only:
        df_data = df_data.dropna(axis=0,subset=['etymology_wikidata'])

    df_data = df_data.reset_index()

    new_df = pandas.DataFrame(
        index=range(len(df_data) * max_candidates),
        columns=feature_list,
    )
    df_counter = 0

    # For each street that we want to retrieve the candidate
    for t,i in enumerate(df_data.name):

        # We extract the list of potential candidates from our database
        candidate_list = candidates.get_candidates(i,prefix,suffix,links,index)
        
        if candidate_list == False:
            continue
        
        if len(candidate_list) > max_candidates:
            candidate_list = candidates.get_max_N(
                candidate_list,
                links,
                N=max_candidates,
            )

        street_hier = candidates.get_hierarchy(df_data.district.iloc[t], places)
        curr_district = df_data.district.iloc[t]

        # For each candidate, we extract the vector that corresponds to the characteristics of the candidate
        for c in candidate_list:
            try:
                count = int(links.loc[c[0]][1])
            except:
                count = 0

            name_list = candidates.get_names(c)
            occs_list = candidates.get_occupations(c[0], occDB)
            rel_list = candidates.get_candidate_relations(street_hier, c[0], places, person_places)

            row = [i,c[0],df_data['etymology_wikidata'].iloc[t],count]
            row.extend(name_list)
            row.extend(occs_list)
            row.extend(rel_list)
            row.append(curr_district)

            new_df.iloc[df_counter] = row
            df_counter += 1

    print(new_df.head())

    new_df = new_df.dropna(axis=0,how='all')

    with open(path_street_candidates,'w') as output:
        new_df.to_csv(output,header=True,index=False)


