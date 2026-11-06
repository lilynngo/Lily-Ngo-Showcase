import pytest

from src.army import generate_standard_army
from src.balance import (
    PieceStats,
    build_balance_report,
    build_piece_instance_match_report,
    build_piece_match_report,
    calculate_average_efficiency,
    collect_piece_stats,
    round_cost,
    suggest_new_costs,
)
from src.piece_loader import load_piece_definitions_from_json
from src.simulation import simulate_matchup


@pytest.fixture(scope="module")
def standard_matchup():
    """
    Run one small deterministic matchup and reuse it throughout this module.

    Reusing the records keeps the balance tests fast while still exercising
    the real simulation and reporting pipeline.
    """
    pieces = load_piece_definitions_from_json(
        "data/standard_pieces.json"
    )

    white_army = generate_standard_army(pieces)
    black_army = generate_standard_army(pieces)

    records = simulate_matchup(
        white_army=white_army,
        black_army=black_army,
        games_per_matchup=2,
        max_turns=20,
        seed=123,
    )

    return pieces, records


def test_piece_efficiency_calculates_average_value_over_cost():
    stat = PieceStats(
        piece_id=2,
        name="knight",
        current_cost=30,
        games_seen=1,
        total_value=60,
    )

    assert stat.efficiency() == 2.0


def test_king_efficiency_is_none_when_cost_is_zero():
    stat = PieceStats(
        piece_id=6,
        name="king",
        current_cost=0,
        games_seen=1,
        total_value=50,
    )

    assert stat.efficiency() is None


def test_average_efficiency_excludes_zero_cost_pieces():
    stats = {
        1: PieceStats(
            1,
            "pawn",
            10,
            games_seen=1,
            total_value=20,
        ),
        6: PieceStats(
            6,
            "king",
            0,
            games_seen=1,
            total_value=999,
        ),
    }

    assert calculate_average_efficiency(stats) == 2.0


def test_round_cost_rounds_to_nearest_5():
    assert round_cost(12) == 10
    assert round_cost(13) == 15
    assert round_cost(27) == 25
    assert round_cost(28) == 30


def test_cost_never_below_minimum():
    assert round_cost(1) == 10


def test_suggest_new_costs_keeps_king_at_zero():
    stats = {
        1: PieceStats(
            1,
            "pawn",
            10,
            games_seen=1,
            total_value=20,
        ),
        6: PieceStats(
            6,
            "king",
            0,
            games_seen=1,
            total_value=999,
        ),
    }

    new_costs = suggest_new_costs(stats)

    assert new_costs[6] == 0


def test_collect_piece_stats_from_matchup_records(
    standard_matchup,
):
    pieces, records = standard_matchup

    stats = collect_piece_stats(records, pieces)

    assert len(stats) == len(pieces)

    for piece in pieces.values():
        assert piece.id in stats


def test_balance_report_includes_every_piece(
    standard_matchup,
):
    pieces, records = standard_matchup

    stats = collect_piece_stats(records, pieces)
    new_costs = suggest_new_costs(stats)
    report = build_balance_report(
        stats,
        new_costs,
    )

    assert len(report) == len(pieces)

    names = {
        row["name"]
        for row in report
    }

    assert "pawn" in names
    assert "king" in names


def test_piece_match_report_returns_empty_list_for_no_records():
    assert build_piece_match_report([], {}) == []


def test_piece_instance_report_returns_empty_list_for_no_records():
    assert build_piece_instance_match_report([]) == []


def test_piece_match_report_has_one_row_per_piece_type(
    standard_matchup,
):
    pieces, records = standard_matchup

    report = build_piece_match_report(
        records,
        pieces,
    )

    piece_names = [
        row["piece"]
        for row in report
    ]

    # All pawn instances must be combined into one pawn row.
    assert piece_names.count("pawn") == 1

    # The standard army should include these six definitions.
    assert {
        "pawn",
        "knight",
        "bishop",
        "rook",
        "queen",
        "king",
    }.issubset(set(piece_names))


def test_piece_match_report_contains_required_columns(
    standard_matchup,
):
    pieces, records = standard_matchup

    report = build_piece_match_report(
        records,
        pieces,
    )

    required_columns = {
        "piece_id",
        "piece",
        "piece_cost",
        "games",
        "moves_per_game",
        "number_of_wins_white",
        "number_of_wins_black",
        "number_of_draws",
        "median_pieces_captured",
        "median_piece_cost_captured",
        "median_number_of_shields_used",
        "median_number_of_swaps",
        "median_number_of_opponent_controlled",
        "median_number_of_times_used",
        "median_number_of_times_used_to_check_or_checkmate",
        "median_number_of_legal_moves",
    }

    assert report

    for row in report:
        assert required_columns.issubset(row.keys())


def test_piece_match_report_game_results_match_records(
    standard_matchup,
):
    pieces, records = standard_matchup

    report = build_piece_match_report(
        records,
        pieces,
    )

    expected_white_wins = sum(
        record.winner == "white"
        for record in records
    )
    expected_black_wins = sum(
        record.winner == "black"
        for record in records
    )
    expected_draws = sum(
        record.winner is None
        for record in records
    )

    for row in report:
        assert row["games"] == len(records)
        assert (
            row["number_of_wins_white"]
            == expected_white_wins
        )
        assert (
            row["number_of_wins_black"]
            == expected_black_wins
        )
        assert (
            row["number_of_draws"]
            == expected_draws
        )


def test_piece_instance_report_contains_all_32_starting_pieces(
    standard_matchup,
):
    _, records = standard_matchup

    report = build_piece_instance_match_report(
        records
    )

    # A standard chess army has 16 pieces per side.
    assert len(report) == 32

    instance_ids = [
        row["piece_instance_id"]
        for row in report
    ]

    assert len(instance_ids) == len(
        set(instance_ids)
    )


def test_piece_instance_report_tracks_all_pawns_separately(
    standard_matchup,
):
    _, records = standard_matchup

    report = build_piece_instance_match_report(
        records
    )

    pawn_rows = [
        row
        for row in report
        if row["piece"] == "pawn"
    ]

    white_pawns = [
        row
        for row in pawn_rows
        if row["owner"] == "white"
    ]

    black_pawns = [
        row
        for row in pawn_rows
        if row["owner"] == "black"
    ]

    assert len(pawn_rows) == 16
    assert len(white_pawns) == 8
    assert len(black_pawns) == 8

    assert {
        row["piece_instance_id"]
        for row in white_pawns
    } == {
        f"white_pawn_{number}"
        for number in range(1, 9)
    }

    assert {
        row["piece_instance_id"]
        for row in black_pawns
    } == {
        f"black_pawn_{number}"
        for number in range(1, 9)
    }


def test_piece_instance_report_contains_required_columns(
    standard_matchup,
):
    _, records = standard_matchup

    report = build_piece_instance_match_report(
        records
    )

    required_columns = {
        "piece_instance_id",
        "owner",
        "piece",
        "piece_id",
        "piece_cost",
        "starting_position",
        "games",
        "moves_per_game",
        "number_of_wins_white",
        "number_of_wins_black",
        "number_of_draws",
        "median_pieces_captured",
        "median_piece_cost_captured",
        "median_number_of_shields_used",
        "median_number_of_swaps",
        "median_number_of_opponent_controlled",
        "median_number_of_times_used",
        "median_number_of_times_used_to_check_or_checkmate",
        "median_number_of_legal_moves",
        "survival_rate",
    }

    assert report

    for row in report:
        assert required_columns.issubset(row.keys())


def test_piece_instance_starting_positions_are_valid(
    standard_matchup,
):
    _, records = standard_matchup

    report = build_piece_instance_match_report(
        records
    )

    for row in report:
        starting_position = row["starting_position"]

        assert isinstance(starting_position, tuple)
        assert len(starting_position) == 2

        board_row, board_column = starting_position

        assert 0 <= board_row <= 7
        assert 0 <= board_column <= 7


def test_piece_instance_survival_rate_is_between_zero_and_one(
    standard_matchup,
):
    _, records = standard_matchup

    report = build_piece_instance_match_report(
        records
    )

    for row in report:
        assert 0.0 <= row["survival_rate"] <= 1.0


def test_aggregate_moves_equal_sum_of_instance_moves(
    standard_matchup,
):
    pieces, records = standard_matchup

    piece_report = build_piece_match_report(
        records,
        pieces,
    )

    instance_report = (
        build_piece_instance_match_report(records)
    )

    aggregate_moves = {
        row["piece"]: row["moves_per_game"]
        for row in piece_report
    }

    instance_moves_by_piece = {}

    for row in instance_report:
        piece_name = row["piece"]

        instance_moves_by_piece[piece_name] = (
            instance_moves_by_piece.get(
                piece_name,
                0.0,
            )
            + row["moves_per_game"]
        )

    for piece_name, moves_per_game in aggregate_moves.items():
        assert instance_moves_by_piece[piece_name] == pytest.approx(
            moves_per_game
        )