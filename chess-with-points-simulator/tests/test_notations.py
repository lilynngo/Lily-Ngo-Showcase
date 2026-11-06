from types import SimpleNamespace

from src.notation import move_to_notation


def make_move(**overrides):
    values = {
        "piece": "knight",
        "from_square": (0, 6),  # g1 in your coordinate system
        "to_square": (2, 5),    # f3
        "captured_piece_id": None,
        "leap_captured_id": None,
        "swap_used": False,
        "swapped_with": None,
        "opponent_control_used": False,
        "controlled_piece": None,
        "promoted_to": None,
        "created_check": False,
        "created_checkmate": False,
        "san_disambiguation": "",
    }

    values.update(overrides)
    return SimpleNamespace(**values)


def test_notation_without_disambiguation():
    move = make_move()

    assert move_to_notation(move) == "Nf3"


def test_notation_with_file_disambiguation():
    move = make_move(
        san_disambiguation="g",
    )

    assert move_to_notation(move) == "Ngf3"


def test_notation_with_rank_disambiguation():
    move = make_move(
        san_disambiguation="1",
    )

    assert move_to_notation(move) == "N1f3"


def test_notation_with_full_square_disambiguation():
    move = make_move(
        san_disambiguation="g1",
    )

    assert move_to_notation(move) == "Ng1f3"


def test_capture_with_disambiguation():
    move = make_move(
        san_disambiguation="g",
        captured_piece_id=4,
    )

    assert move_to_notation(move) == "Ngxf3"