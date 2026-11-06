from dataclasses import dataclass, field
from typing import List, Optional

Player = str # ["white", "black"]
Square = tuple[int, int] # [0, 0] to [7, 7]

@dataclass 
class PieceStats:
    moves: int = 0
    captures: int = 0
    checks_participated: int = 0
    checkmates_participated: int =0

@dataclass(frozen=True)
class PieceDefinition:
    id: int
    name: str
    type: str # Either "Commoner", or "Noble"
    cost: int
    movement: str
    traits: list[str] = field(default_factory=list)
    drawbacks: list[str] = field(default_factory=list)
    is_king_status: bool=False

@dataclass
class PieceInstance:
    definition: PieceDefinition
    owner: Player
    position: Square

    has_moved: bool = False
    shield_charges: int = 0

    # Permanent identity fields
    instance_number: int = 0
    instance_id: str = ""
    starting_position: Square | None = None
    original_piece_name: str = ""

    # Per-piece simulation statistics
    stats: PieceStats = field(default_factory=PieceStats)

    # Existing or future state
    is_captured: bool = False
    is_in_queen_spot: bool = False
    starting_class: str = ""
    is_noble: bool = False

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def color(self) -> Player:
        return self.owner

    @property
    def piece_id(self) -> int:
        return self.definition.id

    def __post_init__(self) -> None:
        if "shield" in self.definition.traits:
            self.shield_charges = 1

        if self.starting_position is None:
            self.starting_position = self.position

        if not self.original_piece_name:
            self.original_piece_name = self.definition.name