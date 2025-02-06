import os
import pandas
import pickledb
import json
import re
from shapely import geometry
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
from data import candidates
import time

#.................................
import os, sys
from IPython.core.ultratb import ColorTB
import yaml

sys.excepthook = ColorTB()

WKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_CFG = './config.yml'

sys.path.append(WKSPACE)
PATH_CFG = os.path.join(WKSPACE, PATH_CFG)

with open(PATH_CFG, 'r') as file:
    PARAMS = yaml.safe_load(file)
#.................................

################################################################################
# USER PARAMETERS
################################################################################

# Import
path_json_suffix = PARAMS['path']['json_suffix']
path_json_prefix = PARAMS['path']['json_prefix']
path_tsv_links = PARAMS['path']['tsv_links']
path_db_new_index = PARAMS['path']['db_new_index']
path_db_all_new_places = PARAMS['path']['db_all_new_places'] 
path_db_all_new_places02 = PARAMS['path']['db_extra'] # places = pickledb.load(ROOT_DIR + '/data/wikidata/places02.db', False)
path_json_gt = PARAMS['path']['json_gt'] 
path_db_all_new_occs = PARAMS['path']['db_all_new_occs'] 
path_db_all_new_labels = PARAMS['path']['db_all_new_labels'] 
N = PARAMS['predict']['max_cand']


# Export
# path_street_dict_db = 'street_dict.db'
data_ml = PARAMS['path']['data_ml'] 

#---------------------------------
path_json_suffix = os.path.join(
    WKSPACE,
    path_json_suffix,
)

path_json_prefix = os.path.join(
    WKSPACE,
    path_json_prefix,
)
path_tsv_links = os.path.join(
    WKSPACE,
    path_tsv_links,
)
path_db_new_index = os.path.join(
    WKSPACE,
    path_db_new_index,
)
path_db_all_new_places = os.path.join(
    WKSPACE,
    path_db_all_new_places,
)
path_db_all_new_places02 = os.path.join(
    WKSPACE,
    path_db_all_new_places02,
)
path_json_gt = os.path.join(
    WKSPACE,
    path_json_gt,
)
path_db_all_new_occs = os.path.join(
    WKSPACE,
    path_db_all_new_occs,
)
path_db_all_new_labels = os.path.join(
    WKSPACE,
    path_db_all_new_labels,
)
data_ml = os.path.join(
    WKSPACE,
    data_ml,
)

################################################################################

if __name__ == "__main__":

    t1 = time.time()
    print('Begin loading necessary files')

    # ROOT_DIR = os.path.abspath("..")

    #---------------------------------
    # Import files
    with open(path_json_suffix, 'r', encoding='utf-8') as file:
        suffix = json.load(file)

    with open(path_json_prefix, 'r', encoding='utf-8') as file:  
        prefix = json.load(file)

    links = pandas.read_csv(path_tsv_links,sep='\t',index_col=0)
    index = pickledb.load(path_db_new_index, False)

    person_places = pickledb.load(path_db_all_new_places, False)

    # places = pickledb.load(ROOT_DIR + '/data/wikidata/places02.db', False)
    places = pickledb.load(path_db_all_new_places02, False)

    with open(path_json_gt, 'r', encoding='utf-8') as file:  
        gt = json.load(file)

    occDB = pickledb.load(path_db_all_new_occs, False)

    labels = pickledb.load(path_db_all_new_labels, False)

    #---------------------------------
    # Extract the features
    t2 = time.time()
    print('Begin extracting features')

    new_df = pandas.DataFrame({
        'street': [],
        'candidate': [],
        'correct': [],
        'link_count': [],
        'full': [],
        'first': [],
        'last': [],
        'alias': [],
        'occ1': [],'occ2': [],'occ3': [],'occ4': [],'occ5': [],'occ6': [],'occ7': [],'occ8': [],'occ9': [],'occ10': [],
        'occ11': [],'occ12': [],'occ13': [],'occ14': [],'occ15': [],'occ16': [],'occ17': [],'occ18': [], 'occ19': [], 'occ20': [],
        'rel_born': [],
        'rel_died': [],
        'rel_buried': [],
        'rel_edu': [],
        'rel_work': []
    })


    feature_list = ['street','candidate','correct','link_count','full','first','last','alias',
    'occ1','occ2','occ3','occ4','occ5','occ6','occ7','occ8','occ9','occ10','occ11','occ12','occ13','occ14','occ15','occ16','occ17','occ18','occ19','occ20',
    'rel_born','rel_died','rel_buried','rel_edu','rel_work']

    # # Database that stores all the results
    # street_dict = pickledb.load(path_street_dict_db, False)

    for t,i in enumerate(gt['results']['bindings']):
        street_id = i['street']['value'].replace('http://www.wikidata.org/entity/', '')
        street_label = i['streetLabel']['value']
        candidate_id = i['person']['value'].replace('http://www.wikidata.org/entity/', '')

        candidate_list = candidates.get_candidates(
            street_label,
            prefix,
            suffix,
            # links,
            index,
        )
        if candidate_list == False:
            continue
        if len(candidate_list) > 50:
            candidate_list = candidates.get_max_N(candidate_list,links, N=N)

        correct_entity_label = labels.get(candidate_id)
        if correct_entity_label != False:
            correct_entity_id = index.get(correct_entity_label)
            if correct_entity_id != False:
                for c in correct_entity_id:
                    if c[0] == candidate_id:
                        candidate_list.append(c)
                        break


        street_hier = candidates.get_hierarchy(street_id, places)

        for c in candidate_list:
            if c[0] == candidate_id:
                correct = 1
            else:
                correct = 0
            try:
                count = int(links.loc[c[0]][1])
            except:
                count = 0

            name_list = candidates.get_names(c)
            occs_list = candidates.get_occupations(c[0], occDB)
            rel_list = candidates.get_candidate_relations(street_hier, c[0], places, person_places)

            row_dict = [{
                'street': street_id,
                'candidate': c[0],
                'correct': correct,
                'link_count': count,
                'full': name_list[0],
                'first': name_list[1],
                'last': name_list[2],
                'alias': name_list[3],
                'occ1': occs_list[0],'occ2': occs_list[1],'occ3': occs_list[2],'occ4': occs_list[3],'occ5': occs_list[4],
                'occ6': occs_list[5],'occ7': occs_list[6],'occ8': occs_list[7],'occ9': occs_list[8],'occ10': occs_list[9],
                'occ11': occs_list[10],'occ12': occs_list[11],'occ13': occs_list[12],'occ14': occs_list[13],'occ15': occs_list[14],
                'occ16': occs_list[15],'occ17': occs_list[16],'occ18': occs_list[17], 'occ19': occs_list[18], 'occ20': occs_list[19],
                'rel_born': rel_list[0],
                'rel_died': rel_list[1],
                'rel_buried': rel_list[2],
                'rel_edu': rel_list[3],
                'rel_work': rel_list[4]
            }]
            new_df = new_df.append(row_dict,ignore_index=True,sort=False)

    # Processing time
    t2 = time.time()
    print(new_df.head())
    print(t2-t1)

    #---------------------------------
    # Export
    with open(data_ml,'w') as output:
        new_df.to_csv(output,header=True,index=False)
