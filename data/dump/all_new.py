import time
from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
# from qwikidata.utils import dump_entities_to_json
# from qwikidata.linked_data_interface import get_entity_dict_from_api
# from qwiki import filtered_properties, is_person_or_street
from qwiki import is_person_or_street
# import json
import pickledb as p

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

"""
This program takes a dump of wikidata in .bz2 as input and exports it into a one hot dataset.
"""

################################################################################
# PARAMS BY USER
################################################################################

# # Input
# wjd_dump_path = "wikidata-20210517-all.json.bz2"

# # Output
# path_db_names = 'all_new_names.db'
# path_db_occs = 'all_new_occs.db'
# path_db_places = 'all_new_places.db'
# path_db_labels = 'all_new_labels.db'


# Input
wjd_dump_path = PARAMS["path"]["wjd_dump_path"]

# Output
path_db_names = PARAMS["path"]['db_all_new_names']
path_db_occs = PARAMS["path"]['db_all_new_occs']
path_db_places = PARAMS["path"]['db_all_new_places']
path_db_labels = PARAMS["path"]['db_all_new_labels']

################################################################################

def create_item(
        entity_dict,
    ):
    """For a given entity, this function extracts one hot columns associated to different characteristics encountered
    in wikidata.

    Args:
        entity_dict (_type_): _description_

    Returns: (key,value)
        (key, val)): with:
            - key = WikidataItem(entity_dict).entity_id
            - value=[[first_names, last_names, aliases],
                occs,
                [birth, death, burial, educated, work],
                label,
                ]
    """

    entity = WikidataItem(entity_dict)

    first_names = []
    last_names = []
    aliases = []
    occs = []
    birth = []
    death = []
    burial = []
    educated = []
    work = []
    label = []

    #---------------------------------
    # Names
    #---------------------------------

    #.................................
    # First name
    try:
        claim_group_P735 = entity.get_truthy_claim_group('P735')
        for c in claim_group_P735:
            first_names.append(c.mainsnak.datavalue.value['id'])
    except:
        first_names.append('')

    #.................................
    # Last names
    try:
        claim_group_P734 = entity.get_truthy_claim_group('P734')
        for c in claim_group_P734:
            last_names.append(c.mainsnak.datavalue.value['id'])
    except:
        last_names.append('')

    #.................................
    # Alias
    try:
        alias_group = entity_dict['aliases']['de']
        for c in alias_group:
            aliases.append(c['value'])
    except:
        aliases.append('')

    #.................................
    # Occupation
    try:
        claim_group_P106 = entity.get_truthy_claim_group('P106')
        for c in claim_group_P106:
            occs.append(c.mainsnak.datavalue.value['id'])
    except:
        occs.append('')

    #.................................
    # Birth place
    try:
        claim_group_P19 = entity.get_truthy_claim_group('P19')
        for c in claim_group_P19:
            birth.append(c.mainsnak.datavalue.value['id'])
    except:
        birth.append('')

    #.................................
    # Death place
    try:
        claim_group_P20 = entity.get_truthy_claim_group('P20')
        for c in claim_group_P20:
            death.append(c.mainsnak.datavalue.value['id'])
    except:
        death.append('')

    #.................................
    # Burial place
    try:
        claim_group_P119 = entity.get_truthy_claim_group('P119')
        for c in claim_group_P119:
            burial.append(c.mainsnak.datavalue.value['id'])
    except:
        burial.append('')

    #.................................
    # Education
    try:
        claim_group_P69 = entity.get_truthy_claim_group('P69')
        for c in claim_group_P69:
            educated.append(c.mainsnak.datavalue.value['id'])
    except:
        educated.append('')

    #.................................
    # Work
    try:
        claim_group_P937 = entity.get_truthy_claim_group('P937')
        for c in claim_group_P937:
            work.append(c.mainsnak.datavalue.value['id'])
    except:
        work.append('')

    #.................................
    # Label
    try:
        label.append(entity_dict['labels']['de']['value'])
    except:
        label.append('')

    #.................................
    key = entity.entity_id
    value=[[first_names, last_names, aliases],
           occs,
           [birth, death, burial, educated, work],
           label]
    return (key,value)

################################################################################

if __name__ == "__main__":

    # Load the database
    new_names = p.load(path_db_names, False)
    new_occs = p.load(path_db_occs, False)
    new_places = p.load(path_db_places, False)
    new_labels = p.load(path_db_labels, False)

    # Create an instance of WikidataJsonDump
    wjd = WikidataJsonDump(wjd_dump_path)

    # Create an iterable of WikidataItem
    results = []
    t1 = time.time()

    ENTITY_TYPE = 'person'
    for ii, entity_dict in enumerate(wjd):
        if entity_dict["type"] == "item":
            entity = WikidataItem(entity_dict)

            # Only process if the item is a person -> Bias
            if is_person_or_street(entity) == ENTITY_TYPE:
                res = create_item(entity_dict)

                new_names.set(res[0], res[1][0])
                new_occs.set(res[0], res[1][1])
                new_places.set(res[0], res[1][2])
                new_labels.set(res[0], res[1][3])
                # break # I deactivate this line: Only for test?
            else:
                pass

        if ii % 10000 == 0:
            t2 = time.time()
            dt = t2 - t1
            print(
                len(results),ii,dt
            )
    # Export in the database
    new_names.dump()
    new_occs.dump()
    new_places.dump()
    new_labels.dump()