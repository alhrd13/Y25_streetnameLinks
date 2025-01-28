'''
Create name index from data that was extracted from a wikidata dump
e.g. Q463035: ['Douglas','first name']

'''

import time
import os
from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json
import json
import pickledb as p

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
################################################################################\

# # Import
# ROOT_DIR = os.path.abspath("../../")
# wjd_dump_path = os.path.join(
#     ROOT_DIR,
#     "/dump/wikidata-20210517-all.json.bz2",
# )

# # Export
# path_name_data_db = 'name_data.db'

# Import
wjd_dump_path = PARAMS["path"]["wjd_dump_path"]

# Export
path_name_data_db = PARAMS['path']['db_name_data']

################################################################################

def is_name(entity):
    try:
        claim_group = entity.get_truthy_claim_group('P31')
        claim = claim_group[0]
        qid = claim.mainsnak.datavalue.value['id']
        if qid == 'Q1243157':
            db.set(entity_dict['id'], [entity_dict['labels']['de']['value'], 'double'])
        if qid == 'Q11879590':
            db.set(entity_dict['id'], [entity_dict['labels']['de']['value'], 'first'])
        if qid == 'Q12308941':
            db.set(entity_dict['id'], [entity_dict['labels']['de']['value'], 'first'])
        if qid == 'Q101352':
            db.set(entity_dict['id'], [entity_dict['labels']['de']['value'], 'last'])
    except:
        pass

################################################################################

if __name__ == "__main__":

    # Create an instance of WikidataJsonDump
    wjd = WikidataJsonDump(wjd_dump_path)

    # Create a new database
    db = p.load(path_name_data_db, False)

    # Create an iterable of WikidataItem
    results = 0
    t1 = time.time()
    for ii, entity_dict in enumerate(wjd):
        if entity_dict["type"] == "item":
            try:
                entity = WikidataItem(entity_dict)
                is_name(entity)
            except:
                continue

        #.................................
        # Printed output for the user
        if ii % 1000 == 0:
            t2 = time.time()
            dt = t2 - t1
            print(
                "found {} humans among {} entities [entities/s: {:.2f}]".format(
                    results, ii, ii / dt
                )
            )

    # Export
    db.dump()
