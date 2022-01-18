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

ROOT_DIR = os.getcwd()

args = sys.argv
try:
    if args[1] == 'bremen':
        X = pd.read_csv(ROOT_DIR + '/eval/candidates_bremen.csv')
    elif args[1] == 'nrw':
        X = pd.read_csv(ROOT_DIR + '/eval/candidates_nrw.csv')
    else:
        X = pd.read_csv(args[1])
except:
    print('Please select a dataset of street-candidate pairs [bremen | nrw] or choose a fitting file.')
    exit()

candidate_threshold = 0.5


# ml data
X_test = X.drop(['street', 'candidate','district'],axis=1)

# model
model = load(ROOT_DIR + '/ml/rfc_1300.joblib')

# predict
prob = model.predict_proba(X_test)
proba = []
for p in prob:
    proba.append(p[1])
X['proba'] = proba

# Sort by propability and then remove duplicate streets and districts
# This should leave the best candidate for every street per district
X = X.sort_values(by=['proba'], ascending=False).drop_duplicates(subset=['street','district'], keep='first')



# Drop all candidates below the treshold
X.drop(X[ X['proba'] < candidate_threshold].index,inplace=True)


with open('best_candidate.csv','w') as output:
    X.to_csv(output,header=True,index=False)
