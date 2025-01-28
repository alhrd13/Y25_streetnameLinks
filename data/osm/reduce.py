import json
import pickledb
import os
import re
import pandas

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
# PARAMS USER
################################################################################

# # Input: obtained with `districts_bremen.py`
# path_csv_test = 'test.csv'

# path_suffix_json = '/home/gurtovoy/new_suffixe/suffixe_final.json'
# path_titels_json = '/home/gurtovoy/new_suffixe/suffixe_titel.json'
# path_links_tsv = '/home/gurtovoy/data/link_counts_wikidata.tsv'
# path_person_index = '/home/gurtovoy/data/new_index.db'

# # Output
# path_named_bremen = 'named_bremen.csv'

# # Manually completed affixes in `./data/affixes``

#.................................

# Input: obtained with `districts_bremen.py`
path_csv_test = PARAMS['path']['tsv_test']          # TODO: csv

path_suffix_json = PARAMS['path']['json_suffix']
path_titels_json = PARAMS['path']['titles_json']
path_links_tsv = PARAMS['path']['tsv_links']
path_person_index = PARAMS['path']['db_new_index_person']

# Output
path_named_bremen = PARAMS['path']['csv_named_location']

# Manually completed affixes in `./data/affixes``


################################################################################

if __name__ == "__main__":
    
    ################################################################################
    # Reading the data
    ################################################################################
    with open(path_suffix_json, 'r', encoding="utf-8") as file:
        suffix = json.load(file)

    with open(path_titels_json, 'r', encoding="utf-8") as file:
        titels = json.load(file)


    person_index = pickledb.load(path_person_index, False)

    links = pandas.read_csv(
        path_links_tsv, 
        sep='\t', 
        index_col='Q64',
    )

    gdf = pandas.read_csv(
        path_csv_test,
        index_col=0,
    )

    ################################################################################
    # 
    ################################################################################

    new_df = pandas.DataFrame()
    

    test = []

    # For each name
    for t,i in enumerate(gdf.name):

        #---------------------------------
        # Create search term and filter it in advance
        #---------------------------------
        # Print index
        print(t)     

        #.................................
        # Name ...
        query = i

            # ... remove all the names between parenthesis and removed the right spaces
        if query.endswith(')') == True:
            extra = re.findall('\(.*\)', query)
            query = query.replace(extra[0],'').rstrip()
        
            # ... removes all the acronyms
        initials = re.findall('[A-Z]\. ',query)
        for init in initials:
            query = query.replace(init,'').rstrip().lstrip()

        #.................................
        # Remove suffixes in the search term
        for s in suffix:
            if query.endswith(s) == True:
                query = query.replace(s,'').rstrip().lstrip()
                break

        #.................................
        # Remove prefixes in the search term
        for titel in titels:
            query = query.replace(titel,'').rstrip().lstrip()

        # #.................................
        # # (Useless ?????)
        # if len(query) == 0:
        #     continue

        #---------------------------------
        # Finds the person in the database
        #---------------------------------
        #.................................
        # Attempt 1: find a person in the database
        # Popularity Ranking
        result = person_index.get(query)

        #.................................
        # Attempt 2: If necessary, add a hyphen between the last two names
        if result == False:
            backspace = query.rfind(' ')
            if backspace > -1:
                query_list = list(query)
                query_list[backspace] = '-'
                query = ''.join(query_list)
                result = person_index.get(query)

        #.................................
        # Attempt 3: If necessary, remove the last s in the name
        if result == False:
            if query.endswith('s') == True:
                query_list = list(query)
                query_list = query_list[:-1]
                query = ''.join(query_list)
                result = person_index.get(query)
                if result == False:
                    continue
            else:
                continue
        #---------------------------------
        max_nb = 0
        res = result[0][0]
        for r in result:
            try:
                qid = r[0]
                count = int(links.loc[qid][1])
                if count > max_nb:
                    res = r[0]
                    max_nb = count
            except:
                pass

        data = gdf.iloc[t]
        new_df.append(data)

    ################################################################################
    # Export
    with open(path_named_bremen,'w') as output:
        new_df.to_csv(output,header=True)
