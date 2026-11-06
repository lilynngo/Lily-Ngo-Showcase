from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece



def test_fast_chariot_moves_up_to_3_squares_orthogonally():
    board = Board()
    chariot = make_piece("fast chariot", "white", (3, 3))

    board.place_piece(chariot, (3, 3))

    moves = get_pseudo_legal_moves(board, chariot)

    assert (3, 4) in moves
    assert (3, 5) in moves
    assert (3, 6) in moves
    assert (3, 7) not in moves


def test_fast_chariot_blocked_by_enemy_piece():
    board = Board()
    chariot = make_piece("fast chariot", "white", (3, 3))
    enemy = make_piece("pawn", "black", (3, 5))

    board.place_piece(chariot, (3, 3))
    board.place_piece(enemy, (3, 5))

    moves = get_pseudo_legal_moves(board, chariot)

    assert (3, 4) in moves
    assert (3, 5) in moves
    assert (3, 6) not in moves