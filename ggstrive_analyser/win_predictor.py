import pandas as pd
import pickle
from game_state import GameState
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn import preprocessing
from config import Config

#Predicts the round or set win given current state
class WinPredictor:
    round_model:  MLPClassifier
    set_model: MLPClassifier
    name_le: preprocessing.LabelEncoder

    def __init__(self):
        print(Config.get('round_model_path'))
        with open(Config.get('round_model_path'), "rb") as f:
            self.round_model = pickle.load(f)

        with open(Config.get('set_model_path'), "rb") as f:
            self.set_model = pickle.load(f)

    def predict_win_round(self, current_state: GameState):
        df= pd.DataFrame([current_state.flatten()])
        round_feature_cols = Config.get('pred_round_features')
        current_x = df.loc[:, round_feature_cols]
        return self.round_model.predict_proba(current_x)

    def predict_win_set(self, current_round_pred: float, current_state: GameState):
        df= pd.DataFrame([current_state.flatten()])

        set_feature_cols = Config.get('pred_set_features')
        current_x = df.loc[:, set_feature_cols]
        current_x['current_round_pred'] = current_round_pred
        return self.set_model.predict_proba(current_x)
