from joblib import dump, load
import pandas as pd
import time
from pandas import DataFrame
from sklearn.metrics import classification_report, confusion_matrix, cohen_kappa_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier

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



################################################################################
# Import
path_X_train = PARAMS['path']['gt_X_train']
path_y_train = PARAMS['path']['gt_y_train']
path_X_test = PARAMS['path']['gt_X_test']
path_y_test = PARAMS['path']['gt_y_test']

# Export
path_ml = PARAMS['path']['ml']

#.................................
do_test = True

################################################################################

if __name__ == "__main__":

    path_X_train = os.path.join(
        WKSPACE,
        path_X_train
    )
    path_y_train = os.path.join(
        WKSPACE,
        path_y_train
    )
    path_X_test = os.path.join(
        WKSPACE,
        path_X_test
    )
    path_y_test = os.path.join(
        WKSPACE,
        path_y_test
    )
    path_ml = os.path.join(
        WKSPACE,
        path_ml
    )

    # Load the training and test dataset
    X_train = pd.read_csv(path_X_train)
    y_train = pd.read_csv(path_y_train)
    y_train = y_train.correct
    X_train.drop(columns='street',inplace=True)
    X_train.drop(columns='candidate', inplace=True)

    if do_test:
        X_test = pd.read_csv(path_X_test)
        y_test = pd.read_csv(path_y_test)

    y_test = y_test.correct
    if do_test:
        X_test.drop(columns='street',inplace=True)
        X_test.drop(columns='candidate',inplace=True)

    # Train the model
    model = RandomForestClassifier(n_estimators=1300, criterion = 'gini')
    model.fit(X_train,y_train)

    print('start fitting')
    t1 = time.time()

    dump(model, path_ml)

    # Evaluate model
    if do_test:
        print(confusion_matrix(y_test, model.predict(X_test)))
        print(classification_report(y_test, model.predict(X_test)))
        print(cohen_kappa_score(y_test,model.predict(X_test)))

    t2 = time.time()
    print('Fitting time: {}'.format(t2-t1))


