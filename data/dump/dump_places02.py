import time
from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json
from qwikidata.linked_data_interface import get_entity_dict_from_api
from qwiki import filtered_properties, is_person_or_street
import json
import pickledb as p

"""
This function reads the wikidata and exports into a database and JSON:
(key=entity.entity_id, val=[(educated_list), (work_list)])
"""

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


################################################################################
# User params
################################################################################

if __name__ == "__main__":
    # # Input
    # wjd_dump_path = "wikidata-20210517-all.json.bz2"

    # # Output
    # path_output_db = 'extra.db'
    # path_output_json = 'extra.json'

    # Input
    wjd_dump_path = PARAMS["path"]["wjd_dump_path"]

    # Output
    path_output_db =PARAMS["path"]["db_extra"]
    path_output_json = PARAMS["path"]["json_extra"]


    #---------------------------------
    wjd_dump_path = os.path.join(
        WKSPACE,
        wjd_dump_path,
    )

    path_output_db = os.path.join(
        WKSPACE,
        path_output_db,
    )

    path_output_json = os.path.join(
        WKSPACE,
        path_output_json,
    )



################################################################################

# def create_item_dump_places02(entity):
#     educated_list = []
#     work_list = []
#     #educated at
#     try:
#         claim_group_P69 = entity.get_truthy_claim_group('P69')
#         for c in claim_group_P69:
#             qid_p69 = c.mainsnak.datavalue.value['id']
#             educated_list.append(qid_p69)
#     except:
#         pass

#     #work
#     try:
#         claim_group_P937 = entity.get_truthy_claim_group('P937')
#         for c in claim_group_P937:
#             qid_p937 = c.mainsnak.datavalue.value['id']
#             work_list.append(qid_p937)
#     except:
#         pass

#     #.................................
#     # Output
#     key = entity.entity_id
#     value=[
#         (educated_list),
#         (work_list)
#     ]
#     return (key,value)

################################################################################
def create_item_dump_places02(entity):
    admin_list = []

    #located in administrative territorial entity
    try:
        claim_group_P69 = entity.get_truthy_claim_group('P131')
        for c in claim_group_P69:
            qid_p131 = c.mainsnak.datavalue.value['id']
            admin_list.append(qid_p131)
    except:
        pass

    #.................................
    # Output
    if len(admin_list) != 0:
        key = entity.entity_id
        value=[
            (admin_list)
        ]
        return (key, value)
    else:
        return None

################################################################################

if __name__ == "__main__":

    # create an instance of WikidataJsonDump
    wjd = WikidataJsonDump(wjd_dump_path)

    # Load the orte database
    db = p.load(path_output_db, False)


    # Create an iterable of WikidataItem
    # ENTITY_TYPE = 'person'    # Original paper
    ENTITY_TYPE = "street"
    
    results = []
    t1 = time.time()

    count_items = 0
    for ii, entity_dict in enumerate(wjd):

        # # Debug
        # if count_items == 10:
        #     break

        if entity_dict["type"] == "item":
            entity = WikidataItem(entity_dict)
            # if is_person_or_street(entity) == ENTITY_TYPE:

            
            # **********
            # res = (key=entity.entity_id, val=[(educated_list), (work_list)])

            # **********

            # filtered_data = filtered_properties(
            #      entity_dict=entity_dict,
            #      is_type=ENTITY_TYPE,
            # )
            #located in administrative territorial entity
            # located_in_administrative_territorial_entity = filtered_data['claims']["P131"]
            # res = (entity.entity_id, located_in_administrative_territorial_entity)

            # Export
            # res: ('Q15321', [['Q656', 'Q270196']])
            res = create_item_dump_places02(entity)
            if res is not None:
                # print("---", res)
                results.append(res)
                db.set(res[0],res[1])

                count_items += 1
            # else:
            #     pass

        # Output to see the progression
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

