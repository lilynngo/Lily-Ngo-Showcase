from dataclasses import dataclass
from itertools import combinations_with_replacement
import random
from src.board import Board
from src.models import PieceDefinition, PieceInstance, Square
from src.moves import is_black_square, is_white_square
from collections import defaultdict

# Constants of the Army
ARMY_BUDGET = 400
REQUIRED_ARMY_SIZE = 16
REQUIRED_COMMONERS = 8
REQUIRED_NOBLES = 8

BOARD_SIZE = 8

@dataclass
class Army:
    pieces: list[PieceDefinition]
    commoners: list[PieceDefinition]
    nobles: list[PieceDefinition]
    name:str

    def total_cost(self):
        return sum(piece.cost for piece in self.pieces)
    
    def count_by_type(self, piece_type:str):
        if piece_type.lower() == "commoner":
            return len(self.commoners)
        elif piece_type.lower() == "noble":
            return len(self.nobles)
    
    def count_by_name(self, piece_name:str):
        return sum(1 for piece in self.pieces if piece.name.lower() == piece_name.lower())
    
    def has_king_status_piece(self):
        return any(piece.is_king_status for piece in self.pieces)
    
    def size(self):
        return len(self.pieces)
    
    def promotion_options(self):
        return [piece for piece in self.pieces if piece.type == "noble" and not piece.is_king_status]

    def best_promotion_option(self):
        options = self.promotion_options()
        if not options:
            return None
        return max(options, key=lambda piece:piece.cost)

def can_start_on_square(piece:PieceDefinition, owner:str, square:tuple[int, int]):
    if piece.name == "queen of air":
        return is_white_square(square)
    if piece.name == "queen of darkness":
        return is_black_square(square)
    return True

def can_piece_fill_role(piece_definition, role: str) -> bool:
    piece_type = piece_definition.type.lower()

    if role == "noble":
        return piece_type in {"noble", "both"}

    if role == "commoner":
        return piece_type in {"commoner", "both"}

    raise ValueError(f"Unknown role: {role}")

def validate_army(army:Army):
    errors = []

    if army.size() != REQUIRED_ARMY_SIZE:
        errors.append(f"Army must have exactly {REQUIRED_ARMY_SIZE} pieces.")

    if army.count_by_type("commoner") != REQUIRED_COMMONERS:
        errors.append(f"Army must have exactly {REQUIRED_COMMONERS} Commoners but found {army.count_by_type("commoner")}.")
    
    if army.count_by_type("noble") != REQUIRED_NOBLES:
        errors.append(f"Army must have exactly {REQUIRED_NOBLES} Nobles but found {army.count_by_type("noble")}.")

    if not army.has_king_status_piece():
        errors.append("Army must have at least one King Status piece.")

    if army.total_cost() > ARMY_BUDGET:
        errors.append(f"Army cost cannot exceed {ARMY_BUDGET}.")
    
    return len(errors) == 0, errors

def generate_army_from_list(piece_definitions:dict[str, PieceDefinition], commoner_pieces: list[str], noble_pieces:list[str], army_name=""):
    pieces = []
    commoners = []
    nobles = []
    for commoner in commoner_pieces:
        commoner:PieceDefinition = piece_definitions[commoner]
        if commoner.type == "commoner" or commoner.type == "both":
            pieces.append(commoner)
            commoners.append(commoner)
        else:
            raise ValueError(f"The {commoner.name} is not a commoner piece.")
    for noble in noble_pieces:
        noble:PieceDefinition = piece_definitions[noble]
        if noble.type == "noble" or noble.type == "both":
            pieces.append(noble)
            nobles.append(noble)
        else:
            raise ValueError(f"The {noble.name} is not a noble piece.")

    return Army(pieces,commoners, nobles, army_name)

def generate_standard_army(piece_definitions:dict[str, PieceDefinition], army_name=""):
    pieces = []
    commoners = []
    nobles = []

    for _ in range(8):
        pieces.append(piece_definitions["pawn"])
        commoners.append(piece_definitions["pawn"])

    pieces.extend([
        piece_definitions["rook"],
        piece_definitions["knight"],
        piece_definitions["bishop"],
        piece_definitions["queen"],
        piece_definitions["king"],
        piece_definitions["bishop"],
        piece_definitions["knight"],
        piece_definitions["rook"],
    ])
    nobles.extend([
        piece_definitions["rook"],
        piece_definitions["knight"],
        piece_definitions["bishop"],
        piece_definitions["queen"],
        piece_definitions["king"],
        piece_definitions["bishop"],
        piece_definitions["knight"],
        piece_definitions["rook"],
    ])
    return Army(pieces, commoners, nobles, army_name)

def generate_group_a_army(piece_definitions:dict[str, PieceDefinition]):
    return Army([
        # 8 Commoners
        piece_definitions["pawn"],
        piece_definitions["squire"],
        piece_definitions["peasant"],
        piece_definitions["shield bearer"],
        piece_definitions["adept"],
        piece_definitions["adept"],
        piece_definitions["pawn"],
        piece_definitions["squire"],

        # 8 Nobles
        piece_definitions["king"],
        piece_definitions["knight"],
        piece_definitions["bishop"],
        piece_definitions["mule"],
        piece_definitions["lance rider"],
        piece_definitions["damaged chariot"],
        piece_definitions["fast chariot"],
        piece_definitions["armored chariot"],
    ])

def generate_legal_standard_armies(
    piece_definitions: dict[str, PieceDefinition],
) -> list[Army]:
    legal_armies = []

    pawn = piece_definitions["pawn"]
    king = piece_definitions["king"]

    noble_options = [
        piece_definitions["knight"],
        piece_definitions["bishop"],
        piece_definitions["rook"],
        piece_definitions["queen"],
    ]

    for noble_group in combinations_with_replacement(noble_options, 7):
        army = Army([
            pawn, pawn, pawn, pawn,
            pawn, pawn, pawn, pawn,
            king,
            *noble_group,
        ])

        is_valid, _ = validate_army(army)

        if is_valid:
            legal_armies.append(army)

    return legal_armies

def get_noble_row(owner: str) -> int:
    if owner == "white":
        return 0
    if owner == "black":
        return 7
    raise ValueError(f"Unknown owner: {owner}")

def get_commoner_row(owner: str) -> int:
    if owner == "white":
        return 1
    if owner == "black":
        return 6
    raise ValueError(f"Unknown owner: {owner}")


def can_start_on_square(piece_definition, square: tuple[int, int]) -> bool:
    if piece_definition.name == "queen of air":
        return is_white_square(square)

    if piece_definition.name == "queen of darkness":
        return is_black_square(square)

    return True

def can_piece_fill_role(piece_definition:PieceDefinition, role:str):
    piece_type = piece_definition.type.lower()
    if role == "noble":
        return piece_type in {"noble", "both"}
    if role == "commoner":
        return piece_type in {"commoner", "both"}
    raise ValueError(f"Unknown role: {role}")

def generate_row_lineup(piece_definitions:list, owner:str, row:int, role:str, rng:random.Random):
    if len(piece_definitions) > BOARD_SIZE:
        raise ValueError(f"Cannot place more than {BOARD_SIZE} in one row")
    for definition in piece_definitions:
        if not can_piece_fill_role(definition, role):
            raise ValueError(
                f"{definition.name} has type '{definition.type}' "
                f"and cannot be used as a {role}."
            )
    available_squares = [(row, col) for col in range(BOARD_SIZE)]
    rng.shuffle(available_squares)
    assignments = []

    for definition in piece_definitions:
        valid_squares = [
            square
            for square in available_squares
            if can_start_on_square(definition, square)
        ]

        if not valid_squares:
            raise ValueError(
                f"No valid starting square for {definition.name} on row {row}."
            )

        square = rng.choice(valid_squares)
        available_squares.remove(square)

        assignments.append({
            "definition": definition,
            "owner": owner,
            "square": square,
            "role": role,
        })

    return assignments

def place_assignments_on_board(board, assignments: list[dict]) -> None:
    for assignment in assignments:
        definition = assignment["definition"]
        owner = assignment["owner"]
        square = assignment["square"]

        piece = PieceInstance(
            definition=definition,
            owner=owner,
            position=square,
        )

        board.place_piece(piece, square)

def get_starting_noble_lineup(assignments: list[dict]) -> list[int]:
    return [
        assignment["definition"].id
        for assignment in assignments
        if assignment["role"] == "noble"
    ]

def assign_piece_instance_ids(board: Board) -> None:
    grouped_pieces: dict[tuple[int, int], list[tuple[Square, PieceInstance]]] = defaultdict(list)

    for square, piece in board.squares.items():
        piece_name = piece.definition.name.lower()
        key = (piece.owner, piece_name)
        grouped_pieces[key].append((square, piece))
    
    for (owner, piece_name), entries in grouped_pieces.items():
        entries.sort(
            key=lambda entry: (
                entry[0][0], entry[0][1]
            )
        )
        for instance_number, (square, piece) in enumerate(entries, start=1):
            safe_piece_name = (piece_name.strip().replace(" ", "_"))

            piece.instance_number = instance_number
            piece.instance_id = (f"{owner}_{safe_piece_name}_{instance_number}")

            piece.starting_position = square
            piece.original_piece_name = piece_name

            piece.starting_class = get_starting_class(
                owner=owner,
                square=square,
            )

            piece.is_noble = (
                piece.starting_class == "noble"
            )

def get_starting_class(
    owner: str,
    square: Square,
) -> str:
    row, _ = square

    if owner == "white":
        if row == 0:
            return "noble"
        if row == 1:
            return "commoner"

    elif owner == "black":
        if row == 7:
            return "noble"
        if row == 6:
            return "commoner"

    return "other"   


def generate_random_army_assignments(nobles: list,commoners: list, owner: str, rng: random.Random | None = None, max_attempts: int = 100) :
    if rng is None:
        rng = random.Random()

    noble_row = get_noble_row(owner)
    commoner_row = get_commoner_row(owner)

    last_error = None

    for _ in range(max_attempts):
        try:
            shuffled_nobles = nobles[:]
            shuffled_commoners = commoners[:]

            rng.shuffle(shuffled_nobles)
            rng.shuffle(shuffled_commoners)

            noble_assignments = generate_row_lineup(
                piece_definitions=shuffled_nobles,
                owner=owner,
                row=noble_row,
                role="noble",
                rng=rng,
            )

            commoner_assignments = generate_row_lineup(
                piece_definitions=shuffled_commoners,
                owner=owner,
                row=commoner_row,
                role="commoner",
                rng=rng,
            )

            return noble_assignments + commoner_assignments

        except ValueError as error:
            last_error = error

    raise ValueError(
        f"Could not generate valid army after {max_attempts} attempts. "
        f"Last error: {last_error}"
    )