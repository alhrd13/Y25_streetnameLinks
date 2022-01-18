from joblib import load
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, cohen_kappa_score

df = pd.read_csv('ml_gt_data.csv', index_col=0)
# Set input & output, split into training & test
y = df.correct
X = df.drop('correct',axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.1)

with open('gt_X_train.csv', 'w') as output:
    X_train.to_csv(output, header=True)
with open('gt_X_test.csv', 'w') as output:
    X_test.to_csv(output, header=True)
with open('gt_y_train.csv', 'w') as output:
    y_train.to_csv(output, header=True)
with open('gt_y_test.csv', 'w') as output:
    y_test.to_csv(output, header=True)
