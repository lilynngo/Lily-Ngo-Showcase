from src.rules import get_legal_moves, is_in_check
from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece

def test_the_old_queen_moves_like_queen():
    board = Board()
    queen = make_piece("the old queen", "white", (3, 3))

    board.place_piece(queen, (3, 3))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 7) in moves
    assert (7, 3) in moves
    assert (6, 6) in moves
    assert (0, 3) in moves
    assert (3, 0) in moves
    assert (0, 0) in moves

def test_the_old_queen_cannot_jump_friendly_piece():
    board = Board()

    queen = make_piece("the old queen", "white", (3, 3))
    friendly = make_piece("pawn", "white", (3, 5))

    board.place_piece(queen, (3, 3))
    board.place_piece(friendly, (3, 5))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 4) in moves
    assert (3, 5) not in moves
    assert (3, 6) not in moves

def test_the_old_queen_can_capture_and_stops():
    board = Board()

    queen = make_piece("the old queen", "white", (3, 3))
    enemy = make_piece("pawn", "black", (3, 5))

    board.place_piece(queen, (3, 3))
    board.place_piece(enemy, (3, 5))

    moves = get_pseudo_legal_moves(board, queen)

    assert (3, 4) in moves
    assert (3, 5) in moves
    assert (3, 6) not in moves

def test_the_old_queen_has_king_status():
    queen = make_piece("the old queen", "white", (3, 3))

    assert queen.definition.is_king_status is True

def test_old_queen_legal_moves_must_resolve_check_on_both_king_status_pieces():
    board = Board()

    king = make_piece("king", "white", (0, 4))
    old_queen = make_piece("the old queen", "white", (2, 5))

    # This rook attacks the king horizontally along row 0.
    king_attacker = make_piece("rook", "black", (0, 7))

    # This rook attacks the old queen vertically along column 5.
    old_queen_attacker = make_piece("rook", "black", (7, 5))

    board.place_piece(king, (0, 4))
    board.place_piece(old_queen, (2, 5))
    board.place_piece(king_attacker, (0, 7))
    board.place_piece(old_queen_attacker, (7, 5))

    assert is_in_check(board, "white") is True

    legal_moves = get_legal_moves(board, old_queen)

    # This is the only move that fixes both checks:
    # - captures the rook checking the king
    # - moves the old queen off the attacked column
    assert legal_moves == [(0, 7)]