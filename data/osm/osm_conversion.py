"""
Just a test
"""

# osm_id	name	street_type	wikipedia	wikidata	etymology_wikidata	etymology_wikipedia	etymology_description	local_name	geometry	name_de	name_en	name_fr	name_es	name_ru
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


import geopandas as gpd

all_paths_osm = [
    "/Users/alexis/Documents/05a_Corpus/01_GEO/OSM_name-etymology/OSM_etymology_lines.geojson",
    "/Users/alexis/Documents/05a_Corpus/01_GEO/OSM_name-etymology/OSM_etymology_multilinestrings.geojson",
    "/Users/alexis/Documents/05a_Corpus/01_GEO/OSM_name-etymology/OSM_etymology_multipolygons.geojson",
    "/Users/alexis/Documents/05a_Corpus/01_GEO/OSM_name-etymology/OSM_etymology_points.geojson",
]

total_data = 0
all_pairs = set()

for path_osm in all_paths_osm:

    osm = gpd.read_file(path_osm)


    map_conversion = {
        "osm_id" : "osm_id",
        "name" : "name",
        "street_type" : "highway",
        "wikipedia" : "wikipedia",
        "wikidata" : "wikidata",
        "etymology_wikidata" : "name:etymology",
        "etymology_wikipedia" : "name:etymology:wikipedia",
        "etymology_description" : None,
        "local_name" : "name",
        "geometry" : "geometry",
        "name_de" : "name:de",
        "name_en" : "name:en",
        "name_fr" : "name:fr",
        "name_ru" : "name:ru",
    }
    # print('\u001b[44m{}\u001b[0m'.format(osm.columns))

    columns_osm = set(osm.columns)
    columns_keep = set(map_conversion.values())

    columns_delete = columns_osm.difference(columns_keep)
    osm = osm.drop(columns=columns_delete)
    osm = osm.loc[osm["name:etymology"].notnull()]
    # total_data += len(osm)

    for idx, row in osm.iterrows():
        pair = (row['name'], row['name:etymology'])
        if pair not in all_pairs:
            all_pairs.add(pair)
            total_data += 1
            print(f"{row['name']} ---> {row['name:etymology']}")

print(f"Total data: {total_data}")


