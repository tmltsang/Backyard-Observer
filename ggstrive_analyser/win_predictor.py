import os
import pandas as pd
from game_state import GameState
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
)

#Predicts the round or set win given current state
class WinPredictor:
    cfg: dict
    round_model:  GaussianNB
    set_model: GaussianNB

    def __init__(self, cfg: dict):
        self.cfg = cfg
        #read the path
        cwd = os.path.abspath(self.cfg['csv_path'])
        #list all the files from the directory
        file_list = os.listdir(cwd)

        df = pd.concat([pd.read_csv(self.cfg['csv_path'] + '/' + f) for f in file_list ], ignore_index=True)

        round_feature_cols = self.cfg['pred_round_features']
        round_x = df.loc[:, round_feature_cols]

        set_feature_cols = self.cfg['pred_set_features']
        set_x = df.loc[:, set_feature_cols]

        df[self.cfg['prod_round_win_field']] = df[self.cfg['prod_round_win_field']].astype('bool')
        round_y = df[self.cfg['prod_round_win_field']]

        df[self.cfg['prod_set_win_field']] = df[self.cfg['prod_set_win_field']].astype('bool')
        set_y = df[self.cfg['prod_set_win_field']]

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

    def predict_win_round(self, current_state: GameState):
        feature_x = []
        for feature in self.cfg['pred_round_features']:
            feature_x.append(current_state.flatten()[feature])
        return self.round_model.predict([feature_x])
    
    def predict_win_set(self, current_state: GameState):
        return self.set_model.predict([pd.array(list(current_state.flatten().values()))])
