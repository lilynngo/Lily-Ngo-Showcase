from src.simulation import get_shielded_capture_target
from src.board import Board
from src.moves import get_pseudo_legal_moves
from tests.helpers import make_piece


def test_armored_chariot_moves_up_to_2_squares_orthogonally():
    board = Board()
    chariot = make_piece("armored chariot", "white", (3, 3))

    board.place_piece(chariot, (3, 3))

    moves = get_pseudo_legal_moves(board, chariot)

    assert (3, 4) in moves
    assert (3, 5) in moves
    assert (3, 6) not in moves

def test_armored_chariot_has_shield_counter():
    chariot = make_piece("armored chariot", "white", (3, 3))

    assert "shield" in chariot.definition.traits
    assert chariot.shield_charges == 1

def test_armored_chariot_triggers_shield_when_targeted():
    board = Board()

    attacker = make_piece("rook", "black", (3, 0))
    target = make_piece("armored chariot", "white", (3, 3))

    board.place_piece(attacker, (3, 0))
    board.place_piece(target, (3, 3))

    result = get_shielded_capture_target(board, (3, 0), (3, 3))

    assert result == target

def test_armored_chariot_does_not_protect_adjacent_piece():
    board = Board()

    attacker = make_piece("rook", "black", (3, 0))
    chariot = make_piece("armored chariot", "white", (3, 3))
    pawn = make_piece("pawn", "white", (3, 4))

    board.place_piece(attacker, (3, 0))
    board.place_piece(chariot, (3, 3))
    board.place_piece(pawn, (3, 4))

    result = get_shielded_capture_target(board, (3, 0), (3, 4))

    assert result is None

