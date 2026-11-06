from src.board import Board
from src.moves import get_pseudo_legal_moves, is_black_square, is_white_square
from tests.helpers import make_piece

def test_standard_chess_square_colors_for_darkness():
    assert is_black_square((0, 0)) is True
    assert is_white_square((0, 1)) is True
    assert is_black_square((3, 4)) is False
    assert is_black_square((3, 5)) is True

def test_queen_of_darkness_only_lands_on_black_squares():
    board = Board()
    queen = make_piece("queen of darkness", "white", (3, 5))

    board.place_piece(queen, (3, 5))

    moves = get_pseudo_legal_moves(board, queen)

    assert len(moves) > 0

    for square in moves:
        assert is_black_square(square)

def test_queen_of_darkness_moves_like_queen_to_black_squares():
    board = Board()
    queen = make_piece("queen of darkness", "white", (3, 5))

    board.place_piece(queen, (3, 5))

    moves = get_pseudo_legal_moves(board, queen)

    # Horizontal black squares.
    assert (3, 7) in moves
    assert (3, 3) in moves
    assert (3, 1) in moves

    # Vertical black squares.
    assert (5, 5) in moves
    assert (7, 5) in moves
    assert (1, 5) in moves

    # Diagonal black squares.
    assert (4, 6) in moves
    assert (5, 7) in moves
    assert (4, 4) in moves
    assert (5, 3) in moves

def test_queen_of_darkness_cannot_land_on_white_squares():
    board = Board()
    queen = make_piece("queen of darkness", "white", (3, 5))

    board.place_piece(queen, (3, 5))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 6) not in moves
    assert (4, 5) not in moves
    assert (4, 7) not in moves

    # These are black squares and should be legal if path is clear.
    assert (3, 7) in moves
    assert (4, 6) in moves

def test_queen_of_darkness_can_pass_through_empty_white_squares():
    board = Board()
    queen = make_piece("queen of darkness", "white", (3, 5))

    board.place_piece(queen, (3, 5))

    moves = get_pseudo_legal_moves(board, queen)

    # (3, 6) is white, so she cannot land there.
    assert (3, 6) not in moves

    # But she can pass through it to the next black square.
    assert (3, 7) in moves

def test_queen_of_darkness_cannot_move_through_friendly_piece():
    board = Board()

    queen = make_piece("queen of darkness", "white", (3, 5))
    friendly = make_piece("pawn", "white", (3, 6))

    board.place_piece(queen, (3, 5))
    board.place_piece(friendly, (3, 6))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 6) not in moves
    assert (3, 7) not in moves

def test_queen_of_darkness_can_capture_enemy_on_black_square():
    board = Board()

    queen = make_piece("queen of darkness", "white", (3, 5))
    enemy = make_piece("pawn", "black", (3, 7))

    board.place_piece(queen, (3, 5))
    board.place_piece(enemy, (3, 7))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 7) in moves

def test_queen_of_darkness_cannot_capture_enemy_on_white_square():
    board = Board()

    queen = make_piece("queen of darkness", "white", (3, 5))
    enemy = make_piece("pawn", "black", (3, 6))

    board.place_piece(queen, (3, 5))
    board.place_piece(enemy, (3, 6))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 6) not in moves

    # Enemy still blocks movement beyond it.
    assert (3, 7) not in moves

