from src.piece_loader import load_piece_definitions_from_json

def test_loads_pawn_from_json():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    pawn = pieces["pawn"]

    assert pawn.cost == 10
    assert pawn.type == "commoner"
    assert pawn.movement == "pawn"


def test_loads_knight_from_json():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    knight = pieces["knight"]

    assert knight.cost == 30
    assert knight.type == "noble"
    assert knight.movement == "knight"

def test_loads_king_status_from_json():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    king = pieces["king"]

    assert king.cost == 0
    assert king.is_king_status is True


def test_loads_queen_from_json():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    queen = pieces["queen"]

    assert queen.cost == 100
    assert queen.type == "noble"
    assert queen.movement == "queen"


def test_all_pieces_have_required_fields():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    for piece in pieces.values():
        assert piece.id is not None
        assert piece.name
        assert piece.type
        assert piece.cost is not None
        assert piece.movement
        assert isinstance(piece.traits, list)
        assert isinstance(piece.drawbacks, list)
        assert isinstance(piece.is_king_status, bool)