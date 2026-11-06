
from src.models import PieceInstance
from src.board import Board

def get_swap_moves_for_piece(board:Board, piece:PieceInstance):
    if not can_swap_piece(piece):
        return []
    swaps = []
    for square, other_piece in board.squares.items():
        if other_piece.owner != piece.owner:
            continue
        if other_piece == piece:
            continue
        if not can_swap_piece(other_piece):
            continue

        swaps.append((piece.position, square))
    return swaps

def can_swap_piece(piece:PieceInstance):
    return "swap" in piece.definition.traits


def execute_swap(board:Board, from_square:tuple[int, int], to_square:tuple[int, int]):
    piece = board.get_piece_at(from_square)
    other_piece = board.get_piece_at(to_square)
    if piece is None:
        raise ValueError(f"no piece at {from_square}")
    if other_piece is None:
        raise ValueError(f"no piece to swap with at {to_square}")
    if piece.owner != other_piece.owner:
        raise ValueError("cannot swap with enemy piece")
    if not can_swap_piece(piece):
        raise ValueError(f"{piece.name} cannot swap")
    board.squares[from_square] = other_piece
    board.squares[to_square] = piece
    piece.position = to_square
    other_piece.position = from_square
    piece.has_moved = True

    return {
        "swap_used": True,
        "swapped_with": other_piece.name,
        "swapped_with_id": other_piece.definition.id,
        "swapped_with_instance_id": other_piece.instance_id,
        "swapped_from_square": to_square,
        "swapped_to_square": from_square,
    }

def can_leap(piece):
    return "leap" in piece.definition.traits

def leap_cannot_capture(piece):
    return "cannot_capture_after_leap" in piece.definition.drawbacks


def can_land_with_leap(board:Board, piece:PieceInstance, target_square:tuple[int, int]):
    if not board.is_square_on_board(target_square):
        return False
    target_piece = board.get_piece_at(target_square)
    if target_piece is None:
        return True
    if target_piece.owner == piece.owner:
        return False
    if leap_cannot_capture(piece):
        return False
    return True

def get_knight_style_leap_moves(board:Board, piece:PieceInstance):
    row, col = piece.position
    offsets = [
        (2, 1), (2, -1),
        (-2, 1), (-2, -1),
        (1, 2), (1, -2),
        (-1, 2), (-1, -2),
    ]
    leap_moves = []
    for row_step, col_step in offsets:
        target_square = (row+row_step, col + col_step)
        if not can_land_with_leap(board, piece, target_square):
            continue
        leap_moves.append((piece.position, target_square))
    return leap_moves

def get_diagonal_exact_leap_moves(board:Board, piece:PieceInstance, distance:int):
    row, col = piece.position
    directions = [
        (1, 1), (1, -1),
        (-1, 1), (-1, -1),
    ]
    leap_moves = []
    for row_step, col_step in directions:
        target_square = (row+row_step*distance, col+col_step*distance)
        if not can_land_with_leap(board, piece, target_square):
            continue
        leap_moves.append((piece.position, target_square))
    return leap_moves

def get_orthogonal_limited_leap_moves(board:Board, piece:PieceInstance, distances:list[int]):
    row, col = piece.position
    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
    ]
    leap_moves = []
    for row_step, col_step in directions:
        for distance in distances:
            target_square = (row+row_step*distance, col+col_step*distance)
            if not can_land_with_leap(board, piece, target_square):
                continue
            leap_moves.append((piece.position, target_square))
    return leap_moves

def get_lance_rider_leap_moves(board:Board, piece:PieceInstance):
    leap_moves = []
    leap_moves.extend(get_knight_style_leap_moves(board, piece))
    row, col = piece.position
    direction = 1 if piece.owner == "white" else -1
    target_square = (row+direction*3, col)
    if can_land_with_leap(board, piece, target_square):
        leap_moves.append((piece.position, target_square))
    return list(dict.fromkeys(leap_moves))

def get_leap_moves_for_piece(board:Board, piece:PieceInstance):
    if not can_leap(piece):
        return []
    
    if piece.name in {"wild stallion", "pegasus"}:
        return get_knight_style_leap_moves(board, piece)
    if piece.name == "clergy riders":
        return get_diagonal_exact_leap_moves(board, piece, distance=2)
    if piece.name == "lance rider":
        return get_lance_rider_leap_moves(board, piece)
    if piece.name == "fast chariot":
        return get_orthogonal_limited_leap_moves(board, piece, distances=[2, 3])

    return []

def execute_leap(board:Board, from_square:tuple[int, int], to_square:tuple[int, int]):
    piece:PieceInstance = board.get_piece_at(from_square)
    if piece is None:
        raise ValueError(f"No piece at {from_square}")
    if not can_leap(piece):
        raise ValueError(f"Uh {piece.name} cannot leap")
    if not can_land_with_leap(board, piece, to_square):
        raise ValueError(f"{piece.name} cannot leap to {to_square}")
    target_piece = board.get_piece_at(to_square)
    board.move_piece(from_square, to_square)
    return {
        "leap_used": True,
        "leap_captured": target_piece.name if target_piece else None,
        "leap_captured_id": target_piece.definition.id if target_piece else None,
        "leap_captured_cost": target_piece.definition.cost if target_piece else 0,
    }

def can_be_moved_by_opponent(piece:PieceInstance) -> bool:
    return "opponent_controlled" in piece.definition.traits

def get_opponent_control_moves_for_piece(board:Board, piece:PieceInstance, controller:str):
    if not can_be_moved_by_opponent(piece):
        return []
    if piece.owner == controller:
        return []
    row, col = piece.position
    offsets = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
    ]

    moves = []

    for row_step, col_step in offsets:
        target_square = (row+row_step, col+col_step)
        if not board.is_square_on_board(target_square):
            continue
        if not board.is_square_empty(target_square):
            continue
        moves.append((piece.position, target_square))
    return moves


def execute_opponent_control_move(board: Board,from_square: tuple[int, int],to_square: tuple[int, int],controller: str):
    piece = board.get_piece_at(from_square)
    if piece is None:
        raise ValueError(f"No piece at {from_square}")
    if not can_be_moved_by_opponent(piece):
        raise ValueError(f"{piece.name} can't be moved by opponent")
    if piece.owner == controller:
        raise ValueError(f"owner cannot use opponent-control movement")
    if not board.is_square_on_board(to_square):
        raise ValueError(f"{to_square} is off the board")
    target_piece = board.get_piece_at(to_square)
    if target_piece is not None:
        raise ValueError(f"Cannot captue or move into occupied square while using opponent controlled piece!")

    from_row, from_col = from_square
    to_row, to_col = to_square

    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    is_one_square_orthogonal = (
        (row_diff == 1 and col_diff == 0)
        or (row_diff == 0 and col_diff == 1)
    )
    if not is_one_square_orthogonal:
        raise ValueError(f"Can only move 1 sq vertically or horizontally for opponent controlled corrupted abot")

    board.move_piece(from_square, to_square)

    return {
        "opponent_control_used": True,
        "controlled_piece": piece.name,
        "controlled_piece_id": piece.definition.id,
        "controlled_piece_owner": piece.owner,
        "controlled_piece_instance_id": piece.instance_id,
        "controlled_piece_instance_number": piece.instance_number,
    }

