from player_state import PlayerState
from dataclasses import fields
from win_state import WinState

class GameState:
    time: float
    round_win_state: WinState
    set_win_state: WinState
    p1: PlayerState
    p2: PlayerState

    def __init__(self, time = 0, round_win_state = WinState.NO_WIN, set_win_state = WinState.NO_WIN, p1: PlayerState = PlayerState(), p2: PlayerState = PlayerState()):
        self.time = time
        self.round_win_state = round_win_state
        self.set_win_state = set_win_state
        self.p1 = p1
        self.p2 = p2
    
    def determine_win_state(self, curr_round_win_state: WinState):
        self.round_win_state = curr_round_win_state
        if curr_round_win_state != WinState.NO_WIN:
            # Set is won if current win_state and round_count == 1 
            if curr_round_win_state == WinState.P1_WIN and self.p1.round_count == 1:
                self.set_win_state = WinState.P1_WIN
            elif curr_round_win_state == WinState.P2_WIN and self.p2.round_count == 1:
                self.set_win_state = WinState.P2_WIN
            else:
                self.set_win_state = WinState.NO_WIN
        else:
            self.set_win_state = WinState.NO_WIN

    def flatten(self) -> dict:
        game_state_dict = {'time': self.time}
        for field in fields(PlayerState):
            game_state_dict['p1_' + field.name ] = getattr(self.p1, field.name)
            game_state_dict['p2_' + field.name ] = getattr(self.p2, field.name)
        return game_state_dict