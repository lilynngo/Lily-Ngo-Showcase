from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece


def test_pawn_can_move_two_steps_on_first_move_if_clear():
    board = Board()
    pawn = make_piece("pawn", "white", (1, 3))

    board.place_piece(pawn, (1, 3))

    moves = get_pseudo_legal_moves(board, pawn)

    assert (2, 3) in moves
    assert (3, 3) in moves


def test_pawn_cannot_move_two_steps_after_it_has_moved():
    board = Board()
    pawn = make_piece("pawn", "white", (1, 3))
    pawn.has_moved = True

    board.place_piece(pawn, (1, 3))

    moves = get_pseudo_legal_moves(board, pawn)

    assert (2, 3) in moves
    assert (3, 3) not in moves


def test_pawn_cannot_move_two_steps_if_first_square_blocked():
    board = Board()
    pawn = make_piece("pawn", "white", (1, 3))
    blocker = make_piece("pawn", "white", (2, 3))

    board.place_piece(pawn, (1, 3))
    board.place_piece(blocker, (2, 3))

    moves = get_pseudo_legal_moves(board, pawn)

    assert (2, 3) not in moves
    assert (3, 3) not in moves


def test_pawn_cannot_move_two_steps_if_second_square_blocked():
    board = Board()
    pawn = make_piece("pawn", "white", (1, 3))
    blocker = make_piece("pawn", "white", (3, 3))

    board.place_piece(pawn, (1, 3))
    board.place_piece(blocker, (3, 3))

    moves = get_pseudo_legal_moves(board, pawn)

    assert (2, 3) in moves
    assert (3, 3) not in moves


def test_black_pawn_can_move_two_steps_on_first_move_if_clear():
    board = Board()
    pawn = make_piece("pawn", "black", (6, 3))

    board.place_piece(pawn, (6, 3))

    moves = get_pseudo_legal_moves(board, pawn)

    assert (5, 3) in moves
    assert (4, 3) in moves