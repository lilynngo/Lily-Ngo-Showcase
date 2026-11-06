from src.board import Board
from src.rules import is_in_check, is_checkmate, get_legal_moves
from tests.helpers import make_piece


def test_rook_attacks_enemy_king_on_same_file():
    board = Board()
    white_rook = make_piece("rook", "white", (0, 0))
    black_king = make_piece("king", "black", (7, 0))

    board.place_piece(white_rook, (0, 0))
    board.place_piece(black_king, (7, 0))

    assert is_in_check(board, "black") is True


def test_bishop_attacks_enemy_king_diagonally():
    board = Board()
    white_bishop = make_piece("bishop", "white", (0, 0))
    black_king = make_piece("king", "black", (3, 3))

    board.place_piece(white_bishop, (0, 0))
    board.place_piece(black_king, (3, 3))

    assert is_in_check(board, "black") is True


def test_knight_attacks_enemy_king():
    board = Board()
    white_knight = make_piece("knight", "white", (3, 3))
    black_king = make_piece("king", "black", (5, 4))

    board.place_piece(white_knight, (3, 3))
    board.place_piece(black_king, (5, 4))

    assert is_in_check(board, "black") is True


def test_piece_blocks_rook_check():
    board = Board()
    white_rook = make_piece("rook", "white", (0, 0))
    blocker = make_piece("pawn", "black", (3, 0))
    black_king = make_piece("king", "black", (7, 0))

    board.place_piece(white_rook, (0, 0))
    board.place_piece(blocker, (3, 0))
    board.place_piece(black_king, (7, 0))

    assert is_in_check(board, "black") is False


def test_king_can_escape_check_not_checkmate():
    board = Board()
    white_rook = make_piece("rook", "white", (0, 0))
    black_king = make_piece("king", "black", (7, 0))

    board.place_piece(white_rook, (0, 0))
    board.place_piece(black_king, (7, 0))

    assert is_in_check(board, "black") is True
    assert is_checkmate(board, "black") is False


def test_move_that_leaves_king_in_check_is_illegal():
    board = Board()
    white_king = make_piece("king", "white", (0, 0))
    white_rook = make_piece("rook", "white", (1, 0))
    black_rook = make_piece("rook", "black", (7, 0))

    board.place_piece(white_king, (0, 0))
    board.place_piece(white_rook, (1, 0))
    board.place_piece(black_rook, (7, 0))

    legal_moves = get_legal_moves(board, white_rook)

    assert (1, 1) not in legal_moves


def test_simple_checkmate_position():
    board = Board()

    black_king = make_piece("king", "black", (7, 7))
    white_queen = make_piece("queen", "white", (6, 6))
    white_king = make_piece("king", "white", (5, 5))

    board.place_piece(black_king, (7, 7))
    board.place_piece(white_queen, (6, 6))
    board.place_piece(white_king, (5, 5))

    assert is_checkmate(board, "black") is True