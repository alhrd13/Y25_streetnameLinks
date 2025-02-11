'''
Pick the best candidate for a street
You can choose between the Bremen or Nordrhein-Westfalen data, or you can pick your own. Make sure to generate street-candidate pairs first.
TODO: implement a method to choose the best candidate for a single street
TODO: option to adjust candidate threshold (default: 0.5)
'''

import os
import sys
import pandas as pd
import pickledb as p
from joblib import load
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, cohen_kappa_score

#.................................
import os, sys
from IPython.core.ultratb import ColorTB
import yaml

sys.excepthook = ColorTB()

WKSPACE = os.path.dirname(os.path.abspath(__file__))
PATH_CFG = './config.yml'

sys.path.append(WKSPACE)
PATH_CFG = os.path.join(WKSPACE, PATH_CFG)

with open(PATH_CFG, 'r') as file:
    PARAMS = yaml.safe_load(file)
#.................................


# ################################################################################
# ROOT_DIR = os.getcwd()
# args = sys.argv
# try:
#     if args[1] == 'bremen':
#         X = pd.read_csv(ROOT_DIR + '/eval/candidates_bremen.csv')
#     elif args[1] == 'nrw':
#         X = pd.read_csv(ROOT_DIR + '/eval/candidates_nrw.csv')
#     else:
#         X = pd.read_csv(args[1])
# except:
#     print('Please select a dataset of street-candidate pairs [bremen | nrw] or choose a fitting file.')
#     exit()

# candidate_threshold = 0.5
candidate_threshold = 0

#---------------------------------
path_ml = PARAMS['path']['ml']
path_export_results_pred = PARAMS['path']['best_candidate']
path_candidates = PARAMS["path"]["path_candidates_prepared_for_predict"]

path_candidates = os.path.join(
    WKSPACE,
    path_candidates,
)
path_ml = os.path.join(
    WKSPACE,
    path_ml,
)
path_export_results_pred = os.path.join(
    WKSPACE,
    path_export_results_pred,
)
path_candidates = os.path.join(
    WKSPACE,
    path_candidates,
)

X = pd.read_csv(path_candidates)

################################################################################

if __name__ == "__main__":

    path_ml = os.path.join(
        WKSPACE,
        path_ml,
    )
    path_export_results_pred = os.path.join(
        WKSPACE,
        path_export_results_pred,
    )

    # ml data
    # X_test = X.drop(['street', 'candidate', 'candidate_explicit', 'district','correct'],axis=1)
    X_test = X.drop(['street', 'candidate', 'candidate_explicit'],axis=1)

    # model
    model = load(path_ml)

    # predict
    prob = model.predict_proba(X_test)
    proba = []
    for p in prob:
        proba.append(p[1])
    X['proba'] = proba

    # Sort by propability and then remove duplicate streets and districts
    # This should leave the best candidate for every street per district
    # X = X.sort_values(by=['proba'], ascending=False).drop_duplicates(subset=['street','district'], keep='first')
    X = X.sort_values(by=['proba'], ascending=False).drop_duplicates(subset=['street'], keep='first')


    # Drop all candidates below the treshold
    X.drop(X[ X['proba'] < candidate_threshold].index,inplace=True)


    with open(path_export_results_pred,'w') as output:
        X.to_csv(output,header=True,index=False)
