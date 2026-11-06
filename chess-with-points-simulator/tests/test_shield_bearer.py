from src.simulation import apply_capture_or_shield_block, choose_random_move, get_shield_block_for_move, get_shielded_capture_target
from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece

def test_shield_piece_starts_with_counter():
    piece = make_piece("shield bearer", "white", (3, 3))

    assert "shield" in piece.definition.traits
    assert piece.shield_charges == 1

def test_non_shield_piece_does_not_trigger_shield():
    board = Board()

    attacker = make_piece("rook", "black", (3, 0))
    target = make_piece("pawn", "white", (3, 3))

    board.place_piece(attacker, (3, 0))
    board.place_piece(target, (3, 3))

    result = get_shielded_capture_target(board, (3, 0), (3, 3))

    assert result is None

def test_shield_triggers_when_shielded_piece_is_targeted():
    board = Board()

    attacker = make_piece("rook", "black", (3, 0))
    target = make_piece("shield bearer", "white", (3, 3))

    board.place_piece(attacker, (3, 0))
    board.place_piece(target, (3, 3))

    result = get_shielded_capture_target(board, (3, 0), (3, 3))

    assert result == target

def test_shield_does_not_protect_adjacent_piece():
    board = Board()

    shield_bearer = make_piece("shield bearer", "white", (3, 3))
    pawn = make_piece("pawn", "white", (3, 4))
    attacker = make_piece("rook", "black", (3, 0))

    board.place_piece(attacker, (3, 0))
    board.place_piece(shield_bearer, (3, 3))
    board.place_piece(pawn, (3, 4))

    result = get_shielded_capture_target(board, (3, 0), (3, 4))

    assert result is None

def test_shield_activation_spends_target_counter():
    board = Board()

    attacker = make_piece("rook", "black", (3, 0))
    target = make_piece("shield bearer", "white", (3, 3))

    board.place_piece(attacker, (3, 0))
    board.place_piece(target, (3, 3))

    shielded_target = get_shielded_capture_target(board, (3, 0), (3, 3))

    assert shielded_target == target

    shielded_target.shield_charges -= 1

    assert target.shield_charges == 0

    second_result = get_shielded_capture_target(board, (3, 0), (3, 3))

    assert second_result is None

def test_shield_activation_spends_target_counter():
    board = Board()

    attacker = make_piece("rook", "black", (3, 0))
    target = make_piece("shield bearer", "white", (3, 3))

    board.place_piece(attacker, (3, 0))
    board.place_piece(target, (3, 3))

    shielded_target = get_shielded_capture_target(
        board,
        (3, 0),
        (3, 3),
    )

    assert shielded_target == target
    assert target.shield_charges == 1

    shielded_target.shield_charges -= 1

    assert target.shield_charges == 0

    second_result = get_shielded_capture_target(
        board,
        (3, 0),
        (3, 3),
    )

    assert second_result is None