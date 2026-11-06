from src.board import Board
from src.models import PieceInstance, Square

def can_move_to(board:Board, piece:PieceInstance, square:Square):
    if not board.is_square_on_board(square):
        return False

    target = board.get_piece_at(square)

    if target is None:
        return True
    
    return target.owner != piece.owner

def get_sliding_moves(
    board: Board,
    piece: PieceInstance,
    directions: list[tuple[int, int]],
) :
    moves = []
    row, col = piece.position

    for row_step, col_step in directions:
        current_row = row + row_step
        current_col = col + col_step

        while board.is_square_on_board((current_row, current_col)):
            square = (current_row, current_col)
            target = board.get_piece_at(square)

            if target is None:
                moves.append(square)
            elif target.owner != piece.owner:
                moves.append(square)
                break
            else:
                break

            current_row += row_step
            current_col += col_step

    return moves

def get_limited_sliding_moves(board:Board, piece:PieceInstance, directions:list[tuple[int, int]], max_distance):
    moves = []
    row, col = piece.position
    for row_step, col_step in directions:
        for distance in range(1, max_distance+1):
            square = (row+row_step*distance, col+col_step*distance)
            if not board.is_square_on_board(square):
                break
            target = board.get_piece_at(square)
            if target is None:
                moves.append(square)
            elif target.owner != piece.owner:
                moves.append(square)
                break
            else:
                break
    return moves

def get_squire_moves(board:Board, piece:PieceInstance):
    moves = []
    row, col = piece.position
    direction = 1 if piece.owner == "white" else -1
    next_row = row + direction
    one_step_forward = (next_row, col)
    if board.is_square_on_board(one_step_forward):
        square = one_step_forward
        target = board.get_piece_at(square)

        if target is None:
            moves.append(square)
        elif target.owner != piece.owner:
            moves.append(square)
    
        
    return moves

def get_peasant_moves(board:Board, piece:PieceInstance):
    moves = []
    row, col = piece.position
    direction = 1 if piece.owner == "white" else -1
    next_row = (row + direction) % 8
    one_step_forward = (next_row, col)
    if board.is_square_empty(one_step_forward):
        moves.append(one_step_forward)
        two_steps_forward = (row+direction*2, col)
        if (not piece.has_moved
            and board.is_square_on_board(two_steps_forward)
            and board.is_square_empty(two_steps_forward)):
            moves.append(two_steps_forward)

    for col_offset in (-1, 1):
        capture_square = (
            next_row,
            col + col_offset,
        )

        if not board.is_square_on_board(capture_square):
            continue

        target = board.get_piece_at(capture_square)

        if (
            target is not None
            and target.owner != piece.owner
        ):
            moves.append(capture_square)

    return moves
    # return get_pawn_moves(board, piece)

def get_mule_moves(board:Board, piece:PieceInstance):
    last_piece = board.get_current_player_last_piece()
    if last_piece:
        if last_piece.lower() == piece.instance_id.lower():
            return []
    return get_limited_sliding_moves(board, piece, [(1, 0), (-1, 0), (0, 1), (0, -1)], max_distance=2)

def get_damaged_chariot_moves(board:Board, piece:PieceInstance):
    return get_limited_sliding_moves(board, piece, [(1, 0), (-1, 0), (0, 1), (0, -1)],max_distance=2)

def get_fast_chariot_moves(board:Board, piece:PieceInstance):
    return get_rook_moves(board, piece)

def get_armored_chariot_moves(board:Board, piece:PieceInstance):
    return get_limited_sliding_moves(board, piece, [(1, 0), (-1, 0), (0, 1), (0, -1)], max_distance=4)

def get_adept_moves(board: Board, piece: PieceInstance):
    moves = []
    row, col = piece.position
    direction = 1 if piece.owner == "white" else -1
    next_row = row + direction
    one_step_forward = (next_row, col)
    if board.is_square_empty(one_step_forward) and board.is_square_on_board(one_step_forward):
        moves.append(one_step_forward)
        
    return moves

def get_wild_stallion_moves(board:Board, piece:PieceInstance):
    return get_knight_moves(board, piece)

def get_clergy_riders_moves(board:Board, piece:PieceInstance):
    moves = []
    row, col = piece.position
    directions = [
        (1, 1), (1, -1),
        (-1, 1), (-1, -1),
    ]
    for row_step, col_step in directions:
        middle_square = (row+row_step, col + col_step)
        target_square = (row+row_step*2, col + col_step*2)
        if not board.is_square_on_board(target_square):
            continue
        if not board.is_square_empty(middle_square):
            continue
        target = board.get_piece_at(target_square)
        if target is None:
            moves.append(target_square)
        elif target.owner != piece.owner:
            moves.append(target_square)
    return moves


def get_lance_rider_moves(board:Board, piece:PieceInstance):
    return []

    # Move the following logic to leap simulation since it's
    # not normal movement!
    # moves = []
    # moves.extend(get_knight_moves(board, piece))
    # row, col = piece.position 
    # direction = 1 if piece.owner == "white" else -1

    # target_square = (row, direction*3, col)
    # if board.is_square_on_board(target_square):
    #     target = board.get_piece_at(target_square)
    #     if target is None:
    #         moves.append(target_square)
    #     elif target.owner != piece.owner:
    #         moves.append(target_square)
    # return list(dict.fromkeys(moves))

def get_pegasus_moves(board:Board, piece:PieceInstance):
    return get_knight_moves(board, piece)

def get_shield_bearer_moves(board:Board, piece:PieceInstance):
    row, col = piece.position
    candidates = []
    for row_step in [-1, 0, 1]:
        for col_step in [-1, 0, 1]:
            if row_step == 0 and col_step == 0:
                continue
            candidates.append((row+row_step, col+col_step))

    moves = []
    for square in candidates:
        if not board.is_square_on_board(square):
            continue
        if board.is_square_empty(square):
            moves.append(square)
    return moves

def get_rook_moves(board: Board, piece: PieceInstance) -> list[Square]:
    return get_sliding_moves(
        board,
        piece,
        [(1, 0), (-1, 0), (0, 1), (0, -1)],
    )

def get_bishop_moves(board: Board, piece: PieceInstance) -> list[Square]:
    return get_sliding_moves(
        board,
        piece,
        [(1, 1), (1, -1), (-1, 1), (-1, -1)],
    )

def get_sorceress_moves(board:Board, piece:PieceInstance):
    moves = []
    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    ]

    for row_step, col_step in directions:
        moves.extend(
            get_sliding_moves_in_direction(
                board,
                piece,
                row_step,
                col_step,
                max_distance=5,
            )
        )

    return list(dict.fromkeys(moves))

def get_sliding_moves_in_direction(
    board: Board,
    piece: PieceInstance,
    row_step: int,
    col_step: int,
    max_distance: int | None = None,
) -> list[Square]:
    moves = []
    row, col = piece.position

    distance = 1

    while True:
        if max_distance is not None and distance > max_distance:
            break

        square = (
            row + row_step * distance,
            col + col_step * distance,
        )

        if not board.is_square_on_board(square):
            break

        target = board.get_piece_at(square)

        if target is None:
            moves.append(square)
            distance += 1
            continue

        if target.owner != piece.owner:
            moves.append(square)

        # Stop after hitting any piece.
        break

    return moves
def get_high_priest_moves(board: Board, piece: PieceInstance) -> list[Square]:
    moves = []
    diagonal_directions = [
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    ]
    for row_step, col_step in diagonal_directions:
        moves.extend(
            get_sliding_moves_in_direction(
                board,
                piece,
                row_step,
                col_step,
                max_distance=3,
            )
        )
    row, col = piece.position
    horizontal_squares = [
        (row, col - 1),
        (row, col + 1),
    ]

    for square in horizontal_squares:
        if not board.is_square_on_board(square):
            continue

        target = board.get_piece_at(square)

        if target is None:
            moves.append(square)
        elif target.owner != piece.owner:
            moves.append(square)

    return list(dict.fromkeys(moves))

def get_arcane_priest_moves(board:Board, piece:PieceInstance):
    moves = []
    diagonal_directions = [
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    ]
    for row_step, col_step in diagonal_directions:
        moves.extend(
            get_sliding_moves_in_direction(
                board,
                piece,
                row_step,
                col_step,
                max_distance=3,
            )
        )
    return list(dict.fromkeys(moves))

def get_queen_moves(board: Board, piece: PieceInstance) -> list[Square]:
    # print(
    #     "QUEEN DEBUG",
    #     piece.name,
    #     "stored position:",
    #     piece.position,
    #     "board position:",
    #     board.get_piece_at(piece.position),
    # )
    return get_rook_moves(board, piece) + get_bishop_moves(board, piece)

def get_knight_moves(board: Board, piece: PieceInstance) -> list[Square]:
    row, col = piece.position

    candidates = [
        (row + 2, col + 1),
        (row + 2, col - 1),
        (row - 2, col + 1),
        (row - 2, col - 1),
        (row + 1, col + 2),
        (row + 1, col - 2),
        (row - 1, col + 2),
        (row - 1, col - 2),
    ]

    return [square for square in candidates if can_move_to(board, piece, square)]

def get_king_moves(board: Board, piece: PieceInstance) -> list[Square]:
    row, col = piece.position
    candidates = []

    for row_step in [-1, 0, 1]:
        for col_step in [-1, 0, 1]:
            if row_step == 0 and col_step == 0:
                continue

            candidates.append((row + row_step, col + col_step))

    return [square for square in candidates if can_move_to(board, piece, square)]

def get_pawn_moves(board: Board, piece: PieceInstance) -> list[Square]:
    moves = []
    row, col = piece.position

    direction = 1 if piece.owner == "white" else -1

    one_step_forward = (row + direction, col)

    if board.is_square_on_board(one_step_forward) and board.is_square_empty(one_step_forward):
        moves.append(one_step_forward)

        #check for two square forward as first move
        two_steps_forward = (row+direction*2, col)
        if(not piece.has_moved and board.is_square_on_board(two_steps_forward) and board.is_square_empty(two_steps_forward)):
            if piece.name == "pawn" or piece.name == "peasant":
                moves.append(two_steps_forward)

    capture_squares = [
        (row + direction, col - 1),
        (row + direction, col + 1),
    ]

    for square in capture_squares:
        if not board.is_square_on_board(square):
            continue

        target = board.get_piece_at(square)

        if target is not None and target.owner != piece.owner:
            moves.append(square)

    return moves

def get_corrupted_abbot_moves(board: Board, piece: PieceInstance) -> list[Square]:
    return get_bishop_moves(board, piece)

def get_arcane_tower_moves(board:Board, piece:PieceInstance):
    return get_limited_sliding_moves(board, piece, [(1, 0), (-1, 0), (0, 1), (0, -1)], max_distance=1)

def get_joan_of_arc_moves(board:Board, piece:PieceInstance):
    return get_queen_moves(board, piece)

def is_white_square(square: Square):
    row, col = square
    return (row + col) % 2 == 1

def is_black_square(square: Square) -> bool:
    return not is_white_square(square)

def get_queen_of_air_moves(board:Board, piece:PieceInstance):
    moves = []
    row, col = piece.position
    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    ]

    for row_step, col_step in directions:
        distance = 1
        while True:
            square = (
                row + row_step * distance,
                col + col_step * distance,
            )
            if not board.is_square_on_board(square):
                break
            target = board.get_piece_at(square)

            if target is None:
                if is_white_square(square):
                    moves.append(square)

                distance += 1
                continue
            if target.owner == piece.owner:
                break
            if is_white_square(square):
                moves.append(square)
            break
    return list(dict.fromkeys(moves))

def get_queen_of_darkness_moves(board:Board, piece:PieceInstance):
    moves = []
    row, col = piece.position
    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    ]
    for row_step, col_step in directions:
        distance = 1
        while True:
            square = (
                row + row_step * distance,
                col + col_step * distance,
            )
            if not board.is_square_on_board(square):
                break
            target = board.get_piece_at(square)
            if target is None:
                if is_black_square(square):
                    moves.append(square)
                distance +=1
                continue
            if target.owner == piece.owner:
                break
            if is_black_square(square):
                moves.append(square)
            break
    return list(dict.fromkeys(moves))
def get_the_old_queen_moves(board: Board, piece: PieceInstance) -> list[Square]:
    return get_queen_moves(board, piece)

def get_pseudo_legal_moves(board: Board, piece: PieceInstance) -> list[Square]:
    movement = piece.definition.movement

    if movement == "rook":
        return get_rook_moves(board, piece)

    if movement == "bishop":
        return get_bishop_moves(board, piece)

    if movement == "queen":
        return get_queen_moves(board, piece)

    if movement == "knight":
        return get_knight_moves(board, piece)

    if movement == "king":
        return get_king_moves(board, piece)

    if movement == "pawn":
        return get_pawn_moves(board, piece)

    if movement == "squire":
        return get_squire_moves(board, piece)

    if movement == "peasant":
        return get_peasant_moves(board, piece)

    if movement == "mule":
        return get_mule_moves(board, piece)
    
    if movement == "wild_stallion":
        return get_wild_stallion_moves(board, piece)

    if movement == "clergy_riders":
        return get_clergy_riders_moves(board, piece)

    if movement == "lance_rider":
        return get_lance_rider_moves(board, piece)

    if movement == "pegasus":
        return get_pegasus_moves(board, piece)

    if movement == "damaged_chariot":
        return get_damaged_chariot_moves(board, piece)

    if movement == "fast_chariot":
        return get_fast_chariot_moves(board, piece)

    if movement == "armored_chariot":
        return get_armored_chariot_moves(board, piece)
    
    if movement == "shield_bearer":
        return get_shield_bearer_moves(board, piece)
    
    if movement == "adept":
        return get_adept_moves(board, piece)
    
    if movement == "high_priest":
        return get_high_priest_moves(board, piece)
    
    if movement == "arcane_priest":
        return get_arcane_priest_moves(board, piece)
    
    if movement == "corrupted_abbot":
        return get_corrupted_abbot_moves(board, piece)
    
    if movement == "arcane_tower":
        return get_arcane_tower_moves(board, piece)
    
    if movement == "sorceress":
        return get_sorceress_moves(board, piece)
    if movement == "joan_of_arc":
        return get_joan_of_arc_moves(board, piece)
    if movement == "queen_of_air":
        return get_queen_of_air_moves(board, piece)
    if movement == "queen_of_darkness":
        return get_queen_of_darkness_moves(board, piece)
    if movement == "the_old_queen":
        return get_the_old_queen_moves(board, piece)
    
    raise ValueError(f"Unknown movement type: {movement}")