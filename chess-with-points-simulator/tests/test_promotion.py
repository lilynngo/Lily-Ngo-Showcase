from src.moves import is_black_square, is_white_square
from src.army import Army
from src.simulation import can_promote_to_piece, get_starting_noble_ids_from_army
from tests.helpers import get_piece_definition

def test_can_only_promote_to_starting_noble():
    queen = get_piece_definition("queen")
    rook = get_piece_definition("rook")

    starting_noble_lineup = {
        "white": [queen.id],
        "black": [rook.id],
    }

    assert can_promote_to_piece(
        player="white",
        promotion_square=(0, 1),
        target_definition=queen,
        starting_noble_lineup=starting_noble_lineup,
    ) is True

    assert can_promote_to_piece(
        player="white",
        promotion_square=(0, 1),
        target_definition=rook,
        starting_noble_lineup=starting_noble_lineup,
    ) is False
def test_queen_of_air_promotion_requires_white_square():
    queen_of_air = get_piece_definition("queen of air")

    starting_noble_lineup = {
        "white": [queen_of_air.id],
    }

    assert is_white_square((0, 1)) is True
    assert can_promote_to_piece(
        player="white",
        promotion_square=(0, 1),
        target_definition=queen_of_air,
        starting_noble_lineup=starting_noble_lineup,
    ) is True

    assert is_black_square((0, 0)) is True
    assert can_promote_to_piece(
        player="white",
        promotion_square=(0, 0),
        target_definition=queen_of_air,
        starting_noble_lineup=starting_noble_lineup,
    ) is False


def test_queen_of_darkness_promotion_requires_black_square():
    queen_of_darkness = get_piece_definition("queen of darkness")

    starting_noble_lineup = {
        "white": [queen_of_darkness.id],
    }

    assert is_black_square((0, 0)) is True
    assert can_promote_to_piece(
        player="white",
        promotion_square=(0, 0),
        target_definition=queen_of_darkness,
        starting_noble_lineup=starting_noble_lineup,
    ) is True

    assert is_white_square((0, 1)) is True
    assert can_promote_to_piece(
        player="white",
        promotion_square=(0, 1),
        target_definition=queen_of_darkness,
        starting_noble_lineup=starting_noble_lineup,
    ) is False

def test_cannot_promote_to_piece_not_in_starting_noble_lineup():
    queen_of_air = get_piece_definition("queen of air")
    queen = get_piece_definition("queen")

    starting_noble_lineup = {
        "white": [queen.id],
    }

    assert can_promote_to_piece(
        player="white",
        promotion_square=(0, 1),
        target_definition=queen_of_air,
        starting_noble_lineup=starting_noble_lineup,
    ) is False

def test_get_starting_noble_ids_includes_noble_pieces():
    queen = get_piece_definition("queen")
    rook = get_piece_definition("rook")

    army = Army([
        queen,
        rook,
    ])

    noble_ids = get_starting_noble_ids_from_army(army)

    assert queen.id in noble_ids
    assert rook.id in noble_ids

def test_get_starting_noble_ids_excludes_commoner_pieces():
    queen = get_piece_definition("queen")
    pawn = get_piece_definition("pawn")
    shield_bearer = get_piece_definition("shield bearer")

    army = Army([
        queen,
        pawn,
        shield_bearer,
    ])

    noble_ids = get_starting_noble_ids_from_army(army)

    assert queen.id in noble_ids
    assert pawn.id not in noble_ids
    assert shield_bearer.id not in noble_ids

def test_get_starting_noble_ids_includes_both_pieces_for_current_army_system():
    wild_stallion = get_piece_definition("wild stallion")
    queen = get_piece_definition("queen")
    pawn = get_piece_definition("pawn")

    army = Army([
        wild_stallion,
        queen,
        pawn,
    ])

    noble_ids = get_starting_noble_ids_from_army(army)

    assert wild_stallion.id in noble_ids
    assert queen.id in noble_ids
    assert pawn.id not in noble_ids

def test_get_starting_noble_ids_empty_army():
    army = Army([])

    noble_ids = get_starting_noble_ids_from_army(army)

    assert noble_ids == []

