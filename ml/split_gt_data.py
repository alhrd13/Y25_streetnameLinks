from joblib import load
import pandas as pd
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

test_size = PARAMS['train']['split_data']
path_X_train = PARAMS['path']['path_X_train']
path_y_train = PARAMS['path']['path_y_train']
path_X_test = PARAMS['path']['path_X_test']
path_y_test = PARAMS['path']['path_y_test']

################################################################################

if __name__ == "__main__":
    `df = pd.read_csv('ml_gt_data.csv', index_col=0)
    # Set input & output, split into training & test
    y = df.correct
    X = df.drop('correct',axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=test_size)

    with open(path_X_train, 'w') as output:
        X_train.to_csv(output, header=True)
    with open(path_X_test, 'w') as output:
        X_test.to_csv(output, header=True)
    with open(path_y_train, 'w') as output:
        y_train.to_csv(output, header=True)
    with open(path_y_test, 'w') as output:
        y_test.to_csv(output, header=True)
