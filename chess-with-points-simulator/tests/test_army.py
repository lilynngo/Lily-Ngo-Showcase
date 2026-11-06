from src.army import Army, generate_group_a_army, generate_legal_standard_armies, generate_standard_army, validate_army
from src.piece_loader import load_piece_definitions_from_json


def test_standard_army_has_16_pieces():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    army = generate_standard_army(pieces)

    assert army.size() == 16


def test_standard_army_has_8_commoners():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    army = generate_standard_army(pieces)

    assert army.count_by_type("Commoner") == 8


def test_standard_army_has_8_nobles():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    army = generate_standard_army(pieces)

    assert army.count_by_type("Noble") == 8


def test_standard_army_has_king_status_piece():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    army = generate_standard_army(pieces)

    assert army.has_king_status_piece() is True


def test_standard_army_has_no_more_than_one_king():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    army = generate_standard_army(pieces)

    assert army.count_by_name("King") == 1


def test_standard_army_cost_does_not_exceed_budget():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    army = generate_standard_army(pieces)

    assert army.total_cost() <= 400


def test_standard_army_is_valid():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    army = generate_standard_army(pieces)

    is_valid, errors = validate_army(army)

    assert is_valid is True
    assert errors == []

def test_generate_legal_standard_armies_returns_valid_armies():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    armies = generate_legal_standard_armies(pieces)

    assert len(armies) > 0

    for army in armies:
        is_valid, errors = validate_army(army)

        assert is_valid is True
        assert errors == []

def test_group_a_test_army_is_valid():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    army = generate_group_a_army(pieces)

    is_valid, errors = validate_army(army)

    assert is_valid is True
    assert errors == []