from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece

def test_mule_moves_up_to_2_squares_like_rook():
    board = Board()
    mule = make_piece("mule", "white", (3, 3))

    board.place_piece(mule, (3, 3))

    moves = get_pseudo_legal_moves(board, mule)

    assert (3, 4) in moves
    assert (3, 5) in moves
    assert (3, 6) not in moves

    assert (4, 3) in moves
    assert (5, 3) in moves
    assert (6, 3) not in moves


def test_mule_blocked_by_friendly_piece():
    board = Board()
    mule = make_piece("mule", "white", (3, 3))
    blocker = make_piece("pawn", "white", (3, 4))

    board.place_piece(mule, (3, 3))
    board.place_piece(blocker, (3, 4))

    moves = get_pseudo_legal_moves(board, mule)

    assert (3, 4) not in moves
    assert (3, 5) not in moves


def test_mule_can_capture_enemy_but_not_move_beyond():
    board = Board()
    mule = make_piece("mule", "white", (3, 3))
    enemy = make_piece("pawn", "black", (3, 4))

    board.place_piece(mule, (3, 3))
    board.place_piece(enemy, (3, 4))

    moves = get_pseudo_legal_moves(board, mule)

    assert (3, 4) in moves
    assert (3, 5) not in moves