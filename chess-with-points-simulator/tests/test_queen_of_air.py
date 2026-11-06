from src.board import Board
from src.moves import get_pseudo_legal_moves, is_white_square
from tests.helpers import make_piece

def test_queen_of_air_only_lands_on_white_squares():
    board = Board()
    queen = make_piece("queen of air", "white", (3, 3))

    board.place_piece(queen, (3, 3))

    moves = get_pseudo_legal_moves(board, queen)

    assert len(moves) > 0

    for square in moves:
        assert is_white_square(square)

def test_queen_of_air_moves_like_queen_to_white_squares():
    board = Board()
    queen = make_piece("queen of air", "white", (3, 4))

    board.place_piece(queen, (3, 4))

    moves = get_pseudo_legal_moves(board, queen)

    # Horizontal white squares.
    assert (3, 6) in moves

    # Vertical white squares.
    assert (5, 4) in moves
    assert (7, 4) in moves

    # Diagonal white squares.
    assert (4, 5) in moves
    assert (5, 6) in moves
    assert (6, 7) in moves

def test_standard_chess_square_colors():
    assert is_white_square((0, 0)) is False
    assert is_white_square((0, 1)) is True
    assert is_white_square((3, 4)) is True
    assert is_white_square((4, 3)) is True
    assert is_white_square((3, 5)) is False

def test_queen_of_air_cannot_land_on_black_squares():
    board = Board()
    queen = make_piece("queen of air", "white", (3, 4))

    board.place_piece(queen, (3, 4))

    moves = get_pseudo_legal_moves(board, queen)

    # These are black squares.
    assert (3, 5) not in moves
    assert (4, 4) not in moves
    assert (5, 5) not in moves

    # These are white squares, so they should be legal if path is clear.
    assert (4, 3) in moves
    assert (4, 5) in moves
    

def test_queen_of_air_can_pass_through_empty_black_squares():
    board = Board()
    queen = make_piece("queen of air", "white", (3, 4))

    board.place_piece(queen, (3, 4))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 5) not in moves
    assert (3, 6) in moves


def test_queen_of_air_cannot_move_through_friendly_piece():
    board = Board()

    queen = make_piece("queen of air", "white", (3, 3))
    friendly = make_piece("pawn", "white", (3, 4))

    board.place_piece(queen, (3, 3))
    board.place_piece(friendly, (3, 4))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 4) not in moves
    assert (3, 5) not in moves
    assert (3, 6) not in moves

def test_queen_of_air_can_capture_enemy_on_white_square():
    board = Board()

    queen = make_piece("queen of air", "white", (3, 4))
    enemy = make_piece("pawn", "black", (3, 6))

    board.place_piece(queen, (3, 4))
    board.place_piece(enemy, (3, 6))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 6) in moves
    assert (3, 7) not in moves

def test_queen_of_air_cannot_capture_enemy_on_black_square():
    board = Board()

    queen = make_piece("queen of air", "white", (3, 4))
    enemy = make_piece("pawn", "black", (3, 5))

    board.place_piece(queen, (3, 4))
    board.place_piece(enemy, (3, 5))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 5) not in moves

    # Enemy still blocks movement beyond it.
    assert (3, 6) not in moves

def test_queen_of_air_can_start_on_white_square():
    queen = make_piece("queen of air", "white", (0, 1))

    assert is_white_square((0, 1)) is True

def test_queen_of_air_cannot_start_on_black_square():
    queen = make_piece("queen of air", "white", (0, 0))

    assert is_white_square((0, 0)) is False
