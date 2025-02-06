
# import json
import pickledb as p

#.................................
import os, sys
from IPython.core.ultratb import ColorTB
import yaml
from copy import deepcopy

sys.excepthook = ColorTB()

WKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH_CFG = './config.yml'

sys.path.append(WKSPACE)
PATH_CFG = os.path.join(WKSPACE, PATH_CFG)

with open(PATH_CFG, 'r') as file:
    PARAMS = yaml.safe_load(file)

################################################################################

if __name__ == "__main__":
    path_db_names = PARAMS["path"]['db_all_new_names']
    path_db_places = PARAMS["path"]['db_all_new_places']
    path_db_links_counts_wikidata = PARAMS["path"]['tsv_links']
    path_db_links_counts_wikidata = path_db_links_counts_wikidata.replace(".tsv", ".db")

    path_db_names = os.path.join(
        WKSPACE,
        path_db_names,
    )

    path_db_places = os.path.join(
        WKSPACE,
        path_db_places,
    )

    path_db_links_counts_wikidata = os.path.join(
        WKSPACE,
        path_db_links_counts_wikidata,
    )

    #---------------------------------
    db_names = p.load(path_db_names, False)
    print(f"Imported: {path_db_names} / Nb data: {len(db_names.getall())}")
    db_places = p.load(path_db_places, False)
    print(f"Imported: {path_db_places} / Nb data: {len(db_places.getall())}")

    db_links_counts_wikidata = p.load(path_db_links_counts_wikidata, False)
    print(f"Imported: {path_db_links_counts_wikidata} / Nb data: {len(db_links_counts_wikidata.getall())}")

    # all_valid_keys = set()
    # for path in [path_db_names, path_db_places]:
    #     db = p.load(path)
    #     new_keys = db.getall()
    #     all_valid_keys.add(new_keys)
    # print(f"Nb of valid keys: {len(all_valid_keys)}")

    count = 0    
    total = len(db_links_counts_wikidata.getall())
    all_keys = deepcopy(db_links_counts_wikidata).getall()
    for key in all_keys:
        count += 1
        if db_names.get(key) is False:
            if db_places.get(key) is False:
                db_links_counts_wikidata.rem(key)
        if count % 100000 == 0:
            print(f"{count} / {total}")
    
    db_links_counts_wikidata.dump()
        # if key not in all_valid_keys:
        #     db_links_counts_wikidata.remove(key)

