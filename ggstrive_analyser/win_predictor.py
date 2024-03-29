import os
import pandas as pd
from game_state import GameState
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn import preprocessing
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
)
from config import Config

#Predicts the round or set win given current state
class WinPredictor:
    cfg: Config
    round_model:  GaussianNB
    set_model: GaussianNB
    name_le: preprocessing.LabelEncoder

    def __init__(self, cfg: Config):
        self.cfg = cfg
        #read the path
        cwd = os.path.abspath(self.cfg.get('csv_path'))
        #list all the files from the directory
        file_list = os.listdir(cwd)

        df = pd.concat([pd.read_csv(self.cfg.get('csv_path') + '/' + f) for f in file_list ], ignore_index=True)

        self.le = preprocessing.LabelEncoder()
        self.le.fit(pd.concat([df.p1_name, df.p2_name]))
        df.p1_name = self.le.transform(df.p1_name)
        df.p2_name = self.le.transform(df.p2_name)

        round_feature_cols = self.cfg.get('pred_round_features')
        round_x = df.loc[:, round_feature_cols]

        set_feature_cols = self.cfg.get('pred_set_features')
        set_x = df.loc[:, set_feature_cols]

        df[self.cfg.get('prod_round_win_field')] = df[self.cfg.get('prod_round_win_field')].astype('bool')
        round_y = df[self.cfg.get('prod_round_win_field')]

        df[self.cfg.get('prod_set_win_field')] = df[self.cfg.get('prod_set_win_field')].astype('bool')
        set_y = df[self.cfg.get('prod_set_win_field')]

        round_x_train, _, round_y_train, _ = train_test_split(
            round_x, round_y, test_size=0.33, random_state=125
        )

        set_x_train, _, set_y_train, _ = train_test_split(
            set_x, set_y, test_size=0.33, random_state=125
        )

        self.round_model = GaussianNB()

        self.round_model.fit(round_x_train, round_y_train)

        self.set_model = GaussianNB()

        self.set_model.fit(set_x_train, set_y_train)

        #predicted = model.predict(set_x_test.iloc[[100]])

    def __name_transform(self, df: pd.DataFrame):
        df.p1_name = self.le.transform(df.p1_name)
        df.p2_name = self.le.transform(df.p2_name)
        return df

    def predict_win_round(self, current_state: GameState):
        df= pd.DataFrame([current_state.flatten()])
        df = self.__name_transform(df)
        round_feature_cols = self.cfg,get('pred_round_features')
        current_x = df.loc[:, round_feature_cols]
        #print(current_x)
        #print(self.round_model.predict_proba(current_x))
        return self.round_model.predict_proba(current_x)
    
    def predict_win_set(self, current_state: GameState):
        df= pd.DataFrame([current_state.flatten()])
        df = self.__name_transform(df)
        set_feature_cols = self.cfg.get('pred_set_features')
        current_x = df.loc[:, set_feature_cols]
        # print(current_x)
        # print(self.set_model.predict_proba(current_x))
        return self.set_model.predict_proba(current_x)
