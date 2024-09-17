from dataclasses import dataclass, field

@dataclass
class PlayerState:
    round_count: int = field(default = 0)
    health: float = field(default = 1.0)
    tension: float = field(default = 0.0)
    burst: float = field(default = 1.0)
    risc: float = field(default = 0.0)
    counter: int = field(default = 0)
    reversal: int = field(default = 0)
    just: int = field(default = 0)
    punish: int = field(default = 0)
    curr_damaged: bool = field(default = False)
    name: str = field(default="")

    def __post_init__(self):
        self.health = round(self.health, 5)
        self.tension = round(self.tension, 5)
        self.burst = round(self.burst, 5)
        self.risc= round(self.risc, 5)