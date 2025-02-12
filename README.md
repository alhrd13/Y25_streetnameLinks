# StreetnameLinks

This project is dedicated to linking street names to the person they are named after.
The street information is taken from [OpenStreetMap](https://www.openstreetmap.org/) and linked to person data that was generated using [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) (as at May 17th 2022).

Our method was tested on streets from the city of Bremen and the state of North Rhine-Westfalia in Germany. It was able to detect _896_ new person links in Bremen and _31.363_ new links in North Rhine-Westfalia respectively. Overall, we found _183.022_ possible street-person links in all of Germany.

## Approach
In an effort to correctly predict the namesake for a given street, we extracted street data from OpenStreetMap and generated possible candidates for each street.
The candidates are taken from an index database that was created by extracting data from a [Wikidata dump](https://dumps.wikimedia.org/wikidatawiki/). For each candidate we further get properties such as occupations, birth place, place of death etc. The candidates are than classified by a machine learning algorithm, picking the candidate with the highest score above a certain threshold as the final result for each street.

## Results
The machine learning algorithm was trained on known streets in Wikidata that had the property "named after". On the test data, it achieved a precision of 95,2% with a recall of 90,6%. When applied on streets in OSM, our method was able to detect _896_ new person links in Bremen and _31.363_ new links in North Rhine-Westfalia respectively.
You can take a look at the findings of this project in the following two files:
```
best_candidates_bremen.csv
best_candidates_nrw.csv
```
## Dependencies
- Python >= 3.8
- [Pandas](https://pandas.pydata.org/)
- [Geopandas](https://geopandas.org/en/stable/)
- [Pickledb](https://pypi.org/project/pickleDB/)
- [Scikit-Learn](https://pypi.org/project/scikit-learn/)
- [qwikidata](https://pypi.org/project/qwikidata/)

## Usage
To train the ML model and evaluate it, simply run the following command:
```
ml/ml_training.py
```
(optional) If you want to calculate the results of the approach on OSM:
- you can generate a file with all candidates for streets in Bremen or North Rhine-Westfalia using the following command
- Alternatively, you can use your own file from a different region.
```
street_candidates.py [ bremen | nrw | file ]
```

You can then predict the most likely person from the aforementioned candidates for each street.
```
predict.py [bremen | nrw | file]
```
The code will return a csv-file containing the candidate with the highest score above a certain threshold for each street.



# Data

- Install the environment:
  - `python3 -m venv env_street`
  - `source env_street/bin/activate`
  - `pip install -r Y25_streetnameLinks/requirements.txt`

- Create a folder `./out`
- Add `./out/suffix.json` and `./out/prefix` with an empty JSON: []


- Download the data:
  - Wikidata (dump of all the data) = base of knowledge
    - `curl -o Y25_streetnameLinks/data/wikidata_all.json.bz2 https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2` 
    - Choose a dump: e.g. "wikidata-20210517-all.json.bz2"
  - Wikidata (with the links between street <> person) = base for ground truth (model training)
    - Open `./data/wikidata/create_wikidata_all.py`
    - Change the SPARQL query if your want data different from Australia and not related to your test dataset
  - For the inference = base for inference. We must create a CSV file with the following columns:
    - Compulsory: name, district
    - Optional: etymology_wikidata
    - Option 1: via OSM 
      - Use QuickOSM (QGIS) and find all the places with the tag name:etymology
      - Use the functions in `./data/osm/districts_bremen.py` + `./data/osm/reduce.py`
    - Option 2:
      - Manually write your CSV file with the columns: name, district, etymology_wikidata (name should be the root of the street: Batman for John Batman Street)

- Modify the paths in `./config.yml`
- 
- Pre-process - Execute:
  - Wikidata
    - `data/dump/all_new.py`:
      - Create:
        - all_new_names.db'
        - all_new_occs.db
        - all_new_places.db
        - all_new_labels.db
    - `data/dump/dump_places.py` ---> already integrated in `data/dump/all_new.py`
      - Creates:
        - places.db
    - `data/dump/dump_places02.py` ---> already integrated in `data/dump/all_new.py`
      - Creates:
        - extra.db
    - `./data/wikidata/new_names.py`
      - Creates
        - name_data.db
    - `./data/wikidata/new_index.py`
      - Creates:
        - link_counts_wikidata.tsv
  - Data for evaluation:
    - Only if you use data from OSM:
      - `data/osm/districts_bremen.py`
        - Creates
          - test.tsv
      - `data/osm/reduce.py`
        - Creates:
          - named_bremen.py
    - Otherwise, create your own csv file with the columns: name, district, etymology_wikidata 
      - The use of `./data/affixes` is not useful

- Train
  - `ml_gt_data.py`
  - `split_gt_data.py`
  - `ml_training.py`

- Infer:
  - 


? qwiki
PATH = ROOT_DIR + "/data/wikidata/filtered_subprops.json"