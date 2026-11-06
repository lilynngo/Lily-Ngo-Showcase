from src.board import Board
from src.moves import get_pseudo_legal_moves
from src.simulation import get_shielded_capture_target
from tests.helpers import make_piece

def test_joan_of_arc_moves_like_queen():
    board = Board()
    joan = make_piece("joan of arc", "white", (3, 3))

    board.place_piece(joan, (3, 3))

    moves = get_pseudo_legal_moves(board, joan)

    assert (3, 7) in moves
    assert (7, 3) in moves
    assert (6, 6) in moves
    assert (0, 3) in moves
    assert (3, 0) in moves
    assert (0, 0) in moves

def test_joan_of_arc_movement_blocked_by_friendly_piece():
    board = Board()
    joan = make_piece("joan of arc", "white", (3, 3))
    blocker = make_piece("pawn", "white", (3, 5))

    board.place_piece(joan, (3, 3))
    board.place_piece(blocker, (3, 5))

    moves = get_pseudo_legal_moves(board, joan)

    assert (3, 4) in moves
    assert (3, 5) not in moves
    assert (3, 6) not in moves

def test_joan_of_arc_can_capture_and_stops_after_enemy():
    board = Board()
    joan = make_piece("joan of arc", "white", (3, 3))
    enemy = make_piece("pawn", "black", (3, 5))

    board.place_piece(joan, (3, 3))
    board.place_piece(enemy, (3, 5))

    moves = get_pseudo_legal_moves(board, joan)

    assert (3, 4) in moves
    assert (3, 5) in moves
    assert (3, 6) not in moves

def test_joan_of_arc_has_shield_counter():
    joan = make_piece("joan of arc", "white", (3, 3))

    assert "shield" in joan.definition.traits
    assert joan.shield_charges == 1

def test_joan_of_arc_triggers_shield_when_targeted():
    board = Board()

    attacker = make_piece("rook", "black", (3, 0))
    joan = make_piece("joan of arc", "white", (3, 3))

    board.place_piece(attacker, (3, 0))
    board.place_piece(joan, (3, 3))

    result = get_shielded_capture_target(board, (3, 0), (3, 3))

    assert result == joan

def test_joan_of_arc_does_not_protect_adjacent_piece():
    board = Board()

    attacker = make_piece("rook", "black", (3, 0))
    joan = make_piece("joan of arc", "white", (3, 3))
    pawn = make_piece("pawn", "white", (3, 4))

    board.place_piece(attacker, (3, 0))
    board.place_piece(joan, (3, 3))
    board.place_piece(pawn, (3, 4))

    result = get_shielded_capture_target(board, (3, 0), (3, 4))

    assert result is None

def test_joan_of_arc_does_not_have_king_status():
    joan = make_piece("joan of arc", "white", (3, 3))

    assert joan.definition.is_king_status is False

