import time
from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
# from qwikidata.utils import dump_entities_to_json
# from qwikidata.linked_data_interface import get_entity_dict_from_api
# from qwiki import filtered_properties, is_person_or_street
from qwiki import is_person_or_street
# import json
import pickledb as p

#.................................
import os, sys
from IPython.core.ultratb import ColorTB
import yaml

sys.excepthook = ColorTB()

WKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print('\u001b[44m{}\u001b[0m'.format(WKSPACE))
PATH_CFG = './config.yml'

sys.path.append(WKSPACE)
PATH_CFG = os.path.join(WKSPACE, PATH_CFG)

with open(PATH_CFG, 'r') as file:
    PARAMS = yaml.safe_load(file)

#.................................

from data.dump.dump_places import *
from data.dump.dump_places02 import *

#.................................
"""
This program takes a dump of wikidata in .bz2 as input and exports it into a one hot dataset.
Code not optimised for the memory: Better to export smaller pickle DB instead of storing all the database in the memory.
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
lang = PARAMS['search']['lang']
choice_country_wikidata = PARAMS['search']['choice_country_wikidata']

# Output
    # all_new
path_db_names = PARAMS["path"]['db_all_new_names']
path_db_occs = PARAMS["path"]['db_all_new_occs']
path_db_places = PARAMS["path"]['db_all_new_places']
path_db_labels = PARAMS["path"]['db_all_new_labels']

    #dump_places
path_places_db = PARAMS['path']['db_places']
path_output_json = PARAMS['path']['json_places']

    #dump_places02
path_output02_db =PARAMS["path"]["db_extra"]
path_output02_json = PARAMS["path"]["json_extra"]

    #db_count_links
path_export_link_counts_db = PARAMS['path']['tsv_links_test']\
    .replace(".tsv", ".db")
################################################################################

def create_item_all_new(
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

def add_suffix_path_db(
        path,
        suffix,
    ):

    path = path.replace(".db", f"{suffix}.db")
    return path

################################################################################

if __name__ == "__main__":

    #---------------------------------
    # **********
    # all_new.py
    path_db_names = os.path.join(
        WKSPACE,
        path_db_names,
    )
    path_db_occs = os.path.join(
        WKSPACE,
        path_db_occs,
    )
    path_db_places = os.path.join(
        WKSPACE,
        path_db_places,
    )
    path_db_labels = os.path.join(
        WKSPACE,
        path_db_labels,
    )

    print(f"--- path_db_names: {path_db_names}")
    print(f"--- new_occs: {path_db_occs}")
    print(f"--- new_places: {path_db_places}")
    print(f"--- path_db_names: {path_db_labels}")

    # **********
    # dump_place.py
    path_places_db = os.path.join(
        WKSPACE,
        path_places_db,
    )
    path_output_json = os.path.join(
        WKSPACE,
        path_output_json,
    )

    print(f"--- path_places_db: {path_places_db}")
    print(f"--- path_output_json: {path_output_json}")

    # **********
    # dump_place_02.oy
        # dump_place.py
    path_output02_db = os.path.join(
        WKSPACE,
        path_output02_db,
    )
    path_output02_json = os.path.join(
        WKSPACE,
        path_output02_json,
    )

    print(f"--- path_output02_db: {path_output02_db}")
    print(f"--- path_output02_json: {path_output02_json}")

    # **********
    path_export_link_counts_db = os.path.join(
        WKSPACE, 
        # Export
        path_export_link_counts_db
    )


    #---------------------------------
    # Load the databases
    new_names = p.load(path_db_names, False)
    new_occs = p.load(path_db_occs, False)
    new_places = p.load(path_db_places, False)
    new_labels = p.load(path_db_labels, False)

    db = p.load(path_places_db, False)

    db02 = p.load(path_output02_db, False)

    db_count_links = p.load(path_export_link_counts_db, False)

    #---------------------------------
    # Create an instance of WikidataJsonDump
    wjd = WikidataJsonDump(wjd_dump_path)
    # print('\u001b[44m{}\u001b[0m'.format(len(wjd)))

    # Create an iterable of WikidataItem
    results_db = []
    results_db02 = []
    nb_persons = 0
    t1 = time.time()

    ENTITY_TYPE = 'person'
    for ii, entity_dict in enumerate(wjd):

        if entity_dict["type"] == "item":
            entity = WikidataItem(entity_dict)

            # Only process if the item is a person
            if is_person_or_street(entity) == ENTITY_TYPE:
                nb_persons += 1
                res = create_item_all_new(entity_dict)

                new_names.set(res[0], res[1][0])
                new_occs.set(res[0], res[1][1])
                new_places.set(res[0], res[1][2])
                new_labels.set(res[0], res[1][3])

                # To get: res = (key=entity.entity_id, val=[(educated_list), (work_list)])
                res = create_item_dump_places02(entity)
                results_db02.append(res)
                db02.set(res[0],res[1])

            # Data located in the chosen country
            if is_in_country(
                entity=entity, 
                country=choice_country_wikidata,
                ) == True:

                res = create_item_dump_places(entity)       # (key=entity.entity_id, value=[(entity.get_label(lang='en')), instance_of, (qid_p131)])
                results_db.append(res)
                db.set(res[0],res[1])

                # Count links
                id_wikidata = entity_dict["title"]
                try:

                    wikipedia_page = entity_dict["sitelinks"][f"{LANG}wiki"]["title"]\
                        .replace(" ", "_")
                    wikipedia_title = wikipedia_page.split("/")[-1]
                    val =  {
                        "id_wikidata" : id_wikidata,
                        "wikipedia_title" : wikipedia_title, 
                        "count_links" : None,
                    }
                    db_count_links.set(id_wikidata, val)

                except:
                    pass
    

        if ii % 10000 == 0:
            t2 = time.time()
            dt = t2 - t1
            print(
                f"[Idx={ii}] Nb persons: {nb_persons} - Total time: {dt}"
            )

            # Export in the database - Saving time is very high
            # new_names.dump()
            # new_occs.dump()
            # new_places.dump()
            # new_labels.dump()
            # db.dump()
            # db02.dump()

    #---------------------------------
    # Export in the database
    new_names.dump()
    new_occs.dump()
    new_places.dump()
    new_labels.dump()
    
    #---------------------------------
    # First export as a database
    db.dump()

    # Second export as a JSON
    x = json.dumps(results_db,indent=4, ensure_ascii=True)
    with open(path_output_json,'w') as output:
        output.write(x)

    #---------------------------------
    # First export as a database
    db02.dump()

    # Second export as a JSON
    x = json.dumps(results_db02,indent=4)
    with open(path_output02_json,'w') as output:
        output.write(x)

    #---------------------------------
    db_count_links.dump()