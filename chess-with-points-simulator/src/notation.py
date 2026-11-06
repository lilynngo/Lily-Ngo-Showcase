from src.game_record import MoveRecord
from src.rules import get_legal_moves
from src.board import Board
from src.models import PieceInstance, Square


COLUMN_NAMES = "abcdefgh"

def square_to_chess(square: tuple[int, int]) :
    row, col = square

    if not (
        0 <= row <= 7
        and 0 <= col <= 7
    ):
        raise ValueError(
            f"Invalid chess square: {square}"
        )

    return f"{COLUMN_NAMES[col]}{row + 1}"

def move_to_notation(move:MoveRecord):
    destination = square_to_chess(
        move.to_square
    )
    san_disambiguation = move.san_disambiguation
    symbol = piece_symbol(move.piece)

    is_capture = (
        move.captured_piece_id is not None
        or move.leap_captured_id is not None
    )

    if move.swap_used:
        other = piece_symbol(
            move.swapped_with or "piece"
        )
        notation = (
            f"{symbol}↔{other}@{destination}"
        )

    elif move.opponent_control_used:
        controlled = piece_symbol(
            move.controlled_piece or move.piece
        )
        notation = (
            f"{controlled}>{destination}"
        )

    elif symbol == "":
        if is_capture:
            source_file = COLUMN_NAMES[
                move.from_square[1]
            ]
            notation = (
                f"{source_file}x{destination}"
            )
        else:
            notation = destination

    else:
        capture_marker = "x" if is_capture else ""
        disambiguation = san_disambiguation

        notation = (
            f"{symbol}"
            f"{disambiguation}"
            f"{capture_marker}"
            f"{destination}"
        )

    if move.promoted_to:
        notation += (
            f"={piece_symbol(move.promoted_to)}"
        )
    shield_blocks_used = getattr(
        move,
        "shield_blocks_used",
        0,
    )
    if shield_blocks_used == 1:
        notation += "[shield]"
    elif shield_blocks_used > 1:
        notation += f"[shield×{shield_blocks_used}]"
    shield_events = getattr(
        move,
        "shield_events",
        [],
    )

    if shield_events:
        blocked_attempts = [
            shield_event_to_notation(event)
            for event in shield_events
        ]

        notation = (
            " ".join(blocked_attempts)
            + " → "
            + notation
        )
        
    if getattr(move, "leap_used", False):
        notation += "[leap]"   
    if move.created_checkmate:
        notation += "#"
    elif move.created_check:
        notation += "+"

    return notation
def shield_event_to_notation(event: dict) -> str:
    blocked_capture = format_blocked_capture(event)

    blocker_name = event.get(
        "protected_piece",
        "shield bearer",
    )
    blocker_symbol = piece_symbol(blocker_name)

    return (
        f"{blocked_capture}"
        f"{{blocked by {blocker_symbol}}}"
    )

def format_blocked_capture(event: dict) -> str:
    piece_name = event["attacking_piece"].lower()
    from_square = event["blocked_from_square"]
    to_square = event["blocked_to_square"]

    from_row, from_col = from_square
    to_row, to_col = to_square

    destination = square_to_notation(to_square)

    if piece_name == "pawn":
        source_file = chr(ord("a") + from_col)
        return f"{source_file}x{destination}"

    symbol = piece_symbol(piece_name)
    return f"{symbol}x{destination}"
def square_to_notation(square: Square) -> str:

    row, col = square

    if not (0 <= row <= 7 and 0 <= col <= 7):
        raise ValueError(f"Invalid board square: {square}")

    file_letter = chr(ord("a") + col)
    rank_number = row + 1

    return f"{file_letter}{rank_number}"

def piece_symbol(piece_name: str) -> str:
    symbols = {
        "king": "K",
        "queen": "Q",
        "rook": "R",
        "bishop": "B",
        "knight": "N",
        "pawn": "",

        # Custom pieces.
        "squire": "Sq",
        "shield bearer": "SB",
        "peasant": "P",
        "adept": "A",
        "mule": "M",
        "wild stallion": "WS",
        "clergy riders": "CR",
        "lance rider": "LR",
        "pegasus": "Pg",
        "high priest": "HP",
        "corrupted abbot": "CA",
        "arcane priest": "AP",
        "damaged chariot": "DC",
        "fast chariot": "FC",
        "armored chariot": "AC",
        "arcane tower": "AT",
        "sorceress": "S",
        "joan of arc": "JA",
        "queen of air": "QA",
        "queen of darkness": "QD",
        "the old queen": "OQ",
    }

    return symbols.get(piece_name, piece_name[:2].upper())

def build_game_notation(move_history: list) :
    parts: list[str] = []

    for index, move in enumerate(move_history):
        notation = move_to_notation(move)

        if index % 2 == 0:
            move_number = index // 2 + 1
            parts.append(
                f"{move_number}. {notation}"
            )
        else:
            parts.append(notation)

    return " ".join(parts)

def get_san_disambiguation(
    board: Board,
    moving_piece: PieceInstance,
    from_square: Square,
    to_square: Square,
) -> str:
    piece_name = moving_piece.definition.name

    # Pawns have their own capture-file notation.
    # Kings cannot require standard SAN disambiguation.
    if piece_name in {"pawn", "king"}:
        return ""

    competitors: list[PieceInstance] = []

    for row in range(8):
        for col in range(8):
            other = board.get_piece_at((row, col))

            if other is None:
                continue

            if other is moving_piece:
                continue

            if other.owner != moving_piece.owner:
                continue

            if other.definition.name != piece_name:
                continue

            if other.is_captured:
                continue

            # Replace this with your actual legal-move function.
            other_moves = get_legal_moves(board, other)

            if to_square in other_moves:
                competitors.append(other)

    if not competitors:
        return ""

    from_row, from_col = from_square

    same_file = any(
        other.position[1] == from_col
        for other in competitors
    )

    same_rank = any(
        other.position[0] == from_row
        for other in competitors
    )

    source_file = COLUMN_NAMES[from_col]
    source_rank = str(from_row + 1)

    if not same_file:
        return source_file

    if not same_rank:
        return source_rank

    return source_file + source_rank