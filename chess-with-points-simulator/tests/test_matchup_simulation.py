from src.army import generate_standard_army
from src.game_record import GameRecord
from src.piece_loader import load_piece_definitions_from_json
from src.simulation import (
    create_board_from_armies,
    simulate_game_with_armies,
    simulate_matchup,
    summarize_matchup,
)


def test_create_board_from_armies_has_32_pieces():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    white_army = generate_standard_army(pieces)
    black_army = generate_standard_army(pieces)

    board = create_board_from_armies(white_army, black_army)

    assert len(board.squares) == 32


def test_create_board_from_armies_starts_with_white():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    white_army = generate_standard_army(pieces)
    black_army = generate_standard_army(pieces)

    board = create_board_from_armies(white_army, black_army)

    assert board.current_player == "white"


def test_simulate_game_with_armies_returns_game_record():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    white_army = generate_standard_army(pieces)
    black_army = generate_standard_army(pieces)

    record = simulate_game_with_armies(
        white_army=white_army,
        black_army=black_army,
        max_turns=20,
        seed=123,
    )

    assert isinstance(record, GameRecord)
    assert record.reason in {"checkmate", "no legal moves", "move limit"}
    assert record.total_moves <= 20


def test_simulate_matchup_runs_10_games():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    white_army = generate_standard_army(pieces)
    black_army = generate_standard_army(pieces)

    records = simulate_matchup(
        white_army=white_army,
        black_army=black_army,
        games_per_matchup=10,
        max_turns=20,
        seed=123,
    )

    assert len(records) == 10

    for record in records:
        assert isinstance(record, GameRecord)
        assert record.reason in {"checkmate", "no legal moves", "move limit"}


def test_matchup_summary_counts_10_games():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    white_army = generate_standard_army(pieces)
    black_army = generate_standard_army(pieces)

    records = simulate_matchup(
        white_army=white_army,
        black_army=black_army,
        games_per_matchup=10,
        max_turns=20,
        seed=123,
    )

    summary = summarize_matchup(records)

    assert summary["games"] == 10
    assert (
        summary["white_wins"]
        + summary["black_wins"]
        + summary["draws"]
    ) == 10