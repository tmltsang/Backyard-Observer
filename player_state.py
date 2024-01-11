from dataclasses import dataclass

@dataclass
class PlayerState:
    rounds_won: int
    sets_won: int
    health: float
    tension: float
    burst: float
    risk: float