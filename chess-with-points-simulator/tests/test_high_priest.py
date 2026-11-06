from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece

def test_high_priest_moves_up_to_3_diagonal():
    board = Board()
    priest = make_piece("high priest", "white", (3, 3))

    board.place_piece(priest, (3, 3))

    moves = get_pseudo_legal_moves(board, priest)

    assert (4, 4) in moves
    assert (5, 5) in moves
    assert (6, 6) in moves
    assert (7, 7) not in moves

def test_high_priest_moves_1_horizontal():
    board = Board()
    priest = make_piece("high priest", "white", (3, 3))

    board.place_piece(priest, (3, 3))

    moves = get_pseudo_legal_moves(board, priest)

    assert (3, 2) in moves
    assert (3, 4) in moves
    assert (3, 1) not in moves
    assert (3, 5) not in moves

def test_high_priest_does_not_move_vertical():
    board = Board()
    priest = make_piece("high priest", "white", (3, 3))

    board.place_piece(priest, (3, 3))

    moves = get_pseudo_legal_moves(board, priest)

    assert (2, 3) not in moves
    assert (4, 3) not in moves

def test_high_priest_diagonal_movement_is_blocked():
    board = Board()
    priest = make_piece("high priest", "white", (3, 3))
    blocker = make_piece("pawn", "white", (4, 4))

    board.place_piece(priest, (3, 3))
    board.place_piece(blocker, (4, 4))

    moves = get_pseudo_legal_moves(board, priest)

    assert (4, 4) not in moves
    assert (5, 5) not in moves
    assert (6, 6) not in moves

def test_high_priest_can_capture_diagonally():
    board = Board()
    priest = make_piece("high priest", "white", (3, 3))
    enemy = make_piece("pawn", "black", (5, 5))

    board.place_piece(priest, (3, 3))
    board.place_piece(enemy, (5, 5))

    moves = get_pseudo_legal_moves(board, priest)

    assert (5, 5) in moves
    assert (6, 6) not in moves

def test_high_priest_can_capture_1_horizontal():
    board = Board()
    priest = make_piece("high priest", "white", (3, 3))
    enemy = make_piece("pawn", "black", (3, 4))

    board.place_piece(priest, (3, 3))
    board.place_piece(enemy, (3, 4))

    moves = get_pseudo_legal_moves(board, priest)

    assert (3, 4) in moves

def test_high_priest_does_not_have_king_status():
    priest = make_piece("high priest", "white", (3, 3))

    assert priest.definition.is_king_status is False
