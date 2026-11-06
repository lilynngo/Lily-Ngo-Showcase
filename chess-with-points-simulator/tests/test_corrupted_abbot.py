import pytest

from src.board import Board
from src.moves import get_pseudo_legal_moves
from src.simulation import (
    execute_opponent_control_move,
    get_opponent_control_moves_for_piece,
)
from tests.helpers import make_piece

def test_corrupted_abbot_owner_moves_like_queen():
    board = Board()
    abbot = make_piece("corrupted abbot", "white", (3, 3))

    board.place_piece(abbot, (3, 3))

    moves = get_pseudo_legal_moves(board, abbot)

    assert (3, 7) in moves
    assert (7, 3) in moves
    assert (6, 6) in moves

def test_opponent_can_move_corrupted_abbot_1_orthogonal():
    board = Board()
    abbot = make_piece("corrupted abbot", "white", (3, 3))

    board.place_piece(abbot, (3, 3))

    moves = get_opponent_control_moves_for_piece(
        board,
        abbot,
        controller="black",
    )

    assert ((3, 3), (4, 3)) in moves
    assert ((3, 3), (2, 3)) in moves
    assert ((3, 3), (3, 4)) in moves
    assert ((3, 3), (3, 2)) in moves

def test_owner_cannot_use_opponent_control_move():
    board = Board()
    abbot = make_piece("corrupted abbot", "white", (3, 3))

    board.place_piece(abbot, (3, 3))

    moves = get_opponent_control_moves_for_piece(
        board,
        abbot,
        controller="white",
    )

    assert moves == []

def test_opponent_control_corrupted_abbot_cannot_capture():
    board = Board()
    abbot = make_piece("corrupted abbot", "white", (3, 3))
    black_piece = make_piece("pawn", "black", (4, 3))

    board.place_piece(abbot, (3, 3))
    board.place_piece(black_piece, (4, 3))

    moves = get_opponent_control_moves_for_piece(
        board,
        abbot,
        controller="black",
    )

    assert ((3, 3), (4, 3)) not in moves

def test_opponent_control_corrupted_abbot_cannot_move_onto_occupied_square():
    board = Board()
    abbot = make_piece("corrupted abbot", "white", (3, 3))
    white_piece = make_piece("pawn", "white", (4, 3))

    board.place_piece(abbot, (3, 3))
    board.place_piece(white_piece, (4, 3))

    moves = get_opponent_control_moves_for_piece(
        board,
        abbot,
        controller="black",
    )

    assert ((3, 3), (4, 3)) not in moves

def test_execute_opponent_control_move_moves_piece():
    board = Board()
    abbot = make_piece("corrupted abbot", "white", (3, 3))

    board.place_piece(abbot, (3, 3))

    result = execute_opponent_control_move(
        board,
        (3, 3),
        (4, 3),
        controller="black",
    )

    assert result["opponent_control_used"] is True
    assert result["controlled_piece"] == "corrupted abbot"
    assert board.get_piece_at((3, 3)) is None
    assert board.get_piece_at((4, 3)) == abbot

def test_execute_opponent_control_rejects_capture():
    board = Board()
    abbot = make_piece("corrupted abbot", "white", (3, 3))
    black_piece = make_piece("pawn", "black", (4, 3))

    board.place_piece(abbot, (3, 3))
    board.place_piece(black_piece, (4, 3))

    with pytest.raises(ValueError):
        execute_opponent_control_move(
            board,
            (3, 3),
            (4, 3),
            controller="black",
        )

