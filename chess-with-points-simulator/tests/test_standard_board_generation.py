import pytest

from src.simulation import create_board_from_armies
from src.board import Board
from src.army import generate_standard_army
from src.piece_loader import load_piece_definitions_from_json

def test_print_standard_board_owners(standard_board: Board):
    for row in range(8):
        values = []

        for col in range(8):
            piece = standard_board.get_piece_at((row, col))

            if piece is None:
                values.append("empty")
            else:
                values.append(
                    f"{piece.owner}_{piece.definition.name}"
                )

        print(row, values)

@pytest.fixture
def standard_board() -> Board:
    piece_definitions = load_piece_definitions_from_json("data/standard_pieces.json")

    white_army = generate_standard_army(piece_definitions)
    black_army = generate_standard_army(piece_definitions)

    board = create_board_from_armies(white_army, black_army)

    return board


def assert_piece(
    board: Board,
    square: tuple[int, int],
    expected_owner: str,
    expected_name: str,
) -> None:
    piece = board.get_piece_at(square)

    assert piece is not None, f"Expected a piece at {square}"
    assert piece.owner == expected_owner
    assert piece.definition.name == expected_name
    assert piece.position == square
    assert piece.is_captured is False


def test_standard_board_has_32_pieces(standard_board: Board):
    pieces = []

    for row in range(8):
        for col in range(8):
            piece = standard_board.get_piece_at((row, col))

            if piece is not None:
                pieces.append(piece)

    assert len(pieces) == 32


def test_standard_white_back_rank(standard_board: Board):
    expected = [
        "rook",
        "knight",
        "bishop",
        "queen",
        "king",
        "bishop",
        "knight",
        "rook",
    ]

    for col, piece_name in enumerate(expected):
        assert_piece(
            standard_board,
            square=(0, col),
            expected_owner="white",
            expected_name=piece_name,
        )


def test_standard_black_back_rank(standard_board: Board):
    expected = [
        "rook",
        "knight",
        "bishop",
        "queen",
        "king",
        "bishop",
        "knight",
        "rook",
    ]

    for col, piece_name in enumerate(expected):
        assert_piece(
            standard_board,
            square=(7, col),
            expected_owner="black",
            expected_name=piece_name,
        )

def test_standard_white_pawns(standard_board: Board):
    for col in range(8):
        assert_piece(
            standard_board,
            square=(1, col),
            expected_owner="white",
            expected_name="pawn",
        )


def test_standard_black_pawns(standard_board: Board):
    for col in range(8):
        assert_piece(
            standard_board,
            square=(6, col),
            expected_owner="black",
            expected_name="pawn",
        )


def test_middle_of_standard_board_is_empty(standard_board: Board):
    for row in range(2, 6):
        for col in range(8):
            assert standard_board.get_piece_at((row, col)) is None

def test_standard_kings_and_queens_are_correct(
    standard_board: Board,
):
    assert_piece(standard_board, (0, 3), "white", "queen")
    assert_piece(standard_board, (0, 4), "white", "king")

    assert_piece(standard_board, (7, 3), "black", "queen")
    assert_piece(standard_board, (7, 4), "black", "king")

def test_standard_board_has_one_king_per_owner(standard_board: Board):
    kings = {
        "white": [],
        "black": [],
    }

    for row in range(8):
        for col in range(8):
            piece = standard_board.get_piece_at((row, col))

            if piece is None:
                continue

            if piece.definition.name == "king":
                kings[piece.owner].append(piece)

    assert len(kings["white"]) == 1
    assert len(kings["black"]) == 1


def test_all_piece_positions_match_board_squares(standard_board: Board):
    for row in range(8):
        for col in range(8):
            square = (row, col)
            piece = standard_board.get_piece_at(square)

            if piece is not None:
                assert piece.position == square


def test_all_piece_instance_ids_are_unique(standard_board: Board):
    instance_ids = []

    for row in range(8):
        for col in range(8):
            piece = standard_board.get_piece_at((row, col))

            if piece is not None:
                instance_ids.append(piece.instance_id)

    assert len(instance_ids) == len(set(instance_ids))