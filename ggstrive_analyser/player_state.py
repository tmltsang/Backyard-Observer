from dataclasses import dataclass, field

@dataclass
class PlayerState:
    round_count: int = field(default = 0)
    health: float = field(default = 100.0)
    tension: float = field(default = 0.0)
    burst: float = field(default = 100.0)
    risc: float = field(default = 0.0)