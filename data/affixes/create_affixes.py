import os
import sys
import pickledb as p
import json

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

# # Get root directory
# ROOT_DIR = os.path.abspath("../..")
# sys.path.append(ROOT_DIR)

# Get Wikidata ground truth
#GT_PATH = os.path.join(ROOT_DIR,"/data/wikidata/wikidata_all.json")
# GT_PATH = ROOT_DIR + "/data/wikidata/wikidata_all.json"

################################################################################

# Import
GT_PATH = PARAMS['path']['json_gt']
PERSON_PATH = PARAMS['path']['db_all_new_names']
NAME_PATH = PARAMS['path']['db_name_data']

# Export
path_json_all_affixes = PARAMS['path']['json_all_affixes']

################################################################################

if __name__ == '__main__':

    with open(GT_PATH, encoding='utf-8') as fh:
        streets = json.load(fh)

    # # Get person and name database
    # PERSON_PATH = ROOT_DIR + "/data/wikidata/all_new_names.db"
    # NAME_PATH = ROOT_DIR + "/data/wikidata/name_data.db"

    personDB = p.load(PERSON_PATH, False)
    nameDB = p.load(NAME_PATH, False)

    suffixe = []

    # Loop through all streets of the ground truth
    for t,i in enumerate(streets['results']['bindings']):
        street = i['streetLabel']['value'].replace('-',' ')
        qid = i['person']['value'].replace('http://www.wikidata.org/entity/','')
        label = i['personLabel']['value']

        # Get person names and remove them from each street
        names = personDB.get(qid)
        test = []
        for n in names:
            test.extend(n)
        try:
            test.remove('')
        except:
            pass

        for t,j in enumerate(test):
            x = nameDB.get(j)
            if x != False:
                test[t] = x[0]

        last = label.split()
        test.append(label)
        test.reverse()
        test.extend(last)
        test.append(last[-1].replace('-',' '))
        for k in test:
            street = street.replace(k,'')

        street = street.rstrip().lstrip()
        try:
            street = street.split()
            suffixe.extend(street)
        except:
            suffixe.append(street)

        # Add remaining affix to affix list
    #    suffixe.append(street)

    # Remove duplicates
    suffixe = list(dict.fromkeys(suffixe))

    # Sort by length
    suffixe.sort(key=len)


    dumped = json.dumps(suffixe, indent = 4)
    with open(path_json_all_affixes,'w') as output:
        output.write(dumped)

