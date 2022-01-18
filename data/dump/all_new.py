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

def create_item(entity_dict):
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

    #names
    try:
        claim_group_P735 = entity.get_truthy_claim_group('P735')
        for c in claim_group_P735:
            first_names.append(c.mainsnak.datavalue.value['id'])
    except:
        first_names.append('')

    try:
        claim_group_P734 = entity.get_truthy_claim_group('P734')
        for c in claim_group_P734:
            last_names.append(c.mainsnak.datavalue.value['id'])
    except:
        last_names.append('')

    try:
        alias_group = entity_dict['aliases']['de']
        for c in alias_group:
            aliases.append(c['value'])
    except:
        aliases.append('')

    #work
    try:
        claim_group_P106 = entity.get_truthy_claim_group('P106')
        for c in claim_group_P106:
            occs.append(c.mainsnak.datavalue.value['id'])
    except:
        occs.append('')


    #places
    try:
        claim_group_P19 = entity.get_truthy_claim_group('P19')
        for c in claim_group_P19:
            birth.append(c.mainsnak.datavalue.value['id'])
    except:
        birth.append('')

    try:
        claim_group_P20 = entity.get_truthy_claim_group('P20')
        for c in claim_group_P20:
            death.append(c.mainsnak.datavalue.value['id'])
    except:
        death.append('')

    try:
        claim_group_P119 = entity.get_truthy_claim_group('P119')
        for c in claim_group_P119:
            burial.append(c.mainsnak.datavalue.value['id'])
    except:
        burial.append('')

    try:
        claim_group_P69 = entity.get_truthy_claim_group('P69')
        for c in claim_group_P69:
            educated.append(c.mainsnak.datavalue.value['id'])
    except:
        educated.append('')

    try:
        claim_group_P937 = entity.get_truthy_claim_group('P937')
        for c in claim_group_P937:
            work.append(c.mainsnak.datavalue.value['id'])
    except:
        work.append('')

    # label
    try:
        label.append(entity_dict['labels']['de']['value'])
    except:
        label.append('')



    key = entity.entity_id
    value=[[first_names, last_names, aliases],
           occs,
           [birth, death, burial, educated, work],
           label]
    return (key,value)

# Load the database
new_names = p.load('all_new_names.db', False)
new_occs = p.load('all_new_occs.db', False)
new_places = p.load('all_new_places.db', False)
new_labels = p.load('all_new_labels.db', False)


ENTITY_TYPE = 'person'

#create an iterable of WikidataItem
results = []
t1 = time.time()
for ii, entity_dict in enumerate(wjd):
    if entity_dict["type"] == "item":
        entity = WikidataItem(entity_dict)
        if is_person_or_street(entity) == ENTITY_TYPE:
            res = create_item(entity_dict)
            new_names.set(res[0], res[1][0])
            new_occs.set(res[0], res[1][1])
            new_places.set(res[0], res[1][2])
            new_labels.set(res[0], res[1][3])
            break
        else:
            pass

    if ii % 10000 == 0:
        t2 = time.time()
        dt = t2 - t1
        print(
            len(results),ii,dt
        )

new_names.dump()
new_occs.dump()
new_places.dump()
new_labels.dump()
