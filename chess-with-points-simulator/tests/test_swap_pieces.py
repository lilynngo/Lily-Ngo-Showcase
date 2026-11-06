from src.army import generate_group_a_army
from src.piece_loader import load_piece_definitions_from_json
from src.board import Board
from src.moves import get_pseudo_legal_moves
from src.simulation import (
    execute_swap,
    get_all_legal_moves_for_player,
    get_swap_moves_for_piece,
    simulate_game_with_armies,
)
from tests.helpers import make_piece

def test_adept_can_swap_with_non_adjacent_friendly_swap_piece():
    board = Board()
    adept_1 = make_piece("adept", "white", (0, 0))
    adept_2 = make_piece("adept", "white", (7, 7))

    board.place_piece(adept_1, (0, 0))
    board.place_piece(adept_2, (7, 7))

    swaps = get_swap_moves_for_piece(board, adept_1)

    assert ((0, 0), (7, 7)) in swaps

def test_adept_moves_like_king():
    board = Board()
    adept = make_piece("adept", "white", (3, 3))

    board.place_piece(adept, (3, 3))

    moves = get_pseudo_legal_moves(board, adept)

    assert len(moves) == 8
    assert (2, 2) in moves
    assert (4, 4) in moves


def test_adept_cannot_swap_with_enemy_piece():
    board = Board()
    adept = make_piece("adept", "white", (3, 3))
    enemy = make_piece("pawn", "black", (3, 4))

    board.place_piece(adept, (3, 3))
    board.place_piece(enemy, (3, 4))

    swaps = get_swap_moves_for_piece(board, adept)

    assert swaps == []


def test_adept_can_swap_with_friendly_swap_piece_anywhere():
    board = Board()
    adept_1 = make_piece("adept", "white", (3, 3))
    adept_2 = make_piece("adept", "white", (7, 7))

    board.place_piece(adept_1, (3, 3))
    board.place_piece(adept_2, (7, 7))

    swaps = get_swap_moves_for_piece(board, adept_1)

    assert ((3, 3), (7, 7)) in swaps


def test_execute_swap_switches_piece_positions():
    board = Board()
    adept = make_piece("adept", "white", (3, 3))
    pawn = make_piece("pawn", "white", (3, 4))

    board.place_piece(adept, (3, 3))
    board.place_piece(pawn, (3, 4))

    result = execute_swap(board, (3, 3), (3, 4))

    assert result["swap_used"] is True
    assert board.get_piece_at((3, 3)) == pawn
    assert board.get_piece_at((3, 4)) == adept
    assert adept.position == (3, 4)
    assert pawn.position == (3, 3)

def test_swap_of_pinned_piece_is_legal_if_replacement_still_blocks_check():
    board = Board()

    black_king = make_piece("king", "black", (7, 4))
    black_adept_1 = make_piece("adept", "black", (6, 4))
    black_adept_2 = make_piece("adept", "black", (6, 0))
    white_rook = make_piece("rook", "white", (0, 4))

    board.place_piece(black_king, (7, 4))
    board.place_piece(black_adept_1, (6, 4))
    board.place_piece(black_adept_2, (6, 0))
    board.place_piece(white_rook, (0, 4))

    actions = get_all_legal_moves_for_player(board, "black")

    legal_swap = {
        "type": "swap",
        "from_square": (6, 4),
        "to_square": (6, 0),
    }

    assert legal_swap in actions

def test_pegasus_can_swap_with_friendly_adept():
    board = Board()

    pegasus = make_piece("pegasus", "white", (3, 3))
    adept = make_piece("adept", "white", (6, 6))

    board.place_piece(pegasus, (3, 3))
    board.place_piece(adept, (6, 6))

    swaps = get_swap_moves_for_piece(board, pegasus)

    assert ((3, 3), (6, 6)) in swaps
def test_adept_can_swap_with_friendly_pegasus():
    board = Board()

    adept = make_piece("adept", "white", (3, 3))
    pegasus = make_piece("pegasus", "white", (6, 6))

    board.place_piece(adept, (3, 3))
    board.place_piece(pegasus, (6, 6))

    swaps = get_swap_moves_for_piece(board, adept)

    assert ((3, 3), (6, 6)) in swaps
def test_pegasus_cannot_swap_with_enemy_pegasus():
    board = Board()

    pegasus_1 = make_piece("pegasus", "white", (3, 3))
    pegasus_2 = make_piece("pegasus", "black", (6, 6))

    board.place_piece(pegasus_1, (3, 3))
    board.place_piece(pegasus_2, (6, 6))

    swaps = get_swap_moves_for_piece(board, pegasus_1)

    assert ((3, 3), (6, 6)) not in swaps
def test_pegasus_cannot_swap_with_friendly_non_swap_piece():
    board = Board()

    pegasus = make_piece("pegasus", "white", (3, 3))
    pawn = make_piece("pawn", "white", (6, 6))

    board.place_piece(pegasus, (3, 3))
    board.place_piece(pawn, (6, 6))

    swaps = get_swap_moves_for_piece(board, pegasus)

    assert ((3, 3), (6, 6)) not in swaps
def test_execute_swap_works_between_pegasus_and_adept():
    board = Board()

    pegasus = make_piece("pegasus", "white", (3, 3))
    adept = make_piece("adept", "white", (6, 6))

    board.place_piece(pegasus, (3, 3))
    board.place_piece(adept, (6, 6))

    result = execute_swap(board, (3, 3), (6, 6))

    assert result["swap_used"] is True
    assert result["swapped_with"] == "adept"

    assert board.get_piece_at((3, 3)) == adept
    assert board.get_piece_at((6, 6)) == pegasus

    assert pegasus.position == (6, 6)
    assert adept.position == (3, 3)
def test_army_with_multiple_swap_pieces_can_simulate():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    white_army = generate_group_a_army(pieces)
    black_army = generate_group_a_army(pieces)

    record = simulate_game_with_armies(
        white_army=white_army,
        black_army=black_army,
        max_turns=50,
        seed=123,
    )

    assert record.total_moves <= 50
    assert record.reason in {
        "checkmate",
        "no legal actions",
        "no legal moves",
        "move limit",
    }