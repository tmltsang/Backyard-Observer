from game_state import GameState
from win_state import WinState

class TournamentIndexManager():
    round_index: int
    set_index: int
    base_set_time: float
    set_time: float
    p1_player_name: str
    p2_player_name: str
    tournament_round: str
    tournament: str

    def __init__(self, p1_player_name, p2_player_name, tournament_round, tournament):
        self.p1_player_name = p1_player_name
        self.p2_player_name = p2_player_name
        self.tournament_round = tournament_round
        self.tournament = tournament
        self.round_index = 0
        self.set_index = 0
        self.base_set_time = 0
        self._set_time = 0

    def update_set_time(self, current_state: GameState):
        self.set_time = self.base_set_time + current_state.time

    def update(self, current_state: GameState):
        if current_state.round_win_state != WinState.NO_WIN:
            self.round_index += 1
            self.base_set_time += current_state.time

        if current_state.set_win_state != WinState.NO_WIN:
            self.set_index += 1
            self.round_index = 0
            self.base_set_time = 0

    def add_tr_data(self, dict: dict):
        dict["round_index"] = self.round_index
        dict["set_index"] = self.set_index
        dict['set_time'] = self.set_time
        dict["p1_player_name"] = self.p1_player_name
        dict["p2_player_name"] = self.p2_player_name
        dict["tournament_round"] = self.tournament_round
        dict["tournament"] = self.tournament
        return dict