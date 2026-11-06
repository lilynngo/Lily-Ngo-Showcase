from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece

def test_squire_moves_like_king():
    board = Board()
    squire = make_piece("squire", "white", (3, 3))

    board.place_piece(squire, (3, 3))

    moves = get_pseudo_legal_moves(board, squire)

    assert len(moves) == 8
    assert (2, 2) in moves
    assert (2, 3) in moves
    assert (2, 4) in moves
    assert (3, 2) in moves
    assert (3, 4) in moves
    assert (4, 2) in moves
    assert (4, 3) in moves
    assert (4, 4) in moves