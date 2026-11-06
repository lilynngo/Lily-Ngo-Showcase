import pytest

from src.board import Board
from tests.helpers import make_piece


def test_place_piece_on_empty_square():
    board = Board()
    piece = make_piece("rook")

    board.place_piece(piece, (0, 0))

    assert board.get_piece_at((0, 0)) == piece


def test_move_piece_to_empty_square():
    board = Board()
    piece = make_piece("rook")

    board.place_piece(piece, (0, 0))
    board.move_piece((0, 0), (0, 5))

    assert board.get_piece_at((0, 0)) is None
    assert board.get_piece_at((0, 5)) == piece


def test_remove_piece():
    board = Board()
    piece = make_piece("rook")

    board.place_piece(piece, (0, 0))
    removed = board.remove_piece((0, 0))

    assert removed == piece
    assert board.get_piece_at((0, 0)) is None


def test_square_outside_board_is_invalid():
    board = Board()

    assert board.is_square_on_board((-1, 0)) is False
    assert board.is_square_on_board((8, 8)) is False


def test_cannot_place_two_pieces_on_same_square():
    board = Board()
    piece_a = make_piece("rook")
    piece_b = make_piece("bishop")

    board.place_piece(piece_a, (0, 0))

    with pytest.raises(ValueError):
        board.place_piece(piece_b, (0, 0))


def test_capture_enemy_piece():
    board = Board()
    white_rook = make_piece("rook", "white", (0, 0))
    black_bishop = make_piece("bishop", "black", (0, 5))

    board.place_piece(white_rook, (0, 0))
    board.place_piece(black_bishop, (0, 5))

    captured = board.move_piece((0, 0), (0, 5))

    assert captured == black_bishop
    assert board.get_piece_at((0, 5)) == white_rook


def test_cannot_capture_friendly_piece():
    board = Board()
    white_rook = make_piece("rook", "white", (0, 0))
    white_bishop = make_piece("bishop", "white", (0, 5))

    board.place_piece(white_rook, (0, 0))
    board.place_piece(white_bishop, (0, 5))

    with pytest.raises(ValueError):
        board.move_piece((0, 0), (0, 5))