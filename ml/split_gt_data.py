from joblib import load
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, cohen_kappa_score

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

# Input
path_ml_gt_data = PARAMS["path"]["data_ml"]

# Export
test_size = PARAMS['train']['test_size']
path_X_train = PARAMS['path']['gt_X_train']
path_y_train = PARAMS['path']['gt_y_train']
path_X_test = PARAMS['path']['gt_X_test']
path_y_test = PARAMS['path']['gt_y_test']

################################################################################

if __name__ == "__main__":
    path_ml_gt_data = os.path.join(
        WKSPACE,
        path_ml_gt_data,
    )
    path_X_train = os.path.join(
        WKSPACE,
        path_X_train,
    )
    path_X_test = os.path.join(
        WKSPACE,
        path_X_test,
    )
    path_y_train = os.path.join(
        WKSPACE,
        path_y_train,
    )
    path_y_test = os.path.join(
        WKSPACE,
        path_y_test,
    )

    df = pd.read_csv(path_ml_gt_data, index_col=0)
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
