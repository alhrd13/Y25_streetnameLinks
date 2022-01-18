from joblib import dump, load
import pandas as pd
import time
from pandas import DataFrame
from sklearn.metrics import classification_report, confusion_matrix, cohen_kappa_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

# Load the training and test dataset
X_train = pd.read_csv('gt_X_train.csv')
y_train = pd.read_csv('gt_y_train.csv')
y_train = y_train.correct
X_train.drop(columns='street',inplace=True)
X_train.drop(columns='candidate', inplace=True)

X_test = pd.read_csv('gt_X_test.csv')
y_test = pd.read_csv('gt_y_test.csv')

y_test = y_test.correct
X_test.drop(columns='street',inplace=True)
X_test.drop(columns='candidate',inplace=True)

# Train the model
model = RandomForestClassifier(n_estimators=1300, criterion = 'gini')
model.fit(X_train,y_train)

print('start fitting')
t1 = time.time()

dump(model, 'rfc_1300.joblib')

# Evaluate model
print(confusion_matrix(y_test, model.predict(X_test)))
print(classification_report(y_test, model.predict(X_test)))
print(cohen_kappa_score(y_test,model.predict(X_test)))

t2 = time.time()
print('Fitting time: {}'.format(t2-t1))


