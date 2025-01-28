
'''
Create street-candidate-pairs for streets in Bremen or Nordrhein-Westfalen
You can user other files as long as the csv data has the correct format
Additionally, you can generate candidates only for streets that have a Wikidata Etymology attribute
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

# Export
path_street_candidates = PARAMS['path']['street_candidates']

do_etymology_only = False

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

    feature_list = ['street','candidate','correct','link_count','full','first','last','alias',
    'occ1','occ2','occ3','occ4','occ5','occ6','occ7','occ8','occ9','occ10','occ11','occ12','occ13','occ14','occ15','occ16','occ17','occ18','occ19','occ20',
    'rel_born','rel_died','rel_buried','rel_edu','rel_work', 'district']

    df_data = df_data.drop_duplicates(subset=['name','district'])

    # try:
    #     if arg[2] == 'etymology_only':
    #         df_data = df_data.dropna(axis=0,subset=['etymology_wikidata'])
    #     else:
    #         print('Did you mean "etymology only" as your second argument?')
    # except:
    #     pass
    if do_etymology_only:
        df_data = df_data.dropna(axis=0,subset=['etymology_wikidata'])

    df_data = df_data.reset_index()

    new_df = pandas.DataFrame(index=range(len(df_data)*50),columns=feature_list)
    df_counter = 0

    for t,i in enumerate(df_data.name):
        candidate_list = candidates.get_candidates(i,prefix,suffix,links,index)
        if candidate_list == False:
            continue
        if len(candidate_list) > 50:
            candidate_list = candidates.get_max_50(candidate_list,links)

        street_hier = candidates.get_hierarchy(df_data.district.iloc[t], places)
        curr_district = df_data.district.iloc[t]

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


