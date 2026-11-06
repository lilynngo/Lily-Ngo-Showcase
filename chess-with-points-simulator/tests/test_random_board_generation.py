from src.simulation import create_random_board_from_lineups
from src.moves import is_white_square, is_black_square
from tests.helpers import get_piece_definition


def test_create_random_board_from_lineups_places_all_pieces():
    king = get_piece_definition("king")
    queen = get_piece_definition("queen")
    pawn = get_piece_definition("pawn")

    board, starting_noble_lineup = create_random_board_from_lineups(
        white_nobles=[king, queen],
        white_commoners=[pawn],
        black_nobles=[king, queen],
        black_commoners=[pawn],
        seed=1,
    )

    assert len(board.squares) == 6

    assert starting_noble_lineup["white"] == [king.id, queen.id] or set(starting_noble_lineup["white"]) == {king.id, queen.id}
    assert starting_noble_lineup["black"] == [king.id, queen.id] or set(starting_noble_lineup["black"]) == {king.id, queen.id}


def test_create_random_board_from_lineups_respects_queen_square_rules():
    king = get_piece_definition("king")
    queen_of_air = get_piece_definition("queen of air")
    queen_of_darkness = get_piece_definition("queen of darkness")
    pawn = get_piece_definition("pawn")

    board, starting_noble_lineup = create_random_board_from_lineups(
        white_nobles=[king, queen_of_air, queen_of_darkness],
        white_commoners=[pawn],
        black_nobles=[king, queen_of_air, queen_of_darkness],
        black_commoners=[pawn],
        seed=2,
    )

    for piece in board.squares.values():
        if piece.name == "queen of air":
            assert is_white_square(piece.position) is True

        if piece.name == "queen of darkness":
            assert is_black_square(piece.position) is True