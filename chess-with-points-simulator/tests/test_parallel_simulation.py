from src.army import generate_standard_army
from src.game_record import GameRecord
from src.piece_loader import load_piece_definitions_from_json
from src.simulation import simulate_matchup_parallel, summarize_matchup


def test_parallel_matchup_runs_requested_number_of_games():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    white_army = generate_standard_army(pieces)
    black_army = generate_standard_army(pieces)

    records = simulate_matchup_parallel(
        white_army=white_army,
        black_army=black_army,
        games_per_matchup=4,
        max_turns=20,
        seed=123,
        max_workers=2,
    )

    assert len(records) == 4

    for record in records:
        assert isinstance(record, GameRecord)
        assert record.reason in {"checkmate", "no legal moves", "move limit"}


def test_parallel_matchup_summary_counts_all_games():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    white_army = generate_standard_army(pieces)
    black_army = generate_standard_army(pieces)

    records = simulate_matchup_parallel(
        white_army=white_army,
        black_army=black_army,
        games_per_matchup=4,
        max_turns=20,
        seed=123,
        max_workers=2,
    )

    summary = summarize_matchup(records)

    assert summary["games"] == 4
    assert (
        summary["white_wins"]
        + summary["black_wins"]
        + summary["draws"]
    ) == 4