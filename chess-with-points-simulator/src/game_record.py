from dataclasses import dataclass, field

@dataclass
class MoveRecord:
    turn: int
    player: str
    piece: str
    piece_id: int
    piece_cost: int

    piece_instance_id:str
    piece_instance_number:int

    from_square: tuple[int, int]
    to_square: tuple[int, int]
    captured: str | None = None
    captured_piece_id: int | None = None
    captured_piece_cost: int = 0

    captured_piece_instance_id: str | None = None
    captured_piece_instance_number:int | None = None

    created_check: bool = False
    created_checkmate: bool = False
    legal_move_count: int = 0

    promoted_from:str | None=None
    promoted_from_id:int | None=None
    promoted_to:str | None=None
    promoted_to_id:int | None=None

    shield_blocks_used: int = 0
    shield_events: list[dict] = field(default_factory=list)

    swap_used: bool = False
    swapped_with: str | None = None
    swapped_with_id: int | None = None
    swapped_from_square: tuple[int, int] | None = None
    swapped_to_square: tuple[int, int] | None = None
    swapped_with_instance_id: str | None = None


    leap_used: bool = False
    leap_captured: str | None = None
    leap_captured_id: int | None = None
    leap_captured_cost: int = 0

    opponent_control_used: bool = False
    controlled_piece: str | None = None
    controlled_piece_id: int | None = None
    controlled_piece_owner: str | None = None
    controlled_piece_instance_id: str | None = None
    controlled_piece_instance_number: int | None = None

    san_disambiguation: str = ""

@dataclass
class GameRecord:
    winner: str | None = None
    seed: int =0
    reason: str = ""
    total_moves: int = 0
    captures: list[MoveRecord] = field(default_factory=list)
    checks: list[MoveRecord] = field(default_factory=list)
    checkmates: list[MoveRecord] = field(default_factory=list)
    promotions: list[MoveRecord] = field(default_factory=list)
    shield_blocks: list[MoveRecord] = field(default_factory=list)
    move_history: list[MoveRecord] = field(default_factory=list)
    surviving_piece_ids: list[int] = field(default_factory=list)
    surviving_piece_instance_ids: list[str] = field(
        default_factory=list
    )
    swaps: list[MoveRecord] = field(default_factory=list)
    leaps: list[MoveRecord] = field(default_factory=list)
    opponent_control_moves: list[MoveRecord] = field(default_factory=list)
    starting_noble_line: dict[str, list[int]] = field(default_factory=dict)
    starting_commoner_line: dict[str, list[int]] = field(default_factory=dict)
    
    starting_piece_instances: dict[str, list[dict]] = field(
        default_factory=dict
    )
    starting_piece_instance_ids: list[str] = field(default_factory=list)
    

    def log_move(self, move: MoveRecord) -> None:
        self.move_history.append(move)
        self.total_moves += 1

        if move.captured is not None:
            self.captures.append(move)

        if move.created_check:
            self.checks.append(move)

        if move.created_checkmate:
            self.checkmates.append(move)
        
        if move.promoted_to is not None:
            self.promotions.append(move)
        
        if move.shield_blocks_used > 0 :
            self.shield_blocks.append(move)

        if move.swap_used:
            self.swaps.append(move)
        
        if move.leap_used:
            self.leaps.append(move)

        if move.opponent_control_used:
            self.opponent_control_moves.append(move)