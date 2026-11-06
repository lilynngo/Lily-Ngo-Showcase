from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece


def test_rook_in_center_empty_board():
    board = Board()
    rook = make_piece("rook", "white", (3, 3))

    board.place_piece(rook, (3, 3))

    moves = get_pseudo_legal_moves(board, rook)

    assert (3, 0) in moves
    assert (3, 7) in moves
    assert (0, 3) in moves
    assert (7, 3) in moves
    assert len(moves) == 14


def test_rook_blocked_by_friendly_piece():
    board = Board()
    rook = make_piece("rook", "white", (3, 3))
    blocker = make_piece("pawn", "white", (3, 5))

    board.place_piece(rook, (3, 3))
    board.place_piece(blocker, (3, 5))

    moves = get_pseudo_legal_moves(board, rook)

    assert (3, 4) in moves
    assert (3, 5) not in moves
    assert (3, 6) not in moves


def test_rook_can_capture_enemy_but_not_move_beyond():
    board = Board()
    rook = make_piece("rook", "white", (3, 3))
    enemy = make_piece("bishop", "black", (3, 5))

    board.place_piece(rook, (3, 3))
    board.place_piece(enemy, (3, 5))

    moves = get_pseudo_legal_moves(board, rook)

    assert (3, 4) in moves
    assert (3, 5) in moves
    assert (3, 6) not in moves


def test_bishop_in_center_empty_board():
    board = Board()
    bishop = make_piece("bishop", "white", (3, 3))

    board.place_piece(bishop, (3, 3))

    moves = get_pseudo_legal_moves(board, bishop)

    assert (0, 0) in moves
    assert (6, 6) in moves
    assert (0, 6) in moves
    assert (6, 0) in moves


def test_knight_has_8_moves_in_center():
    board = Board()
    knight = make_piece("knight", "white", (3, 3))

    board.place_piece(knight, (3, 3))

    moves = get_pseudo_legal_moves(board, knight)

    assert len(moves) == 8
    assert (5, 4) in moves
    assert (1, 2) in moves


def test_knight_can_jump_over_pieces():
    board = Board()
    knight = make_piece("knight", "white", (3, 3))

    board.place_piece(knight, (3, 3))

    surrounding_squares = [
        (2, 2), (2, 3), (2, 4),
        (3, 2),         (3, 4),
        (4, 2), (4, 3), (4, 4),
    ]

    for square in surrounding_squares:
        board.place_piece(make_piece("pawn", "white", square), square)

    moves = get_pseudo_legal_moves(board, knight)

    assert len(moves) == 8


def test_knight_cannot_capture_friendly_piece():
    board = Board()
    knight = make_piece("knight", "white", (3, 3))
    friendly = make_piece("pawn", "white", (5, 4))

    board.place_piece(knight, (3, 3))
    board.place_piece(friendly, (5, 4))

    moves = get_pseudo_legal_moves(board, knight)

    assert (5, 4) not in moves


def test_knight_can_capture_enemy_piece():
    board = Board()
    knight = make_piece("knight", "white", (3, 3))
    enemy = make_piece("pawn", "black", (5, 4))

    board.place_piece(knight, (3, 3))
    board.place_piece(enemy, (5, 4))

    moves = get_pseudo_legal_moves(board, knight)

    assert (5, 4) in moves


def test_king_in_center():
    board = Board()
    king = make_piece("king", "white", (3, 3))

    board.place_piece(king, (3, 3))

    moves = get_pseudo_legal_moves(board, king)

    assert len(moves) == 8


def test_king_near_edge_only_has_on_board_moves():
    board = Board()
    king = make_piece("king", "white", (0, 0))

    board.place_piece(king, (0, 0))

    moves = get_pseudo_legal_moves(board, king)

    assert set(moves) == {(0, 1), (1, 0), (1, 1)}


def test_white_pawn_moves_forward():
    board = Board()
    pawn = make_piece("pawn", "white", (1, 0))

    board.place_piece(pawn, (1, 0))

    moves = get_pseudo_legal_moves(board, pawn)

    assert (2, 0) in moves


def test_black_pawn_moves_forward():
    board = Board()
    pawn = make_piece("pawn", "black", (6, 0))

    board.place_piece(pawn, (6, 0))

    moves = get_pseudo_legal_moves(board, pawn)

    assert (5, 0) in moves


def test_pawn_captures_diagonally():
    board = Board()
    pawn = make_piece("pawn", "white", (1, 1))
    enemy = make_piece("knight", "black", (2, 2))

    board.place_piece(pawn, (1, 1))
    board.place_piece(enemy, (2, 2))

    moves = get_pseudo_legal_moves(board, pawn)

    assert (2, 2) in moves


def test_pawn_cannot_move_forward_into_occupied_square():
    board = Board()
    pawn = make_piece("pawn", "white", (1, 1))
    blocker = make_piece("knight", "black", (2, 1))

    board.place_piece(pawn, (1, 1))
    board.place_piece(blocker, (2, 1))

    moves = get_pseudo_legal_moves(board, pawn)

    assert (2, 1) not in moves

