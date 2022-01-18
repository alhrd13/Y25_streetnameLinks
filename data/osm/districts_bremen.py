import os
import geopandas
import pandas
from shapely.wkt import loads
from shapely.geometry import Polygon, LineString

gdf = pandas.read_csv('streets_bremen.tsv',index_col=0,sep='\t')
bremen_gdf = pandas.read_csv('polygons_bremen.tsv',index_col=0,sep='\t')

for t,i in enumerate(bremen_gdf['geometry']):
   bremen_gdf['geometry'].iloc[t] = loads(i)

for t,i in enumerate(gdf['geometry']):
   gdf['geometry'].iloc[t] = loads(i)

district = []

for tt,j in enumerate(gdf['geometry']):
    print(tt)
    street = j
    min_area = bremen_gdf['geometry'].loc['Q24879'].area
    res = 'Q24879'
    for t,i in enumerate(bremen_gdf.geometry):
        if i.contains(street):
            if i.area < min_area:
                min_area = i.area
                res = bremen_gdf.iloc[t].name
    district.append(res)

gdf = gdf.assign(district = district)

with open('test.csv','w') as output:
    gdf.to_csv(output,header=True)
