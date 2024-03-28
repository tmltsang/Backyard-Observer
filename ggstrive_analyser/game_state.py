from player_state import PlayerState
from dataclasses import fields
from win_state import WinState

class GameState:
    time: float
    win_state: WinState
    p1: PlayerState
    p2: PlayerState

    def __init__(self, time = 0, win_state = WinState.NO_WIN, p1: PlayerState = PlayerState(), p2: PlayerState = PlayerState()):
        self.time = time
        self.win_state = win_state
        self.p1 = p1
        self.p2 = p2

    def flatten(self) -> dict:
        game_state_dict = {'time': self.time}
        for field in fields(PlayerState):
            game_state_dict['p1_' + field.name ] = getattr(self.p1, field.name)
            game_state_dict['p2_' + field.name ] = getattr(self.p2, field.name)
        return game_state_dict