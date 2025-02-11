import json

from qwikidata.sparql import (
    return_sparql_query_results,
)


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

wikidata_street_2_person = os.path.join(
    WKSPACE,
    PARAMS["path"]["street_2_person"],
)

# ################################################################################

# ################################################################################

if __name__ == "__main__":

    # send any sparql query to the wikidata query service and get full result back
    # here we use an example that counts the number of humans
    sparql_query = """
    SELECT DISTINCT ?street ?streetLabel ?person ?personLabel

    WHERE {  

        BIND(?street_id AS ?street)
        BIND(?street_name AS ?streetLabel)
        BIND(?origin_id AS ?person)
        BIND(?origin_name AS ?personLabel)
        
        ?street_id wdt:P138 ?origin_id ;   # named after
            rdfs:label ?street_name ; 
            wdt:P31 ?type_street ;    # instance of 
            wdt:P17 wd:Q408 ;     # Country=Australia
            wdt:P131 ?admin.      # Located in the administrative territorial entity

        ?origin_id rdfs:label ?origin_name ;
            wdt:P31 wd:Q5 .       # Human

        FILTER (?type_street IN (wd:Q34442, wd:Q79007, wd:Q537127))  # road, street, road bridge
        FILTER (langMatches( lang(?street_name), "EN" ) )   
        FILTER (lang(?origin_name) = "en")
        # FILTER (?admin NOT IN (wd:Q3141, wd:Q6811747))  # Melbourne, Melbourne central business district 
        
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } 
    }
    """

    res = return_sparql_query_results(sparql_query)
    nb_res = len(res["results"]["bindings"])
    print(f"Nb results: {nb_res}")
    
    with open(wikidata_street_2_person, 'w', encoding="utf-8") as file:
        json.dump(res, file, ensure_ascii=True, indent=4)

    print(f"Exported in: {wikidata_street_2_person}")