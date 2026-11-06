import pytest

from src.board import Board
from src.moves import get_pseudo_legal_moves
from src.simulation import execute_leap, get_leap_moves_for_piece
from tests.helpers import make_piece

def test_wild_stallion_moves_like_knight():
    board = Board()
    piece = make_piece("wild stallion", "white", (3, 3))

    board.place_piece(piece, (3, 3))

    moves = get_pseudo_legal_moves(board, piece)

    assert (5, 4) in moves
    assert (1, 2) in moves


def test_wild_stallion_can_leap_capture_enemy():
    board = Board()
    piece = make_piece("wild stallion", "white", (3, 3))
    enemy = make_piece("pawn", "black", (5, 4))

    board.place_piece(piece, (3, 3))
    board.place_piece(enemy, (5, 4))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((3, 3), (5, 4)) in leap_moves

def test_clergy_riders_move_exactly_2_diagonal():
    board = Board()
    piece = make_piece("clergy riders", "white", (3, 3))

    board.place_piece(piece, (3, 3))

    moves = get_pseudo_legal_moves(board, piece)

    assert (4, 4) not in moves
    assert (5, 5) in moves
    assert (6, 6) not in moves


def test_clergy_riders_normal_move_blocked_by_middle_piece():
    board = Board()
    piece = make_piece("clergy riders", "white", (3, 3))
    blocker = make_piece("pawn", "white", (4, 4))

    board.place_piece(piece, (3, 3))
    board.place_piece(blocker, (4, 4))

    moves = get_pseudo_legal_moves(board, piece)

    assert (5, 5) not in moves


def test_clergy_riders_leap_exactly_2_over_blocker_and_capture():
    board = Board()
    piece = make_piece("clergy riders", "white", (3, 3))
    blocker = make_piece("pawn", "white", (4, 4))
    enemy = make_piece("pawn", "black", (5, 5))

    board.place_piece(piece, (3, 3))
    board.place_piece(blocker, (4, 4))
    board.place_piece(enemy, (5, 5))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((3, 3), (4, 4)) not in leap_moves
    assert ((3, 3), (5, 5)) in leap_moves


def test_lance_rider_has_no_normal_moves_if_tracked_as_leap():
    board = Board()
    piece = make_piece("lance rider", "white", (3, 3))

    board.place_piece(piece, (3, 3))

    moves = get_pseudo_legal_moves(board, piece)

    assert moves == []


def test_lance_rider_can_leap_like_knight():
    board = Board()
    piece = make_piece("lance rider", "white", (3, 3))

    board.place_piece(piece, (3, 3))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((3, 3), (5, 4)) in leap_moves
    assert ((3, 3), (1, 2)) in leap_moves


def test_lance_rider_can_leap_exactly_3_forward():
    board = Board()
    piece = make_piece("lance rider", "white", (2, 3))

    board.place_piece(piece, (2, 3))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((2, 3), (3, 3)) not in leap_moves
    assert ((2, 3), (4, 3)) not in leap_moves
    assert ((2, 3), (5, 3)) in leap_moves


def test_lance_rider_can_leap_exactly_3_forward_over_blockers():
    board = Board()
    piece = make_piece("lance rider", "white", (2, 3))
    blocker_1 = make_piece("pawn", "white", (3, 3))
    blocker_2 = make_piece("pawn", "black", (4, 3))

    board.place_piece(piece, (2, 3))
    board.place_piece(blocker_1, (3, 3))
    board.place_piece(blocker_2, (4, 3))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((2, 3), (5, 3)) in leap_moves


def test_lance_rider_can_leap_capture_with_knight_style():
    board = Board()
    piece = make_piece("lance rider", "white", (3, 3))
    enemy = make_piece("pawn", "black", (5, 4))

    board.place_piece(piece, (3, 3))
    board.place_piece(enemy, (5, 4))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((3, 3), (5, 4)) in leap_moves


def test_lance_rider_can_leap_capture_exactly_3_forward():
    board = Board()
    piece = make_piece("lance rider", "white", (2, 3))
    enemy = make_piece("pawn", "black", (5, 3))

    board.place_piece(piece, (2, 3))
    board.place_piece(enemy, (5, 3))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((2, 3), (5, 3)) in leap_moves

def test_pegasus_moves_like_knight():
    board = Board()
    piece = make_piece("pegasus", "white", (3, 3))

    board.place_piece(piece, (3, 3))

    moves = get_pseudo_legal_moves(board, piece)

    assert (5, 4) in moves
    assert (1, 2) in moves


def test_pegasus_can_leap_capture_enemy():
    board = Board()
    piece = make_piece("pegasus", "white", (3, 3))
    enemy = make_piece("pawn", "black", (5, 4))

    board.place_piece(piece, (3, 3))
    board.place_piece(enemy, (5, 4))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((3, 3), (5, 4)) in leap_moves

def test_fast_chariot_can_leap_over_blocker_to_empty_square():
    board = Board()
    piece = make_piece("fast chariot", "white", (3, 3))
    blocker = make_piece("pawn", "white", (3, 4))

    board.place_piece(piece, (3, 3))
    board.place_piece(blocker, (3, 4))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((3, 3), (3, 5)) in leap_moves
    assert ((3, 3), (3, 6)) in leap_moves


def test_fast_chariot_cannot_leap_capture_enemy_piece():
    board = Board()
    piece = make_piece("fast chariot", "white", (3, 3))
    enemy = make_piece("pawn", "black", (3, 5))

    board.place_piece(piece, (3, 3))
    board.place_piece(enemy, (3, 5))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((3, 3), (3, 5)) not in leap_moves

def test_leap_cannot_land_on_friendly_piece():
    board = Board()
    piece = make_piece("pegasus", "white", (3, 3))
    friendly = make_piece("pawn", "white", (5, 4))

    board.place_piece(piece, (3, 3))
    board.place_piece(friendly, (5, 4))

    leap_moves = get_leap_moves_for_piece(board, piece)

    assert ((3, 3), (5, 4)) not in leap_moves


def test_execute_leap_can_capture_enemy_for_non_fast_chariot():
    board = Board()
    piece = make_piece("pegasus", "white", (3, 3))
    enemy = make_piece("pawn", "black", (5, 4))

    board.place_piece(piece, (3, 3))
    board.place_piece(enemy, (5, 4))

    result = execute_leap(board, (3, 3), (5, 4))

    assert result["leap_used"] is True
    assert result["leap_captured"] == "pawn"
    assert board.get_piece_at((3, 3)) is None
    assert board.get_piece_at((5, 4)) == piece


def test_execute_leap_rejects_fast_chariot_capture():
    board = Board()
    piece = make_piece("fast chariot", "white", (3, 3))
    enemy = make_piece("pawn", "black", (3, 5))

    board.place_piece(piece, (3, 3))
    board.place_piece(enemy, (3, 5))

    with pytest.raises(ValueError):
        execute_leap(board, (3, 3), (3, 5))

