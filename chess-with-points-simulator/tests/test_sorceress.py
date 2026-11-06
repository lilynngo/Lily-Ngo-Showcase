from src.board import Board
from src.moves import get_pseudo_legal_moves
from src.simulation import get_swap_moves_for_piece, execute_swap
from tests.helpers import make_piece


def test_sorceress_moves_any_direction_up_to_5():
    board = Board()
    sorceress = make_piece("sorceress", "white", (3, 3))

    board.place_piece(sorceress, (3, 3))

    moves = get_pseudo_legal_moves(board, sorceress)

    assert (3, 4) in moves
    assert (3, 7) in moves
    assert (4, 3) in moves
    assert (7, 3) in moves
    assert (4, 4) in moves
    assert (7, 7) in moves

def test_sorceress_does_not_move_beyond_5():
    board = Board()
    sorceress = make_piece("sorceress", "white", (1, 1))

    board.place_piece(sorceress, (1, 1))

    moves = get_pseudo_legal_moves(board, sorceress)

    assert (6, 6) in moves
    assert (7, 7) not in moves

def test_sorceress_movement_is_blocked_by_friendly_piece():
    board = Board()
    sorceress = make_piece("sorceress", "white", (3, 3))
    blocker = make_piece("pawn", "white", (3, 5))

    board.place_piece(sorceress, (3, 3))
    board.place_piece(blocker, (3, 5))

    moves = get_pseudo_legal_moves(board, sorceress)

    assert (3, 4) in moves
    assert (3, 5) not in moves
    assert (3, 6) not in moves
    assert (3, 7) not in moves

def test_sorceress_can_capture_and_stops_after_enemy():
    board = Board()
    sorceress = make_piece("sorceress", "white", (3, 3))
    enemy = make_piece("pawn", "black", (3, 5))

    board.place_piece(sorceress, (3, 3))
    board.place_piece(enemy, (3, 5))

    moves = get_pseudo_legal_moves(board, sorceress)

    assert (3, 4) in moves
    assert (3, 5) in moves
    assert (3, 6) not in moves
    assert (3, 7) not in moves

def test_sorceress_can_swap_with_friendly_adept():
    board = Board()
    sorceress = make_piece("sorceress", "white", (3, 3))
    adept = make_piece("adept", "white", (6, 6))

    board.place_piece(sorceress, (3, 3))
    board.place_piece(adept, (6, 6))

    swaps = get_swap_moves_for_piece(board, sorceress)

    assert ((3, 3), (6, 6)) in swaps

def test_adept_can_swap_with_sorceress():
    board = Board()
    adept = make_piece("adept", "white", (3, 3))
    sorceress = make_piece("sorceress", "white", (6, 6))

    board.place_piece(adept, (3, 3))
    board.place_piece(sorceress, (6, 6))

    swaps = get_swap_moves_for_piece(board, adept)

    assert ((3, 3), (6, 6)) in swaps

def test_execute_swap_works_between_sorceress_and_adept():
    board = Board()
    sorceress = make_piece("sorceress", "white", (3, 3))
    adept = make_piece("adept", "white", (6, 6))

    board.place_piece(sorceress, (3, 3))
    board.place_piece(adept, (6, 6))

    result = execute_swap(board, (3, 3), (6, 6))

    assert result["swap_used"] is True
    assert result["swapped_with"] == "adept"

    assert board.get_piece_at((3, 3)) == adept
    assert board.get_piece_at((6, 6)) == sorceress

def test_sorceress_cannot_swap_with_non_swap_piece():
    board = Board()
    sorceress = make_piece("sorceress", "white", (3, 3))
    pawn = make_piece("pawn", "white", (6, 6))

    board.place_piece(sorceress, (3, 3))
    board.place_piece(pawn, (6, 6))

    swaps = get_swap_moves_for_piece(board, sorceress)

    assert ((3, 3), (6, 6)) not in swaps

def test_sorceress_does_not_have_king_status():
    sorceress = make_piece("sorceress", "white", (3, 3))

    assert sorceress.definition.is_king_status is False