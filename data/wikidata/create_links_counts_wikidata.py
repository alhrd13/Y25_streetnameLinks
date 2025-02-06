
import pickledb as p
# from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
import requests
import pandas as pd

#.................................
import os, sys
from IPython.core.ultratb import ColorTB
import yaml
import time
from tqdm import tqdm
import multiprocessing

sys.excepthook = ColorTB()

WKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH_CFG = './config.yml'

sys.path.append(WKSPACE)
PATH_CFG = os.path.join(WKSPACE, PATH_CFG)

with open(PATH_CFG, 'r') as file:
    PARAMS = yaml.safe_load(file)
#.................................

################################################################################
# USER PARAMETERS
################################################################################\

# Import
wjd_dump_path = PARAMS["path"]["wjd_dump_path"]
LANG = PARAMS['search']['lang']

# Process
create_map_idWikidata_idWikipedia = False
cal_counts_wikipedia = True
batch_size_search = 200000

# Debug
max_iter = -1


# Export
path_export_link_counts_tsv = PARAMS['path']['tsv_links']
path_export_link_counts_db = PARAMS['path']['tsv_links']\
    .replace(".tsv", ".db")

# ################################################################################

def get_count_wikipedia(
        wikipedia_title, 
    ):

    global counter_max
    global time_start

    url = "https://linkcount.toolforge.org/api/?page={ID_WIKIPEDIA}&project={LANG}.wikipedia.org"
    url_completed = url.format(
        ID_WIKIPEDIA=wikipedia_title,
        LANG=LANG,
    )

    do_search = True
    response = requests.get(url_completed)
    # print("---", wikipedia_title)
    # print(response)

    attempt = 1
    # Too many requests
    while response.status_code == 429 and do_search:
        response = requests.get(url_completed)
        attempt += 1
        if attempt == 20:
            do_search = False
    
    try:
        response = response.json()
        if "error" in response.keys():
            count_links = 0
        else:
            count_links = response["wikilinks"]["all"]
    except:
        count_links = 0
        # print(response) # Error <Response [429]>
        print(counter.value, wikipedia_title, count_links)

    with counter.get_lock():
        counter.value += 1
        # print(f"--- Done: {counter.value} / {counter_max. value}")
        if counter.value % 10000 == 0:
            time_end = time.time()
            duration = round(time_end - time_start.value, 0)
            print(f"--- Done: {counter.value} / {counter_max.value} - Time: {duration} s")

    return count_links

################################################################################

def get_batch(
        iterable, 
        batch_size=1,
        get_idx=False,
    ):

    if get_idx:
        iterable = range(len(iterable))

    l = len(iterable)

    for ndx in range(0, l, batch_size):
        iterable_batch = iterable[ndx:min(ndx + batch_size, l)]
        yield iterable_batch

################################################################################

counter = None

def init_process(arg0, arg1, arg3):
    ''' store the counter for later use '''
    global counter
    global counter_max
    global time_start

    counter = arg0
    counter_max = arg1
    time_start = arg3

################################################################################

if __name__ == "__main__":

    #---------------------------------
    path_export_link_counts_tsv = os.path.join(
        WKSPACE, 
        # Export
        path_export_link_counts_tsv
    )

    path_export_link_counts_db = os.path.join(
        WKSPACE, 
        # Export
        path_export_link_counts_db
    )

    #---------------------------------
    # Load the database
    db = p.load(path_export_link_counts_db, False)
    print(f"Imported db: {path_export_link_counts_db}")

    #---------------------------------
    # Creation of the database id_wikidata <> id_wikipedia
    t1 = time.time()
    if create_map_idWikidata_idWikipedia:
        # Create an instance of WikidataJsonDump
        wjd = WikidataJsonDump(wjd_dump_path)

        print(f"--- Create of a database id_wikidata <> id_wikipedia", flush=True)
        for idx, entity_dict_wjd in enumerate(tqdm(wjd)):

            # if idx == 3:
            #     break

            if entity_dict_wjd["type"] == "item":
                id_wikidata = entity_dict_wjd["title"]
                try:

                    wikipedia_page = entity_dict_wjd["sitelinks"][f"{LANG}wiki"]["title"]\
                        .replace(" ", "_")
                    wikipedia_title = wikipedia_page.split("/")[-1]
                    val =  {
                        "id_wikidata" : id_wikidata,
                        "wikipedia_title" : wikipedia_title, 
                        "count_links" : None,
                    }
                    db.set(id_wikidata, val)

                except:
                    pass

            if idx % 10000 == 0:
                # Time
                t2 = time.time()
                dt = t2 - t1
                print(f"[{idx}] Length of the index: {len(db.getall())} - Time: {dt}")
    
        db.dump()

    #---------------------------------
    if cal_counts_wikipedia:
        print(f"--- Calculate the number of links per wikidata", flush=True)

        # API request
        S = requests.Session()
        url = "https://linkcount.toolforge.org/api/?page={ID_WIKIPEDIA}&project={LANG}.wikipedia.org"
        
        # Params for the request
        all_params = []
        path_map_wikipediaTitle_idWikidata = os.path.join(
            WKSPACE,
            "out",
            "_tmp_map_wikipediaTitle_idWikidata.db"
        )
        map_wikipediaTitle_idWikidata = p.load(path_map_wikipediaTitle_idWikidata, False)

        counter_max = len(list(db.getall()))
        count_data_to_treat = 0

        for idx, key in enumerate(tqdm(db.getall())):

            if count_data_to_treat == max_iter:
                break

            val = db.get(key)
            if val["count_links"] is None:
                count_data_to_treat += 1

                wikipedia_title = val["wikipedia_title"]
                map_wikipediaTitle_idWikidata.set(wikipedia_title, key)

                all_params.append(wikipedia_title)

        # Time
        time_start = time.time()
        time_start_0 = time_start

        # Synchronised values for multiprocessing
        counter = multiprocessing.Value('i', 0)
        counter_max = multiprocessing.Value('i', counter_max)
        time_start = multiprocessing.Value('f', time_start)

        # Init multiprocess
        pool = multiprocessing.Pool(
            processes=50,
            initializer = init_process,
            initargs = (counter, counter_max, time_start)
        )

        # We work per batch to save after each iteration

        for batch_idx in get_batch(
                iterable=all_params,
                batch_size=batch_size_search,
                get_idx=True,
            ):
            all_params_batch = [all_params[idx] for idx in batch_idx]

            # results = pool.starmap_async(
            results = pool.map_async(
                get_count_wikipedia, 
                iterable=all_params_batch,
            )

            all_counts_batch = results.get()

            for key, count in zip(all_params_batch, all_counts_batch):
                idx_wikidata = map_wikipediaTitle_idWikidata.get(key)
                val = db.get(idx_wikidata)
                val["count_links"] = int(count)
                db.set(idx_wikidata, val)

            # Export
            print(f"-- [idx={batch_idx[-1]}] Export in: {path_export_link_counts_db}")
            db.dump()

            time_end = time.time()
            duration = f"  \tDuration: {round(time_end - time_start_0, 0)} s"
            print(f"Duration: {duration}")

        #.................................
        with open(path_export_link_counts_db, encoding='utf-8') as file:
            db = pd.read_json(file, orient="index")

        db.to_csv(
            path_export_link_counts_tsv, 
            encoding='utf-8', 
            sep='\t', 
            index=False, 
            header=False,
        )


