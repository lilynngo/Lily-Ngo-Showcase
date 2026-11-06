import random
import pytest

from src.army import (
    can_piece_fill_role,
    generate_random_army_assignments,
    get_commoner_row,
    get_noble_row,
    get_starting_noble_lineup,
)
from src.moves import is_white_square, is_black_square
from tests.helpers import get_piece_definition


def test_noble_piece_can_fill_noble_role():
    queen = get_piece_definition("queen")

    assert can_piece_fill_role(queen, "noble") is True
    assert can_piece_fill_role(queen, "commoner") is False


def test_commoner_piece_can_fill_commoner_role():
    pawn = get_piece_definition("pawn")

    assert can_piece_fill_role(pawn, "commoner") is True
    assert can_piece_fill_role(pawn, "noble") is False


def test_both_piece_can_fill_either_role():
    wild_stallion = get_piece_definition("wild stallion")

    assert can_piece_fill_role(wild_stallion, "noble") is True
    assert can_piece_fill_role(wild_stallion, "commoner") is True


def test_army_generation_places_nobles_on_noble_row():
    king = get_piece_definition("king")
    queen = get_piece_definition("queen")

    assignments = generate_random_army_assignments(
        nobles=[king, queen],
        commoners=[],
        owner="white",
        rng=random.Random(1),
    )

    noble_row = get_noble_row("white")

    for assignment in assignments:
        assert assignment["role"] == "noble"
        assert assignment["square"][0] == noble_row


def test_army_generation_places_commoners_on_commoner_row():
    pawn = get_piece_definition("pawn")
    shield_bearer = get_piece_definition("shield bearer")

    assignments = generate_random_army_assignments(
        nobles=[],
        commoners=[pawn, shield_bearer],
        owner="white",
        rng=random.Random(2),
    )

    commoner_row = get_commoner_row("white")

    for assignment in assignments:
        assert assignment["role"] == "commoner"
        assert assignment["square"][0] == commoner_row


def test_army_generation_has_no_duplicate_squares():
    king = get_piece_definition("king")
    queen = get_piece_definition("queen")
    rook = get_piece_definition("rook")
    pawn = get_piece_definition("pawn")
    shield_bearer = get_piece_definition("shield bearer")

    assignments = generate_random_army_assignments(
        nobles=[king, queen, rook],
        commoners=[pawn, shield_bearer],
        owner="white",
        rng=random.Random(3),
    )

    squares = [assignment["square"] for assignment in assignments]

    assert len(squares) == len(set(squares))


def test_queen_of_air_starts_on_white_square():
    queen_of_air = get_piece_definition("queen of air")
    king = get_piece_definition("king")

    assignments = generate_random_army_assignments(
        nobles=[king, queen_of_air],
        commoners=[],
        owner="white",
        rng=random.Random(4),
    )

    queen_assignment = next(
        assignment
        for assignment in assignments
        if assignment["definition"].name == "queen of air"
    )

    assert is_white_square(queen_assignment["square"]) is True


def test_queen_of_darkness_starts_on_black_square():
    queen_of_darkness = get_piece_definition("queen of darkness")
    king = get_piece_definition("king")

    assignments = generate_random_army_assignments(
        nobles=[king, queen_of_darkness],
        commoners=[],
        owner="white",
        rng=random.Random(5),
    )

    queen_assignment = next(
        assignment
        for assignment in assignments
        if assignment["definition"].name == "queen of darkness"
    )

    assert is_black_square(queen_assignment["square"]) is True


def test_commoner_cannot_be_in_noble_list():
    pawn = get_piece_definition("pawn")

    with pytest.raises(ValueError):
        generate_random_army_assignments(
            nobles=[pawn],
            commoners=[],
            owner="white",
            rng=random.Random(6),
        )


def test_noble_cannot_be_in_commoner_list():
    queen = get_piece_definition("queen")

    with pytest.raises(ValueError):
        generate_random_army_assignments(
            nobles=[],
            commoners=[queen],
            owner="white",
            rng=random.Random(7),
        )


def test_both_piece_counts_as_starting_noble_only_when_assigned_as_noble():
    wild_stallion = get_piece_definition("wild stallion")

    noble_assignments = generate_random_army_assignments(
        nobles=[wild_stallion],
        commoners=[],
        owner="white",
        rng=random.Random(8),
    )

    commoner_assignments = generate_random_army_assignments(
        nobles=[],
        commoners=[wild_stallion],
        owner="white",
        rng=random.Random(9),
    )

    noble_lineup = get_starting_noble_lineup(noble_assignments)
    commoner_lineup = get_starting_noble_lineup(commoner_assignments)

    assert wild_stallion.id in noble_lineup
    assert wild_stallion.id not in commoner_lineup