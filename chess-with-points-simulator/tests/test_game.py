import pytest

from src.rules import get_legal_moves, is_checkmate, is_in_check
from src.simulation import is_stalemate, next_halfmove_clock, simulate_game_with_armies
from tests.helpers import make_piece, PIECES
from src.board import Board
from src.models import PieceInstance
from src.army import (
    assign_piece_instance_ids,
    get_starting_class
)

@pytest.fixture
def standard_board() -> Board:
    board = Board()

    back_rank = [
        "rook",
        "knight",
        "bishop",
        "queen",
        "king",
        "bishop",
        "knight",
        "rook",
    ]

    # White starts on rows 0 and 1 in your coordinate system.
    for col, name in enumerate(back_rank):
        board.squares[(0, col)] = make_piece(
            name,
            owner="white",
            position=(0, col),
        )

    for col in range(8):
        board.squares[(1, col)] = make_piece(
            "pawn",
            owner="white",
            position=(1, col),
        )

    # Black starts on rows 7 and 6.
    for col, name in enumerate(back_rank):
        board.squares[(7, col)] = make_piece(
            name,
            owner="black",
            position=(7, col),
        )

    for col in range(8):
        board.squares[(6, col)] = make_piece(
            "pawn",
            owner="black",
            position=(6, col),
        )

    return board

@pytest.mark.parametrize(
    "owner,square",
    [
        ("white", (2, 0)),
        ("white", (5, 4)),
        ("black", (2, 7)),
        ("black", (5, 3)),
    ],
)

def test_get_starting_class_returns_other_for_middle_rows(
    owner: str,
    square: tuple[int, int],
):
    assert get_starting_class(owner, square) == "other"

def test_same_piece_type_can_be_noble_or_commoner():
    noble_class = get_starting_class(
        owner="white",
        square=(0, 3),
    )

    commoner_class = get_starting_class(
        owner="white",
        square=(1, 3),
    )

    assert noble_class == "noble"
    assert commoner_class == "commoner"

def test_assign_piece_instance_ids_marks_white_back_rank_as_noble(
    standard_board: Board,
):
    assign_piece_instance_ids(standard_board)

    piece = standard_board.get_piece_at((0, 0))

    assert piece is not None
    assert piece.starting_position == (0, 0)
    assert piece.starting_class == "noble"
    assert piece.is_noble is True

def test_assign_piece_instance_ids_marks_white_pawn_rank_as_commoner(
    standard_board: Board,
):
    assign_piece_instance_ids(standard_board)

    piece = standard_board.get_piece_at((1, 0))

    assert piece is not None
    assert piece.starting_position == (1, 0)
    assert piece.starting_class == "commoner"
    assert piece.is_noble is False

def test_assign_piece_instance_ids_marks_black_back_rank_as_noble(
    standard_board: Board,
):
    assign_piece_instance_ids(standard_board)

    piece = standard_board.get_piece_at((7, 0))

    assert piece is not None
    assert piece.starting_class == "noble"
    assert piece.is_noble is True

def test_assign_piece_instance_ids_marks_black_pawn_rank_as_commoner(
    standard_board: Board,
):
    assign_piece_instance_ids(standard_board)

    piece = standard_board.get_piece_at((6, 0))

    assert piece is not None
    assert piece.starting_class == "commoner"
    assert piece.is_noble is False

def place_piece(
    board: Board,
    owner: str,
    piece_name: str,
    square: tuple[int, int],
) -> PieceInstance:
    piece = PieceInstance(
        definition=PIECES[piece_name],
        owner=owner,
        position=square,
    )

    board.squares[square] = piece
    return piece

def test_detects_basic_stalemate():
    board = Board()

    place_piece(
        board,
        "black",
        "king",
        (7, 0),
    )

    place_piece(
        board,
        "white",
        "king",
        (5, 2),
    )

    place_piece(
        board,
        "white",
        "queen",
        (5, 1),
    )

    assert is_in_check(board, "black") is False
    assert player_has_legal_move(board, "black") is False
    assert is_stalemate(board, "black") is True

def player_has_legal_move(
    board: Board,
    player: str,
) -> bool:
    for piece in board.squares.values():
        if piece.owner != player:
            continue

        if piece.is_captured:
            continue

        legal_moves = get_legal_moves(
            board,
            piece,
        )

        if legal_moves:
            return True

    return False

def test_position_with_legal_move_is_not_stalemate(
):
    board = Board()

    place_piece(
        board,
        "black",
        "king",
        (7, 0),
    )

    place_piece(
        board,
        "white",
        "king",
        (4, 2),
    )

    assert is_in_check(board, "black") is False
    assert player_has_legal_move(board, "black") is True
    assert is_stalemate(board, "black") is False

def test_player_in_check_with_legal_escape_is_not_stalemate(
):
    board = Board()

    place_piece(
        board,
        "black",
        "king",
        (7, 0),
    )

    place_piece(
        board,
        "white",
        "king",
        (4, 2),
    )

    place_piece(
        board,
        "white",
        "rook",
        (7, 7),
    )

    assert is_in_check(board, "black") is True
    assert player_has_legal_move(board, "black") is True
    assert is_stalemate(board, "black") is False
    assert is_checkmate(board, "black") is False


def test_quiet_move_increments_halfmove_clock():
    knight = make_piece("knight", owner="black", position=(0,0), is_noble=True)

    result = next_halfmove_clock(
        halfmove_clock=12,
        moving_piece=knight,
        captured_piece=None,
    )

    assert result == 13


def test_pawn_move_resets_halfmove_clock():
    pawn = make_piece("pawn")

    result = next_halfmove_clock(
        halfmove_clock=149,
        moving_piece=pawn,
        captured_piece=None,
    )

    assert result == 0


def test_normal_capture_resets_halfmove_clock():
    rook = make_piece("rook")
    captured_pawn = make_piece("pawn", owner="black")

    result = next_halfmove_clock(
        halfmove_clock=149,
        moving_piece=rook,
        captured_piece=captured_pawn,
    )

    assert result == 0


def test_pawn_capture_resets_halfmove_clock():
    pawn = make_piece("pawn")
    captured_knight = make_piece("knight", owner="black", position=(0,0), is_noble=True)

    result = next_halfmove_clock(
        halfmove_clock=149,
        moving_piece=pawn,
        captured_piece=captured_knight,
    )

    assert result == 0


def test_quiet_move_reaches_150():
    bishop = make_piece("bishop", position=(0,0), is_noble=True)

    result = next_halfmove_clock(
        halfmove_clock=149,
        moving_piece=bishop,
        captured_piece=None,
    )

    assert result == 150