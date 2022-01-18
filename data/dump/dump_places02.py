import time
from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json
from qwikidata.linked_data_interface import get_entity_dict_from_api
from qwiki import filtered_properties, is_person_or_street
import json
import pickledb as p

# create an instance of WikidataJsonDump
wjd_dump_path = "wikidata-20210517-all.json.bz2"
wjd = WikidataJsonDump(wjd_dump_path)

def create_item(entity):
    educated_list = []
    work_list = []
    #educated at
    try:
        claim_group_P69 = entity.get_truthy_claim_group('P69')
        for c in claim_group_P69:
            qid_p69 = c.mainsnak.datavalue.value['id']
            educated_list.append(qid_p69)
    except:
        pass

    #work
    try:
        claim_group_P937 = entity.get_truthy_claim_group('P937')
        for c in claim_group_P937:
            qid_p937 = c.mainsnak.datavalue.value['id']
            work_list.append(qid_p937)
    except:
        pass


    key = entity.entity_id
    value=[
    (educated_list),
    (work_list)
    ]
    return (key,value)

# Load the orte database
db = p.load('extra.db', False)

ENTITY_TYPE = 'person'

#create an iterable of WikidataItem
results = []
t1 = time.time()
for ii, entity_dict in enumerate(wjd):
    if entity_dict["type"] == "item":
        entity = WikidataItem(entity_dict)
        if is_person_or_street(entity) == ENTITY_TYPE:
            res = create_item(entity)
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

db.dump()
x = json.dumps(results,indent=4)
with open('extra.json','w') as output:
    output.write(x)

