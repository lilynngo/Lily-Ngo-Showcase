from src.board import Board
from src.moves import get_pseudo_legal_moves
from src.simulation import get_swap_moves_for_piece, execute_swap
from tests.helpers import make_piece

def test_arcane_priest_moves_diagonally_up_to_3():
    board = Board()
    priest = make_piece("arcane priest", "white", (3, 3))

    board.place_piece(priest, (3, 3))

    moves = get_pseudo_legal_moves(board, priest)

    assert (4, 4) in moves
    assert (5, 5) in moves
    assert (6, 6) in moves
    assert (7, 7) not in moves

def test_arcane_priest_diagonal_movement_is_blocked():
    board = Board()
    priest = make_piece("arcane priest", "white", (3, 3))
    blocker = make_piece("pawn", "white", (4, 4))

    board.place_piece(priest, (3, 3))
    board.place_piece(blocker, (4, 4))

    moves = get_pseudo_legal_moves(board, priest)

    assert (4, 4) not in moves
    assert (5, 5) not in moves
    assert (6, 6) not in moves

def test_arcane_priest_can_capture_diagonally():
    board = Board()
    priest = make_piece("arcane priest", "white", (3, 3))
    enemy = make_piece("pawn", "black", (5, 5))

    board.place_piece(priest, (3, 3))
    board.place_piece(enemy, (5, 5))

    moves = get_pseudo_legal_moves(board, priest)

    assert (5, 5) in moves
    assert (6, 6) not in moves

def test_arcane_priest_can_swap_with_friendly_adept():
    board = Board()
    priest = make_piece("arcane priest", "white", (3, 3))
    adept = make_piece("adept", "white", (6, 6))

    board.place_piece(priest, (3, 3))
    board.place_piece(adept, (6, 6))

    swaps = get_swap_moves_for_piece(board, priest)

    assert ((3, 3), (6, 6)) in swaps

def test_adept_can_swap_with_arcane_priest():
    board = Board()
    adept = make_piece("adept", "white", (3, 3))
    priest = make_piece("arcane priest", "white", (6, 6))

    board.place_piece(adept, (3, 3))
    board.place_piece(priest, (6, 6))

    swaps = get_swap_moves_for_piece(board, adept)

    assert ((3, 3), (6, 6)) in swaps

def test_execute_swap_works_between_arcane_priest_and_adept():
    board = Board()
    priest = make_piece("arcane priest", "white", (3, 3))
    adept = make_piece("adept", "white", (6, 6))

    board.place_piece(priest, (3, 3))
    board.place_piece(adept, (6, 6))

    result = execute_swap(board, (3, 3), (6, 6))

    assert result["swap_used"] is True
    assert result["swapped_with"] == "adept"

    assert board.get_piece_at((3, 3)) == adept
    assert board.get_piece_at((6, 6)) == priest

def test_arcane_priest_cannot_swap_with_non_swap_piece():
    board = Board()
    priest = make_piece("arcane priest", "white", (3, 3))
    pawn = make_piece("pawn", "white", (6, 6))

    board.place_piece(priest, (3, 3))
    board.place_piece(pawn, (6, 6))

    swaps = get_swap_moves_for_piece(board, priest)

    assert ((3, 3), (6, 6)) not in swaps

