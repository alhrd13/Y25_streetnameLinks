import json
import pickledb
import os
import re
import pandas

person_index = pickledb.load('/home/gurtovoy/data/new_index.db',False)
suffix = json.load(open('/home/gurtovoy/new_suffixe/suffixe_final.json','r'))
titels = json.load(open('/home/gurtovoy/new_suffixe/suffixe_titel.json','r'))
links = pandas.read_csv('/home/gurtovoy/data/link_counts_wikidata.tsv', sep='\t', index_col='Q64')

gdf = pandas.read_csv('test.csv',index_col=0)

new_df = pandas.DataFrame()

test = []

for t,i in enumerate(gdf.name):
# Suchbegriff erstellen und vorab filtern
    print(t)
    query = i
    if query.endswith(')') == True:
        extra = re.findall('\(.*\)', query)
        query = query.replace(extra[0],'').rstrip()
    initials = re.findall('[A-Z]\. ',query)
    for init in initials:
        query = query.replace(init,'').rstrip().lstrip()

# Suffixe im Suchbegriff entfernen
    for s in suffix:
        if query.endswith(s) == True:
            query = query.replace(s,'').rstrip().lstrip()
            break
# Präfixe im Suchbegriff entfernen
    for titel in titels:
        query = query.replace(titel,'').rstrip().lstrip()

    if len(query) == 0:
        continue

# Popularity Ranking
    result = person_index.get(query)

# Füge ggf. Bindestrich zwischen letzten beiden Namen hinzu
    if result == False:
        backspace = query.rfind(' ')
        if backspace > -1:
            query_list = list(query)
            query_list[backspace] = '-'
            query = ''.join(query_list)
            result = person_index.get(query)

# Entferne ggf. das letzte s im Namen
    if result == False:
        if query.endswith('s') == True:
            query_list = list(query)
            query_list = query_list[:-1]
            query = ''.join(query_list)
            result = person_index.get(query)
            if result == False:
                continue
        else:
            continue

    max = 0
    res = result[0][0]
    for r in result:
        try:
            qid = r[0]
            count = int(links.loc[qid][1])
            if count > max:
                res = r[0]
                max = count
        except:
            pass

    data = gdf.iloc[t]
    new_df.append(data)

with open('named_bremen.csv','w') as output:
   new_df.to_csv(output,header=True)
