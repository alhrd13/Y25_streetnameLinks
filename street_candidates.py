
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

ROOT_DIR = os.getcwd()
sys.path.append(ROOT_DIR + '/data')
import candidates

print('Begin loading necessary files')

arg = sys.argv
try:
    if arg[1] == "bremen":
        df_data = pandas.read_csv(ROOT_DIR + '/data/osm/named_bremen.csv')
    elif arg[1] == "nrw":
        df_data = pandas.read_csv(ROOT_DIR +'/data/osm/named_nrw.csv')
    else:
        df_data = pandas.read_csv(arg[1])
except:
    print('Please select an option [bremen | nrw] or one of your own files')
    exit()

suffix = json.load(open(ROOT_DIR +'/data/affixes/suffixe.json',encoding='utf-8'))
prefix = json.load(open(ROOT_DIR +'/data/affixes/prefixe.json',encoding='utf-8'))
links = pandas.read_csv(ROOT_DIR +'/data/link_counts_wikidata.tsv',sep='\t', index_col=0)
index = pickledb.load(ROOT_DIR +'/data/wikidata/new_index.db', False)
person_places = pickledb.load(ROOT_DIR +'/data/wikidata/all_new_places.db', False)
places = pickledb.load(ROOT_DIR +'/data/wikidata/places02.db', False)
occDB = pickledb.load(ROOT_DIR +'/data/wikidata/all_new_occs.db', False)

print('Begin extracting features')

feature_list = ['street','candidate','correct','link_count','full','first','last','alias',
'occ1','occ2','occ3','occ4','occ5','occ6','occ7','occ8','occ9','occ10','occ11','occ12','occ13','occ14','occ15','occ16','occ17','occ18','occ19','occ20',
'rel_born','rel_died','rel_buried','rel_edu','rel_work', 'district']

df_data = df_data.drop_duplicates(subset=['name','district'])

try:
    if args[2] == 'etymology_only':
        df_data = df_data.dropna(axis=0,subset=['etymology_wikidata'])
    else:
        print('Did you mean "etymology only" as your second argument?')
except:
    pass

df_data = df_data.reset_index()

new_df = pandas.DataFrame(index=range(len(df_data*50)),columns=feature_list)
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

    break


print(new_df.head())

new_df = new_df.dropna(axis=0,how='all')

with open('street_candidates.csv','w') as output:
    new_df.to_csv(output,header=True,index=False)


