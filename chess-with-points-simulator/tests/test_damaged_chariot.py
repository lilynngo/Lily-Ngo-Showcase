from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece

def test_damaged_chariot_moves_only_1_square_orthogonally():
    board = Board()
    chariot = make_piece("damaged chariot", "white", (3, 3))

    board.place_piece(chariot, (3, 3))

    moves = get_pseudo_legal_moves(board, chariot)

    assert set(moves) == {
        (2, 3),
        (4, 3),
        (3, 2),
        (3, 4),
    }