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

ROOT_DIR = os.path.abspath("../../")

# create an instance of WikidataJsonDump
wjd_dump_path = ROOT_DIR + "/dump/wikidata-20210517-all.json.bz2"
wjd = WikidataJsonDump(wjd_dump_path)

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

db = p.load('name_data.db', False)
# create an iterable of WikidataItem
results = 0
t1 = time.time()
for ii, entity_dict in enumerate(wjd):
    if entity_dict["type"] == "item":
        try:
            entity = WikidataItem(entity_dict)
            is_name(entity)
        except:
            continue
    if ii % 1000 == 0:
        t2 = time.time()
        dt = t2 - t1
        print(
            "found {} humans among {} entities [entities/s: {:.2f}]".format(
                results, ii, ii / dt
            )
        )

db.dump()
