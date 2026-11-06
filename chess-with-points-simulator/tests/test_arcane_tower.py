from src.board import Board
from src.moves import get_pseudo_legal_moves
from src.simulation import get_swap_moves_for_piece, execute_swap
from tests.helpers import make_piece

def test_arcane_tower_moves_like_king():
    board = Board()
    tower = make_piece("arcane tower", "white", (3, 3))

    board.place_piece(tower, (3, 3))

    moves = get_pseudo_legal_moves(board, tower)

    expected_moves = {
        (2, 2), (2, 3), (2, 4),
        (3, 2),         (3, 4),
        (4, 2), (4, 3), (4, 4),
    }

    for square in expected_moves:
        assert square in moves

def test_arcane_tower_does_not_move_farther_than_king():
    board = Board()
    tower = make_piece("arcane tower", "white", (3, 3))

    board.place_piece(tower, (3, 3))

    moves = get_pseudo_legal_moves(board, tower)

    assert (5, 5) not in moves
    assert (3, 5) not in moves
    assert (1, 3) not in moves

def test_arcane_tower_can_swap_with_friendly_adept():
    board = Board()
    tower = make_piece("arcane tower", "white", (3, 3))
    adept = make_piece("adept", "white", (6, 6))

    board.place_piece(tower, (3, 3))
    board.place_piece(adept, (6, 6))

    swaps = get_swap_moves_for_piece(board, tower)

    assert ((3, 3), (6, 6)) in swaps

def test_adept_can_swap_with_arcane_tower():
    board = Board()
    adept = make_piece("adept", "white", (3, 3))
    tower = make_piece("arcane tower", "white", (6, 6))

    board.place_piece(adept, (3, 3))
    board.place_piece(tower, (6, 6))

    swaps = get_swap_moves_for_piece(board, adept)

    assert ((3, 3), (6, 6)) in swaps

def test_execute_swap_works_between_arcane_tower_and_adept():
    board = Board()
    tower = make_piece("arcane tower", "white", (3, 3))
    adept = make_piece("adept", "white", (6, 6))

    board.place_piece(tower, (3, 3))
    board.place_piece(adept, (6, 6))

    result = execute_swap(board, (3, 3), (6, 6))

    assert result["swap_used"] is True
    assert result["swapped_with"] == "adept"

    assert board.get_piece_at((3, 3)) == adept
    assert board.get_piece_at((6, 6)) == tower

def test_arcane_tower_cannot_swap_with_non_swap_piece():
    board = Board()
    tower = make_piece("arcane tower", "white", (3, 3))
    pawn = make_piece("pawn", "white", (6, 6))

    board.place_piece(tower, (3, 3))
    board.place_piece(pawn, (6, 6))

    swaps = get_swap_moves_for_piece(board, tower)

    assert ((3, 3), (6, 6)) not in swaps

def test_arcane_tower_does_not_have_king_status():
    tower = make_piece("arcane tower", "white", (3, 3))

    assert tower.definition.is_king_status is False

