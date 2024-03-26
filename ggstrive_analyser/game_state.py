from player_state import PlayerState
from dataclasses import fields

class GameState:

    def __init__(self, time = 0, p1: PlayerState = PlayerState(), p2: PlayerState = PlayerState()):
        self.time = time
        self.p1 = p1
        self.p2 = p2

    def flatten(self) -> dict:
        game_state_dict = {'time': self.time}
        for field in fields(PlayerState):
            game_state_dict['p1_' + field.name ] = getattr(self.p1, field.name)
            game_state_dict['p2_' + field.name ] = getattr(self.p2, field.name)
        return game_state_dict