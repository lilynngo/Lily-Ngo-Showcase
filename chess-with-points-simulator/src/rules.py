from copy import deepcopy

from src.actions import execute_leap, execute_opponent_control_move, execute_swap, get_leap_moves_for_piece, get_opponent_control_moves_for_piece, get_swap_moves_for_piece
from src.board import Board
from src.models import PieceInstance, Square
from src.moves import get_pseudo_legal_moves

def get_enemy_player(player:str):
    return "black" if player == "white" else "white"
def other_player(current_player:str):
    return "white" if current_player=="black" else "black"

def get_pieces_for_player(board:Board, player:str):
    return [
        piece 
        for piece in board.squares.values()
        if piece.owner == player
    ]

def get_attack_squares(
    board: Board,
    piece: PieceInstance,
) -> set[Square]:
    attack_squares = set(
        get_pseudo_legal_moves(board, piece)
    )

    for _, to_square in get_leap_moves_for_piece(board, piece):
        attack_squares.add(to_square)

    return attack_squares

def get_all_legal_moves_for_player(
    board: Board,
    player: str,
) -> list[dict]:
    all_moves: list[dict] = []

    for piece in get_pieces_for_player(board, player):
        for destination in get_legal_moves(board, piece):
            all_moves.append({
                "type": "move",
                "from_square": piece.position,
                "to_square": destination,
            })

        for from_square, to_square in get_swap_moves_for_piece(
            board,
            piece,
        ):
            if swap_leaves_king_in_check(
                board,
                from_square,
                to_square,
                player,
            ):
                continue

            all_moves.append({
                "type": "swap",
                "from_square": from_square,
                "to_square": to_square,
            })

        for from_square, to_square in get_leap_moves_for_piece(
            board,
            piece,
        ):
            if leap_leaves_king_in_check(
                board,
                from_square,
                to_square,
                player,
            ):
                continue

            all_moves.append({
                "type": "leap",
                "from_square": from_square,
                "to_square": to_square,
            })

    for piece in board.squares.values():
        if piece.owner == player:
            continue

        controlled_moves = get_opponent_control_moves_for_piece(
            board,
            piece,
            controller=player,
        )

        for from_square, to_square in controlled_moves:
            if opponent_control_move_leaves_king_in_check(
                board,
                from_square,
                to_square,
                player,
            ):
                continue

            all_moves.append({
                "type": "opponent_control_move",
                "from_square": from_square,
                "to_square": to_square,
            })

    return all_moves

def find_king(board:Board, player:str):
    for piece in board.squares.values():
        if piece.owner == player and piece.definition.is_king_status:
            return piece
    return None

def get_king_status_pieces(board: Board, player: str):
    return [
        piece
        for piece in board.squares.values()
        if piece.owner == player and piece.definition.is_king_status
    ]


def swap_leaves_king_in_check(board:Board, from_square:tuple[int, int], to_square:tuple[int, int], player:str):
    board_copy = copy_board(board)
    execute_swap(board_copy, from_square, to_square)
    return is_in_check(board_copy, player)

def leap_leaves_king_in_check(board:Board, from_square:tuple[int, int], to_square:tuple[int, int], player):
    board_copy = copy_board(board)
    execute_leap(board_copy, from_square, to_square)
    return is_in_check(board_copy, player)


def opponent_control_move_leaves_king_in_check(board:Board, from_square:tuple[int, int], to_square:tuple[int, int], player:str):
    board_copy = copy_board(board)
    execute_opponent_control_move(
        board_copy,
        from_square,
        to_square,
        controller=player,
    )

    return is_in_check(board_copy, player)

def is_in_check(board: Board, player: str) -> bool:
    king_status_pieces = get_king_status_pieces(board, player)

    if not king_status_pieces:
        raise ValueError(f"{player} has no king-status pieces.")

    king_squares = {
        piece.position
        for piece in king_status_pieces
    }

    opponent = other_player(player)

    for piece in get_pieces_for_player(board, opponent):
        if king_squares.intersection(
            get_attack_squares(board, piece)
        ):
            return True

    return False

def copy_board(board: Board):
    new_board = Board()
    new_board.current_player = board.current_player
    new_board.move_number = board.move_number

    for square, piece in board.squares.items():
        copied_piece = PieceInstance(
            definition=piece.definition,
            owner=piece.owner,
            position=piece.position,
            has_moved=piece.has_moved,

            instance_number=piece.instance_number,
            instance_id=piece.instance_id,
            starting_position=piece.starting_position,
            original_piece_name=piece.original_piece_name,
        )


        copied_piece.shield_charges = piece.shield_charges
        copied_piece.is_captured = piece.is_captured
        copied_piece.is_in_queen_spot = piece.is_in_queen_spot

        new_board.place_piece(copied_piece, square)

    return new_board

def move_leaves_king_in_check(board:Board, piece:PieceInstance, destination:Square):
    test_board = copy_board(board)
    test_piece = test_board.get_piece_at(piece.position)
    if test_piece is None:
        return True
    test_board.move_piece(test_piece.position, destination)
    return is_in_check(test_board, piece.owner)

def get_legal_moves(board:Board, piece:PieceInstance):
    pseudo_moves = get_pseudo_legal_moves(board, piece)
    legal_moves = []
    for destination in pseudo_moves:
        if not move_leaves_king_in_check(board, piece, destination):
            legal_moves.append(destination)
    return legal_moves


def is_square_attacked(
    board: Board,
    square: Square,
    by_player: str,
) -> bool:
    for piece in get_pieces_for_player(board, by_player):
        if square in get_attack_squares(board, piece):
            return True

    return False

def player_has_any_legal_moves(
    board: Board,
    player: str,
) -> bool:
    return bool(
        get_all_legal_moves_for_player(board, player)
    )

def is_checkmate(board: Board, player:str):
    return is_in_check(board, player) and not player_has_any_legal_moves(board, player)

def validate_board_state(board: Board) -> None:
    seen_positions = set()

    white_kings = 0
    black_kings = 0

    for square, piece in board.squares.items():
        if not board.is_square_on_board(square):
            raise ValueError(f"Piece is outside board at {square}")

        if square in seen_positions:
            raise ValueError(f"Duplicate piece position at {square}")

        seen_positions.add(square)

        if piece.position != square:
            raise ValueError(
                f"Piece position mismatch: piece says {piece.position}, "
                f"board says {square}"
            )

        if piece.owner not in {"white", "black"}:
            raise ValueError(f"Invalid owner: {piece.owner}")

        if piece.definition.is_king_status:
            if piece.owner == "white":
                white_kings += 1
            else:
                black_kings += 1

    if white_kings < 1:
        raise ValueError(f"Expected 1 white king, found {white_kings}")

    if black_kings < 1:
        raise ValueError(f"Expected 1 black king, found {black_kings}")