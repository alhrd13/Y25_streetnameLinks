import os
# import geopandas
import pandas
from shapely.wkt import loads
# from shapely.geometry import Polygon, LineString

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

"""
Affects a new column to {tsv_streets}: districts
The districts are extracted from tsv_polygons
"""

################################################################################
# USER PARAMS
################################################################################

# # Input

# tsv_streets = 'streets_bremen.tsv'
# tsv_polygons = 'polygons_bremen.tsv'

# # Output
# path_file_output = 'test.tsv'
# #.................................
# # Index = Q24879 for example
# id_wikidata_ref = 'Q24879'

# Input

tsv_streets = PARAMS['path']['tsv_streets']
tsv_polygons = PARAMS['path']['tsv_polygons']

# Output
path_file_output = PARAMS['path']['tsv_test']
#.................................
# Index = Q24879 for example
id_wikidata_ref = PARAMS['search']['id_wikidata_ref_test']

################################################################################

if __name__ == "__main__":

    #---------------------------------
    # Import data
    gdf = pandas.read_csv(
        tsv_streets,
        index_col=0,
        sep='\t',
    )

    bremen_gdf = pandas.read_csv(
        tsv_polygons,
        index_col=0,
        sep='\t',
    )

    #---------------------------------
    # Converts geom into WKT
        # bremen_gdf
    for t,i in enumerate(bremen_gdf['geometry']):
        bremen_gdf['geometry'].iloc[t] = loads(i)

        # gdf
    for t,i in enumerate(gdf['geometry']):
        gdf['geometry'].iloc[t] = loads(i)

    district = []

    # For each street from tsv_street
    for tt,j in enumerate(gdf['geometry']):
        print(tt)
        street = j

        # Pick the area of of the studied area
            # Q24879 = wikidata(Bremen)
        min_area = bremen_gdf['geometry'].loc[id_wikidata_ref].area

        res = id_wikidata_ref

        # For each polygon in tsv_polygon
        for t,i in enumerate(bremen_gdf.geometry):
            # If the polygon contains the street
            if i.contains(street):
                # If the area of the polygon is inferior to the previous stored area
                if i.area < min_area:
                    # Update the new min area
                    min_area = i.area
                    res = bremen_gdf.iloc[t].name
        district.append(res)

    gdf = gdf.assign(district = district)

    #.................................
    # Export
    with open(path_file_output,'w') as output:
        gdf.to_csv(output,header=True)
