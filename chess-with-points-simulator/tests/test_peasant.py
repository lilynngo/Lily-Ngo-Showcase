from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece

def test_peasant_moves_like_pawn():
    board = Board()
    peasant = make_piece("peasant", "white", (1, 3))

    board.place_piece(peasant, (1, 3))

    moves = get_pseudo_legal_moves(board, peasant)

    assert (2, 3) in moves