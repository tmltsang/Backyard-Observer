import os
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn import preprocessing
from sklearn.inspection import permutation_importance
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
)

csv_path = "csv/gg_matches"
cwd = os.path.abspath(csv_path)
#list all the files from the directory
full_list = os.listdir(cwd)
file_list = [f for f in full_list if os.path.isfile(os.path.join(csv_path, f))]
df = pd.concat([pd.read_csv(csv_path + '/' + f) for f in file_list], ignore_index=True)

le = preprocessing.LabelEncoder()
le.fit(pd.concat([df.p1_name, df.p2_name]))
df.p1_name = le.transform(df.p1_name)
df.p2_name = le.transform(df.p2_name)
df["p1_round_win"] = df["p1_round_win"].astype('bool')
df["p1_set_win"] = df["p1_set_win"].astype('bool')

est = KBinsDiscretizer(n_bins=20, encode='ordinal', strategy='uniform')
bars = [ 'p1_health', 'p2_health',
              'p1_tension', 'p2_tension',
              'p1_burst', 'p2_burst',
              'p1_risc', 'p2_risc',]
df[bars] = est.fit_transform(df[bars])
#Shuffle dataset
print(df.shape)
df = df.sample(frac=1)
round_feature_cols = [
              'p1_name', 'p2_name',
              'p1_health', 'p2_health',
              'p1_tension', 'p2_tension',
              'p1_burst', 'p2_burst',
              'p1_risc', 'p2_risc',
              'p1_counter', 'p2_counter',
              'p1_curr_damaged', 'p2_curr_damaged', "p1_round_win"]

round = df.loc[:, round_feature_cols]
round = round.drop_duplicates().sample(n=100000)
round_x = round.drop(columns='p1_round_win')
round_y = round["p1_round_win"]


set_feature_cols = [
              'p1_name', 'p2_name',
              'p1_health', 'p2_health',
              'p1_tension', 'p2_tension',
              'p1_burst', 'p2_burst',
              'p1_risc', 'p2_risc',
              'p1_round_count', 'p2_round_count',
              'p1_counter', 'p2_counter',
              'p1_curr_damaged', 'p2_curr_damaged']
set_x = df.loc[:, set_feature_cols]


df["p1_set_win"] = df["p1_set_win"].astype('bool')
set_y = df["p1_set_win"]

round_x_train, round_x_test, round_y_train, round_y_test = train_test_split(
    round_x, round_y, test_size=0.33, random_state=125
)

set_x_train, set_x_test, set_y_train, set_y_test = train_test_split(
    set_x, set_y, test_size=0.33, random_state=125
)
round_model = GaussianNB()
round_svc_model = SVC(random_state=100, kernel='rbf')
round_dtree_model = DecisionTreeClassifier(max_depth=5, random_state=42)

round_svc_model.fit(round_x_train, round_y_train)
round_dtree_model.fit(round_x_train, round_y_train)
round_model.fit(round_x_train, round_y_train)

with open('round_svc.pkl', 'wb') as f:
    pickle.dump(round_svc_model, f)

with open('round_dtree.pkl', 'wb') as f:
    pickle.dump(round_dtree_model, f)

with open('round_gnb.pkl', 'wb') as f:
    pickle.dump(round_model, f)


round_score = round_model.score(round_x_test, round_y_test)
round_svc_score = round_svc_model.score(round_x_test, round_y_test)
round_dtree_score = round_dtree_model.score(round_x_test, round_y_test)

print(round_score)
print(round_svc_score)
print(round_dtree_score)
#print(permutation_importance(round_model, round_x_test, round_y_test))
set_model = GaussianNB()

set_model.fit(set_x_train, set_y_train)
set_score = set_model.score(set_x_test, set_y_test)

#print(set_score)
