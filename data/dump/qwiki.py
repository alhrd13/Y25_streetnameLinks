import os
from qwikidata.linked_data_interface import get_entity_dict_from_api
from qwikidata.entity import WikidataItem, WikidataProperty, WikidataLexeme
from qwikidata.claim import WikidataClaimGroup,WikidataClaim
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

path_subprops = PARAMS['path']['path_subprops']
path_subprops = os.path.join(
    WKSPACE,
    path_subprops,
)

f = json.load(open(path_subprops,'r'))

lang = ['de', 'en', 'fr', 'ru']

person_claims = [
'P735',  #given name
'P734',  #family name
'P106',  #occupation
'P742'  #pseudonym
]

street_claims = [
'P131',  #located in administrative territorial entity
'P625',  #coordinates
'P402',  #OSM-ID
'P138'  #named after
]

################################################################################

def is_person_or_street(entity):
    try:
        claim_group = entity.get_truthy_claim_group('P31')
        claim = claim_group[0]
        qid = claim.mainsnak.datavalue.value['id']
        if qid == 'Q5':
            return 'person'
        if qid == 'Q79007':
            return 'street'
    except:
        return False

################################################################################

def filtered_properties(entity_dict, is_type):
    item = {
        'type': entity_dict['type'],
        'id' : entity_dict['id'],
        'labels' : {
            },
        'descriptions' : {
        },
        'aliases' : {
        },
        'claims':{
        },
        'sitelinks' : {
        }
    }
    for i in lang:
        try:
            item['labels'][i] = entity_dict['labels'][i]
        except:
            pass

        try:
            item['descriptions'][i] = entity_dict['descriptions'][i]
        except:
            pass

        try:
            item['aliases'][i] = entity_dict['aliases'][i]
        except:
            pass

        try:
            item['sitelinks'][i] = entity_dict['sitelinks'][i+'wiki'],
        except:
            pass

    if is_type == 'person':
        #general claims
        for i in person_claims:
            try:
                item['claims'][i] = entity_dict['claims'][i]
            except:
                pass

    if is_type == 'street':
        for k in street_claims:
            try:
                item['claims'][k] = entity_dict['claims'][k]
            except:
                pass

    #location related claims
    for j in f:
        try:
            item['claims'][j] = entity_dict['claims'][j]
        except:
            pass

    return item

################################################################################
