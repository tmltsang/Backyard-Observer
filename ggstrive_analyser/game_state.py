
from player_state import PlayerState

class GameState:

    def __init__(self, frame_count = 0, p1: PlayerState = PlayerState(), p2: PlayerState = PlayerState()):
        self.frame_count = frame_count
        self.p1 = p1
        self.p2 = p2
    
    def flatten(self):
        return {'frame': self.frame_count, 'p1_health': self.p1.health, 'p2_health': self.p2.health, 
                                                    'p1_tension': self.p1.tension, 'p2_tension': self.p2.tension, 
                                                    'p1_risc': self.p1.risc, 'p2_risc': self.p2.risc, 
                                                    'p1_burst': self.p1.burst, 'p2_burst': self.p2.burst,
                                                    'p1_round_count': self.p1.round_count, 'p2_round_count': self.p2.round_count}