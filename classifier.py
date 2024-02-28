import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
)

#read the path
cwd = os.path.abspath('csv/')
#list all the files from the directory
file_list = os.listdir(cwd)

df = pd.concat([pd.read_csv('csv/' + f) for f in file_list ], ignore_index=True)

feature_cols = ['p1_health', 'p2_health', 'p1_tension', 'p2_tension', 'p1_burst', 'p2_burst', 'p1_risc', 'p2_risc']
x = df.loc[:, feature_cols]

set_feature_cols = ['p1_health', 'p2_health', 'p1_tension', 'p2_tension', 'p1_burst', 'p2_burst', 'p1_risc', 'p2_risc', 'p1_round_win', 'p2_round_win']
set_x = df.loc[:, feature_cols]

df['p1_round_win'] = df['p1_round_win'].astype('bool')
y = df.p1_round_win

df['p1_set_win'] = df['p1_set_win'].astype('bool')
set_y = df.p1_set_win


x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.33, random_state=125
)

set_x_train, set_x_test, set_y_train, set_y_test = train_test_split(
    set_x, set_y, test_size=0.33, random_state=125
)

model = GaussianNB()

model.fit(x_train, y_train)

set_model = GaussianNB()

set_model.fit(set_x_train, set_y_train)
predicted = model.predict(set_x_test.iloc[[100]])

print("Actual Value:", set_y_test.iloc[[100]])
print("Predicted Value:", predicted[0])

y_pred = model.predict(x_test)
accuray = accuracy_score(y_pred, y_test)
f1 = f1_score(y_pred, y_test, average="weighted")

print("Accuracy:", accuray)
print("F1 Score:", f1)

set_y_pred = model.predict(set_x_test)
accuray = accuracy_score(set_y_pred, set_y_test)
f1 = f1_score(set_y_pred, set_y_test, average="weighted")

print("Accuracy:", accuray)
print("F1 Score:", f1)