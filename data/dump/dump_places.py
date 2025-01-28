import time
from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
# from qwikidata.utils import dump_entities_to_json
# from qwikidata.linked_data_interface import get_entity_dict_from_api
import json
import pickledb as p

#.................................
import os, sys
from IPython.core.ultratb import ColorTB
import yaml

sys.excepthook = ColorTB()

WKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH_CFG = './config.yml'

sys.path.append(WKSPACE)
PATH_CFG = os.path.join(WKSPACE, PATH_CFG)

with open(PATH_CFG, 'r') as file:
    PARAMS = yaml.safe_load(file)
#.................................

"""
This function reads the wikidata and exports into a database and JSON:
(key=entity.entity_id, val=[(educated_list), (work_list)])
"""

################################################################################
# USER PARAMS
################################################################################

# # Input
# wjd_dump_path = "wikidata-20210517-all.json.bz2"
# lang = 'en'

# # Output
# path_places_db = 'places.db'
# path_output_json = 'places.json'

# Input
wjd_dump_path = PARAMS["path"]["wjd_dump_path"]
lang = PARAMS['search']['lang']

# Output
path_places_db = PARAMS['path']['db_places']
path_output_json = PARAMS['path']['json_places']


################################################################################

def is_in_Germay(entity):
    try:
        claim_group = entity.get_truthy_claim_group('P17')
        claim = claim_group[0]
        qid = claim.mainsnak.datavalue.value['id']
        if qid == 'Q183':
            return True
        else:
            return False
    except:
        return False

################################################################################

def create_item(entity):
    #instance of
    instance_of = []
    try:
        claim_group_P31 = entity.get_truthy_claim_group('P31')
        for c in claim_group_P31:
            qid = c.mainsnak.datavalue.value['id']
            instance_of.append(qid)
    except:
        pass

    #located in adminastrative territorial entity
    try:
        claim_group_P131 = entity.get_truthy_claim_group('P131')
        qid_p131 = claim_group_P131[0].mainsnak.datavalue.value['id']
    except:
        qid_p131 = ''

    # create (key,value)-pair
    # key is the entity ID
    # value is entity label, all 'instance of' properties and 'located in' property
    key = entity.entity_id
    value=[
        (entity.get_label(lang=lang)),
        instance_of,
        (qid_p131)
    ]
    return (key,value)

################################################################################

if __name__ == "__main__":

    # Create an instance of WikidataJsonDump
    wjd = WikidataJsonDump(wjd_dump_path)

    # Load the orte database
    db = p.load(path_places_db, False)

    # Create an iterable of WikidataItem
    results = []
    t1 = time.time()

    for ii, entity_dict in enumerate(wjd):
        if entity_dict["type"] == "item":
            entity = WikidataItem(entity_dict)
            if is_in_Germay(entity) == True:
                res = create_item(entity)       # (key=entity.entity_id, value=[(entity.get_label(lang='en')), instance_of, (qid_p131)])
                results.append(res)
                db.set(res[0],res[1])
            else:
                pass

        if ii % 10000 == 0:
            t2 = time.time()
            dt = t2 - t1
            print(
            len(results),ii,dt
            )

    # First export as a database
    db.dump()

    # Second export as a JSON
    x = json.dumps(results,indent=4)
    with open(path_output_json,'w') as output:
        output.write(x)

