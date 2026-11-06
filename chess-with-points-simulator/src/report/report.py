from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import pandas as pd

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


# ============================================================
# CONFIGURATION
# ============================================================

RESULTS_FOLDER = Path("results")
OUTPUT_FOLDER = Path("generated_reports")

POSITION_CSV = OUTPUT_FOLDER / "position_cost_estimates.csv"
ROLE_CSV = OUTPUT_FOLDER / "role_cost_estimates.csv"
UNIVERSAL_CSV = OUTPUT_FOLDER / "universal_piece_costs.csv"
ERRORS_CSV = OUTPUT_FOLDER / "piece_cost_import_errors.csv"
DASHBOARD_XLSX = OUTPUT_FOLDER / "special_piece_costing_dashboard.xlsx"
VANILLA_CONTROL_WORKBOOK = RESULTS_FOLDER / "Vanilla_vs_Vanilla.xlsx"

BASE_COSTS = {
    "pawn": 10,
    "knight": 30,
    "bishop": 30,
    "rook": 50,
    "queen": 100,
}

# Each tuple is:
#     ("special piece", "vanilla piece replaced")
#
# A workbook may contain one swap or any number of swaps.

STRATEGIES: dict[str, list[tuple[str, str]]] = {
    "Vanilla_arcane_priest_bishop_vs_Vanilla.xlsx": [("arcane priest", "bishop")],
    "Vanilla_arcane_tower_rook_vs_Vanilla.xlsx": [("arcane tower", "rook")],
    "Vanilla_armored_chariot_rook_vs_Vanilla.xlsx": [("armored chariot", "rook")],
    "Vanilla_clergy_rider_knight_vs_Vanilla.xlsx": [("clergy rider", "knight")],
    "Vanilla_corrupted_abbot_bishop_vs_Vanilla.xlsx": [("corrupted abbot", "bishop")],
    "Vanilla_damaged_chariot_rook_vs_Vanilla.xlsx": [("damaged chariot", "rook")],
    "Vanilla_fast_chariot_rook_vs_Vanilla.xlsx": [("fast chariot", "rook")],
    "Vanilla_high_priest_bishop_vs_Vanilla.xlsx": [("high priest", "bishop")],
    "Vanilla_joan_of_arc_queen_vs_Vanilla.xlsx": [("joan of arc", "queen")],
    "Vanilla_lance_rider_knight_vs_Vanilla.xlsx": [("lance rider", "knight")],
    "Vanilla_mule_knight_vs_Vanilla.xlsx": [("mule", "knight")],
    "Vanilla_peasant_pawn_vs_Vanilla.xlsx": [("peasant", "pawn")],
    "Vanilla_pegasus_knight_vs_Vanilla.xlsx": [("pegasus", "knight")],
    "Vanilla_queen_of_air_bishop_vs_Vanilla.xlsx": [("queen of air", "bishop")],
    "Vanilla_queen_of_air_queen_vs_Vanilla.xlsx": [("queen of air", "queen")],
    "Vanilla_queen_of_air_rook_vs_Vanilla.xlsx": [("queen of air", "rook")],
    "Vanilla_queen_of_darkness_bishop_vs_Vanilla.xlsx": [("queen of darkness", "bishop")],
    "Vanilla_queen_of_darkness_queen_vs_Vanilla.xlsx": [("queen of darkness", "queen")],
    "Vanilla_queen_of_darkness_rook_vs_Vanilla.xlsx": [("queen of darkness", "rook")],
    "Vanilla_shield_bearer_pawn_vs_Vanilla.xlsx": [("shield bearer", "pawn")],
    "Vanilla_the_old_queen_queen_vs_Vanilla.xlsx": [("the old queen", "queen")],
    "Vanilla_wild_stallion_knight_vs_Vanilla.xlsx": [("wild stallion", "knight")],
    "Vanilla_wild_stallion_pawn_vs_Vanilla.xlsx": [("wild stallion", "pawn")],
    "Vanilla_adept_pawn_vs_Vanilla.xlsx": [("adept", "pawn")],
}

METRIC_WEIGHTS = {
    "Capture Value": 0.35,
    "Check Pressure": 0.30,
    "Mobility": 0.15,
    "Survival": 0.01,
    "Activity": 0.15,
}

SMOOTHING = {
    "Capture Value": 10.0,
    "Check Pressure": 0.5,
    "Mobility": 0.25,
    "Survival": 0.02,
    "Activity": 1.0,
}

METRIC_COLUMN_ALIASES = {
    "Capture Value": [
        "Median Pieces × Cost Captured",
        "Median Pieces x Cost Captured",
        "Median Pieces X Cost Captured",
    ],
    "Check Pressure": [
        "Median Times Used to Check/Checkmate",
    ],
    "Mobility": [
        "Median Number of Legal Moves",
    ],
    "Survival": [
        "Survival Rate",
    ],
    "Activity": [
        "Median Number of Times Used",
    ],
}

START_POSITION_ALIASES = [
    "Starting Position",
    "starting_position",
    "Start Position",
]

GAMES_COLUMN_ALIASES = [
    "Games",
    "games",
]

# Ratio safeguards.
MIN_METRIC_RATIO = 0.50
MAX_METRIC_RATIO = 3.00

# Blend the same-workbook benchmark with the standard control.
DIRECT_RATIO_WEIGHT = 0.60
BASELINE_RATIO_WEIGHT = 0.40

# Match outcome receives a total weight of 0.30.
# For mixed armies this is divided by the number of declared swaps.
TOTAL_OUTCOME_WEIGHT = 0.30

# Universal price formula:
# weighted mean across all observed contexts
# + POSITION_RISK_FACTOR * standard deviation across those contexts.
POSITION_RISK_FACTOR = 0.25

ROUND_TO = 5


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_piece_name(value: object) -> str:
    name = str(value).strip().lower()
    name = name.replace("_", " ")
    name = name.replace("-", " ")
    name = " ".join(name.split())

    aliases = {
        "wild stallions": "wild stallion",
        "wild stallion knights": "wild stallion",
        "wild stallion knight": "wild stallion",
        "wild stallion pawns": "wild stallion",
        "wild stallion pawn": "wild stallion",
        "arcane priests": "arcane priest",
        "arcane towers": "arcane tower",
        "armored chariots": "armored chariot",
        "corrupted abbots": "corrupted abbot",
        "damaged chariots": "damaged chariot",
        "fast chariots": "fast chariot",
        "high priests": "high priest",
        "lance riders": "lance rider",
        "shield bearers": "shield bearer",
    }

    return aliases.get(name, name)


def normalize_text(value: object) -> str:
    return str(value).strip().lower()


def normalize_square(value: object) -> str:
    square = str(value).strip().lower()
    return square if square and square != "nan" else ""


def mirror_square(square: str) -> str:
    """
    Mirror a white starting square to the corresponding black square.

    Examples:
        a1 -> a8
        c1 -> c8
        a2 -> a7
    """
    square = normalize_square(square)

    if len(square) != 2:
        return ""

    file_name = square[0]
    rank_text = square[1]

    if file_name not in "abcdefgh" or not rank_text.isdigit():
        return ""

    rank = int(rank_text)

    if rank < 1 or rank > 8:
        return ""

    return f"{file_name}{9 - rank}"


# ============================================================
# VALIDATION AND COLUMN LOOKUP
# ============================================================

def find_column(
    dataframe: pd.DataFrame,
    possible_names: list[str],
    workbook_name: str,
    required: bool = True,
) -> str | None:
    for possible_name in possible_names:
        if possible_name in dataframe.columns:
            return possible_name

    if required:
        raise ValueError(
            f"{workbook_name}: none of these columns were found: "
            f"{possible_names}. Available columns: {list(dataframe.columns)}"
        )

    return None


def validate_strategy(
    workbook_name: str,
    swaps: list[tuple[str, str]],
) -> None:
    if not swaps:
        raise ValueError(
            f"{workbook_name}: no special-piece swaps were configured."
        )

    for index, swap in enumerate(swaps, start=1):
        if not isinstance(swap, tuple) or len(swap) != 2:
            raise ValueError(
                f"{workbook_name}: swap #{index} must be a tuple such as "
                f"('queen of air', 'rook'). Received {swap!r}."
            )

        special_piece = normalize_piece_name(swap[0])
        replacement_piece = normalize_piece_name(swap[1])

        if not special_piece:
            raise ValueError(
                f"{workbook_name}: swap #{index} has an empty special-piece name."
            )

        if replacement_piece not in BASE_COSTS:
            raise ValueError(
                f"{workbook_name}: replacement '{replacement_piece}' "
                "does not have a configured base cost."
            )


# ============================================================
# CALCULATION HELPERS
# ============================================================

def calculate_metrics(
    rows: pd.DataFrame,
    metric_columns: dict[str, str],
) -> dict[str, float]:
    metrics = {
        metric: float(rows[column_name].median())
        for metric, column_name in metric_columns.items()
    }

    for metric, value in metrics.items():
        if pd.isna(value):
            raise ValueError(
                f"Metric '{metric}' is missing or contains no numeric data."
            )

    return metrics


def calculate_combined_metric_ratios(
    special_metrics: dict[str, float],
    direct_benchmark_metrics: dict[str, float],
    baseline_metrics: dict[str, float],
) -> tuple[
    dict[str, float],
    dict[str, float],
    dict[str, float],
]:
    """
    Return direct, vanilla-control, and blended metric ratios.
    """
    direct_ratios: dict[str, float] = {}
    baseline_ratios: dict[str, float] = {}
    combined_ratios: dict[str, float] = {}

    for metric in METRIC_WEIGHTS:
        direct_raw = (
            special_metrics[metric] + SMOOTHING[metric]
        ) / (
            direct_benchmark_metrics[metric] + SMOOTHING[metric]
        )

        baseline_raw = (
            special_metrics[metric] + SMOOTHING[metric]
        ) / (
            baseline_metrics[metric] + SMOOTHING[metric]
        )

        direct_ratio = float(
            np.clip(
                direct_raw,
                MIN_METRIC_RATIO,
                MAX_METRIC_RATIO,
            )
        )

        baseline_ratio = float(
            np.clip(
                baseline_raw,
                MIN_METRIC_RATIO,
                MAX_METRIC_RATIO,
            )
        )

        combined_ratio = (
            direct_ratio ** DIRECT_RATIO_WEIGHT
            * baseline_ratio ** BASELINE_RATIO_WEIGHT
        )

        direct_ratios[metric] = direct_ratio
        baseline_ratios[metric] = baseline_ratio
        combined_ratios[metric] = float(
            np.clip(
                combined_ratio,
                MIN_METRIC_RATIO,
                MAX_METRIC_RATIO,
            )
        )

    return direct_ratios, baseline_ratios, combined_ratios


def calculate_performance_multiplier(
    ratios: dict[str, float],
) -> float:
    return math.exp(
        sum(
            METRIC_WEIGHTS[metric] * math.log(ratios[metric])
            for metric in METRIC_WEIGHTS
        )
    )


def calculate_match_results(
    games: pd.DataFrame,
    special_owner: str,
) -> tuple[int, int, int, float]:
    if games.empty:
        raise ValueError("The Games sheet is empty.")

    wins = int(games["Winner"].eq(special_owner).sum())
    draws = int(games["Winner"].eq("draw").sum())
    losses = len(games) - wins - draws

    score_rate = (
        wins + 0.5 * draws
    ) / len(games)

    return wins, losses, draws, score_rate


def calculate_outcome_adjustment(
    score_rate: float,
    number_of_swaps: int,
) -> tuple[float, float]:
    outcome_weight = (
        TOTAL_OUTCOME_WEIGHT
        / max(number_of_swaps, 1)
    )

    outcome_multiplier = (
        1
        + outcome_weight
        * (score_rate - 0.50)
    )

    return outcome_weight, outcome_multiplier


def round_cost(value: float) -> int:
    return int(
        round(value / ROUND_TO)
        * ROUND_TO
    )


def weighted_mean(
    values: pd.Series,
    weights: pd.Series,
) -> float:
    values_array = values.astype(float).to_numpy()
    weights_array = weights.astype(float).to_numpy()

    valid = (
        np.isfinite(values_array)
        & np.isfinite(weights_array)
        & (weights_array > 0)
    )

    if not valid.any():
        return float(np.mean(values_array))

    return float(
        np.average(
            values_array[valid],
            weights=weights_array[valid],
        )
    )


def weighted_population_std(
    values: pd.Series,
    weights: pd.Series,
) -> float:
    values_array = values.astype(float).to_numpy()
    weights_array = weights.astype(float).to_numpy()

    valid = (
        np.isfinite(values_array)
        & np.isfinite(weights_array)
        & (weights_array > 0)
    )

    values_array = values_array[valid]
    weights_array = weights_array[valid]

    if len(values_array) <= 1:
        return 0.0

    mean = np.average(
        values_array,
        weights=weights_array,
    )

    variance = np.average(
        (values_array - mean) ** 2,
        weights=weights_array,
    )

    return float(math.sqrt(variance))


# ============================================================
# VANILLA CONTROL BASELINE
# ============================================================

def load_vanilla_baseline(
    path: Path,
) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(
            f"Vanilla control workbook not found: {path.resolve()}"
        )

    instances = pd.read_excel(
        path,
        sheet_name="Piece Instances",
    )

    if "Owner" not in instances.columns:
        raise ValueError(
            f"{path.name}: Piece Instances is missing Owner."
        )

    if "Piece" not in instances.columns:
        raise ValueError(
            f"{path.name}: Piece Instances is missing Piece."
        )

    instances["Owner"] = (
        instances["Owner"]
        .apply(normalize_text)
    )

    instances["Piece"] = (
        instances["Piece"]
        .apply(normalize_piece_name)
    )

    metric_columns = {
        metric: find_column(
            instances,
            aliases,
            path.name,
        )
        for metric, aliases in METRIC_COLUMN_ALIASES.items()
    }

    start_position_column = find_column(
        instances,
        START_POSITION_ALIASES,
        path.name,
        required=False,
    )

    if start_position_column is not None:
        instances[start_position_column] = (
            instances[start_position_column]
            .apply(normalize_square)
        )

    return {
        "instances": instances,
        "metric_columns": metric_columns,
        "start_position_column": start_position_column,
    }


# ============================================================
# WORKBOOK EVALUATION
# ============================================================

def evaluate_workbook(
    path: Path,
    vanilla_baseline: dict[str, object],
) -> list[dict]:
    if path.name not in STRATEGIES:
        raise ValueError(
            f"{path.name}: no STRATEGIES entry exists."
        )

    strategy = STRATEGIES[path.name]
    validate_strategy(path.name, strategy)

    baseline_instances = vanilla_baseline["instances"]
    baseline_metric_columns = vanilla_baseline["metric_columns"]
    baseline_start_position_column = vanilla_baseline[
        "start_position_column"
    ]

    if not isinstance(baseline_instances, pd.DataFrame):
        raise TypeError("Invalid vanilla baseline data.")

    instances = pd.read_excel(
        path,
        sheet_name="Piece Instances",
    )

    games = pd.read_excel(
        path,
        sheet_name="Games",
    )

    if "Owner" not in instances.columns:
        raise ValueError(
            f"{path.name}: Piece Instances is missing Owner."
        )

    if "Piece" not in instances.columns:
        raise ValueError(
            f"{path.name}: Piece Instances is missing Piece."
        )

    if "Winner" not in games.columns:
        raise ValueError(
            f"{path.name}: Games is missing Winner."
        )

    instances["Owner"] = (
        instances["Owner"]
        .apply(normalize_text)
    )

    instances["Piece"] = (
        instances["Piece"]
        .apply(normalize_piece_name)
    )

    games["Winner"] = (
        games["Winner"]
        .apply(normalize_text)
    )

    metric_columns = {
        metric: find_column(
            instances,
            aliases,
            path.name,
        )
        for metric, aliases in METRIC_COLUMN_ALIASES.items()
    }

    start_position_column = find_column(
        instances,
        START_POSITION_ALIASES,
        path.name,
        required=False,
    )

    games_column = find_column(
        instances,
        GAMES_COLUMN_ALIASES,
        path.name,
        required=False,
    )

    if start_position_column is not None:
        instances[start_position_column] = (
            instances[start_position_column]
            .apply(normalize_square)
        )

    special_owner = "white"
    benchmark_owner = "black"

    wins, losses, draws, score_rate = (
        calculate_match_results(
            games,
            special_owner,
        )
    )

    outcome_weight, outcome_multiplier = (
        calculate_outcome_adjustment(
            score_rate,
            len(strategy),
        )
    )

    strategy_label = " + ".join(
        f"{normalize_piece_name(special).title()} "
        f"for {normalize_piece_name(replacement).title()}"
        for special, replacement in strategy
    )

    output: list[dict] = []

    for swap_number, (
        raw_special,
        raw_replacement,
    ) in enumerate(strategy, start=1):

        special = normalize_piece_name(raw_special)
        replacement = normalize_piece_name(raw_replacement)

        special_rows = instances[
            instances["Owner"].eq(special_owner)
            & instances["Piece"].eq(special)
        ].copy()

        replacement_rows = instances[
            instances["Owner"].eq(benchmark_owner)
            & instances["Piece"].eq(replacement)
        ].copy()

        baseline_replacement_rows = baseline_instances[
            baseline_instances["Owner"].eq(benchmark_owner)
            & baseline_instances["Piece"].eq(replacement)
        ].copy()

        if special_rows.empty:
            available = sorted(
                instances.loc[
                    instances["Owner"].eq(special_owner),
                    "Piece",
                ]
                .dropna()
                .unique()
                .tolist()
            )

            raise ValueError(
                f"{path.name}: '{special}' was not found in the white army. "
                f"Available white pieces: {available}"
            )

        if replacement_rows.empty:
            available = sorted(
                instances.loc[
                    instances["Owner"].eq(benchmark_owner),
                    "Piece",
                ]
                .dropna()
                .unique()
                .tolist()
            )

            raise ValueError(
                f"{path.name}: black benchmark '{replacement}' was not found. "
                f"Available black pieces: {available}"
            )

        if baseline_replacement_rows.empty:
            available = sorted(
                baseline_instances.loc[
                    baseline_instances["Owner"].eq(benchmark_owner),
                    "Piece",
                ]
                .dropna()
                .unique()
                .tolist()
            )

            raise ValueError(
                f"{VANILLA_CONTROL_WORKBOOK.name}: black baseline "
                f"'{replacement}' was not found. Available black pieces: "
                f"{available}"
            )

        # If no position column exists, the entire special-piece group becomes
        # one context and is compared against all corresponding benchmarks.
        if start_position_column is None:
            grouped_special_rows = [
                ("unknown", special_rows)
            ]
        else:
            grouped_special_rows = list(
                special_rows.groupby(
                    start_position_column,
                    dropna=False,
                )
            )

        for position_index, (
            special_start,
            position_rows,
        ) in enumerate(
            grouped_special_rows,
            start=1,
        ):
            special_start = normalize_square(
                special_start
            )

            mirrored_start = mirror_square(
                special_start
            )

            position_match_method = (
                "piece-type fallback"
            )

            benchmark_position_rows = (
                replacement_rows
            )

            if (
                start_position_column is not None
                and mirrored_start
            ):
                exact_benchmark_rows = (
                    replacement_rows[
                        replacement_rows[
                            start_position_column
                        ].eq(mirrored_start)
                    ]
                )

                if not exact_benchmark_rows.empty:
                    benchmark_position_rows = (
                        exact_benchmark_rows
                    )

                    position_match_method = (
                        "mirrored starting square"
                    )

            baseline_match_method = (
                "piece-type baseline fallback"
            )

            baseline_position_rows = (
                baseline_replacement_rows
            )

            if (
                baseline_start_position_column is not None
                and mirrored_start
            ):
                exact_baseline_rows = (
                    baseline_replacement_rows[
                        baseline_replacement_rows[
                            baseline_start_position_column
                        ].eq(mirrored_start)
                    ]
                )

                if not exact_baseline_rows.empty:
                    baseline_position_rows = (
                        exact_baseline_rows
                    )

                    baseline_match_method = (
                        "mirrored vanilla control square"
                    )

            special_metrics = calculate_metrics(
                position_rows,
                metric_columns,
            )

            benchmark_metrics = calculate_metrics(
                benchmark_position_rows,
                metric_columns,
            )

            baseline_metrics = calculate_metrics(
                baseline_position_rows,
                baseline_metric_columns,
            )

            (
                direct_ratios,
                baseline_ratios,
                combined_ratios,
            ) = calculate_combined_metric_ratios(
                special_metrics,
                benchmark_metrics,
                baseline_metrics,
            )

            direct_performance_multiplier = (
                calculate_performance_multiplier(
                    direct_ratios
                )
            )

            baseline_performance_multiplier = (
                calculate_performance_multiplier(
                    baseline_ratios
                )
            )

            performance_multiplier = (
                calculate_performance_multiplier(
                    combined_ratios
                )
            )

            base_cost = BASE_COSTS[
                replacement
            ]

            raw_position_cost = (
                base_cost
                * performance_multiplier
                * outcome_multiplier
            )

            instance_games = len(games)

            if games_column is not None:
                numeric_games = pd.to_numeric(
                    position_rows[games_column],
                    errors="coerce",
                ).dropna()

                if not numeric_games.empty:
                    instance_games = int(
                        max(
                            numeric_games.median(),
                            1,
                        )
                    )

            output.append({
                "workbook": path.name,
                "matchup_strategy":
                    strategy_label,
                "strategy_piece_count":
                    len(strategy),
                "swap_number":
                    swap_number,
                "position_index":
                    position_index,
                "special_piece":
                    special,
                "replacement":
                    replacement,
                "base_cost":
                    base_cost,
                "special_starting_position":
                    special_start,
                "benchmark_starting_position":
                    mirrored_start,
                "position_match_method":
                    position_match_method,
                "vanilla_baseline_workbook":
                    VANILLA_CONTROL_WORKBOOK.name,
                "baseline_match_method":
                    baseline_match_method,
                "direct_ratio_weight":
                    DIRECT_RATIO_WEIGHT,
                "baseline_ratio_weight":
                    BASELINE_RATIO_WEIGHT,
                "position_weight_games":
                    instance_games,
                "games":
                    len(games),
                "wins":
                    wins,
                "losses":
                    losses,
                "draws":
                    draws,
                "score_rate":
                    score_rate,
                "outcome_weight":
                    outcome_weight,
                "outcome_multiplier":
                    outcome_multiplier,
                "direct_performance_multiplier":
                    direct_performance_multiplier,
                "baseline_performance_multiplier":
                    baseline_performance_multiplier,
                "performance_multiplier":
                    performance_multiplier,
                "raw_position_cost":
                    raw_position_cost,
                "recommended_position_cost":
                    round_cost(raw_position_cost),

                "special_capture_value":
                    special_metrics[
                        "Capture Value"
                    ],
                "base_capture_value":
                    benchmark_metrics[
                        "Capture Value"
                    ],
                "baseline_capture_value":
                    baseline_metrics[
                        "Capture Value"
                    ],
                "direct_ratio_capture_value":
                    direct_ratios[
                        "Capture Value"
                    ],
                "baseline_ratio_capture_value":
                    baseline_ratios[
                        "Capture Value"
                    ],
                "combined_ratio_capture_value":
                    combined_ratios[
                        "Capture Value"
                    ],
                "ratio_capture_value":
                    combined_ratios[
                        "Capture Value"
                    ],

                "special_check_pressure":
                    special_metrics[
                        "Check Pressure"
                    ],
                "base_check_pressure":
                    benchmark_metrics[
                        "Check Pressure"
                    ],
                "baseline_check_pressure":
                    baseline_metrics[
                        "Check Pressure"
                    ],
                "direct_ratio_check_pressure":
                    direct_ratios[
                        "Check Pressure"
                    ],
                "baseline_ratio_check_pressure":
                    baseline_ratios[
                        "Check Pressure"
                    ],
                "combined_ratio_check_pressure":
                    combined_ratios[
                        "Check Pressure"
                    ],
                "ratio_check_pressure":
                    combined_ratios[
                        "Check Pressure"
                    ],

                "special_mobility":
                    special_metrics[
                        "Mobility"
                    ],
                "base_mobility":
                    benchmark_metrics[
                        "Mobility"
                    ],
                "baseline_mobility":
                    baseline_metrics[
                        "Mobility"
                    ],
                "direct_ratio_mobility":
                    direct_ratios[
                        "Mobility"
                    ],
                "baseline_ratio_mobility":
                    baseline_ratios[
                        "Mobility"
                    ],
                "combined_ratio_mobility":
                    combined_ratios[
                        "Mobility"
                    ],
                "ratio_mobility":
                    combined_ratios[
                        "Mobility"
                    ],

                "special_survival":
                    special_metrics[
                        "Survival"
                    ],
                "base_survival":
                    benchmark_metrics[
                        "Survival"
                    ],
                "baseline_survival":
                    baseline_metrics[
                        "Survival"
                    ],
                "direct_ratio_survival":
                    direct_ratios[
                        "Survival"
                    ],
                "baseline_ratio_survival":
                    baseline_ratios[
                        "Survival"
                    ],
                "combined_ratio_survival":
                    combined_ratios[
                        "Survival"
                    ],
                "ratio_survival":
                    combined_ratios[
                        "Survival"
                    ],

                "special_activity":
                    special_metrics[
                        "Activity"
                    ],
                "base_activity":
                    benchmark_metrics[
                        "Activity"
                    ],
                "baseline_activity":
                    baseline_metrics[
                        "Activity"
                    ],
                "direct_ratio_activity":
                    direct_ratios[
                        "Activity"
                    ],
                "baseline_ratio_activity":
                    baseline_ratios[
                        "Activity"
                    ],
                "combined_ratio_activity":
                    combined_ratios[
                        "Activity"
                    ],
                "ratio_activity":
                    combined_ratios[
                        "Activity"
                    ],
            })

    return output


# ============================================================
# AGGREGATION
# ============================================================

def create_role_estimates(
    position_report: pd.DataFrame,
) -> pd.DataFrame:
    if position_report.empty:
        return pd.DataFrame()

    role_rows: list[dict] = []

    grouping_columns = [
        "special_piece",
        "replacement",
    ]

    for (
        special_piece,
        replacement,
    ), group in position_report.groupby(
        grouping_columns,
        dropna=False,
    ):
        role_mean = weighted_mean(
            group["raw_position_cost"],
            group["position_weight_games"],
        )

        role_std = weighted_population_std(
            group["raw_position_cost"],
            group["position_weight_games"],
        )

        role_risk_adjusted_cost = (
            role_mean
            + POSITION_RISK_FACTOR
            * role_std
        )

        role_rows.append({
            "special_piece":
                special_piece,
            "replacement":
                replacement,
            "base_cost":
                BASE_COSTS[replacement],
            "workbooks_tested":
                group["workbook"].nunique(),
            "positions_tested":
                len(group),
            "total_position_weight":
                float(
                    group[
                        "position_weight_games"
                    ].sum()
                ),
            "minimum_position_cost":
                float(
                    group[
                        "raw_position_cost"
                    ].min()
                ),
            "maximum_position_cost":
                float(
                    group[
                        "raw_position_cost"
                    ].max()
                ),
            "median_position_cost":
                float(
                    group[
                        "raw_position_cost"
                    ].median()
                ),
            "weighted_mean_role_cost":
                role_mean,
            "position_cost_std":
                role_std,
            "risk_adjusted_role_cost":
                role_risk_adjusted_cost,
            "recommended_role_cost":
                round_cost(
                    role_risk_adjusted_cost
                ),
        })

    return pd.DataFrame(
        role_rows
    ).sort_values(
        [
            "special_piece",
            "replacement",
        ]
    )


def create_universal_estimates(
    position_report: pd.DataFrame,
) -> pd.DataFrame:
    if position_report.empty:
        return pd.DataFrame()

    universal_rows: list[dict] = []

    for special_piece, group in (
        position_report.groupby(
            "special_piece",
            dropna=False,
        )
    ):
        universal_mean = weighted_mean(
            group["raw_position_cost"],
            group["position_weight_games"],
        )

        universal_std = weighted_population_std(
            group["raw_position_cost"],
            group["position_weight_games"],
        )

        universal_risk_adjusted_cost = (
            universal_mean
            + POSITION_RISK_FACTOR
            * universal_std
        )

        replacements = ", ".join(
            sorted(
                group[
                    "replacement"
                ].dropna().unique()
            )
        )

        universal_rows.append({
            "special_piece":
                special_piece,
            "replacement_roles_tested":
                replacements,
            "roles_tested":
                group[
                    "replacement"
                ].nunique(),
            "workbooks_tested":
                group[
                    "workbook"
                ].nunique(),
            "position_contexts_tested":
                len(group),
            "total_position_weight":
                float(
                    group[
                        "position_weight_games"
                    ].sum()
                ),
            "minimum_context_cost":
                float(
                    group[
                        "raw_position_cost"
                    ].min()
                ),
            "maximum_context_cost":
                float(
                    group[
                        "raw_position_cost"
                    ].max()
                ),
            "median_context_cost":
                float(
                    group[
                        "raw_position_cost"
                    ].median()
                ),
            "weighted_mean_cost":
                universal_mean,
            "context_cost_std":
                universal_std,
            "position_risk_factor":
                POSITION_RISK_FACTOR,
            "risk_adjusted_universal_cost":
                universal_risk_adjusted_cost,
            "recommended_universal_cost":
                round_cost(
                    universal_risk_adjusted_cost
                ),
        })

    return pd.DataFrame(
        universal_rows
    ).sort_values(
        "recommended_universal_cost",
        ascending=False,
    )


# ============================================================
# EXCEL DASHBOARD
# ============================================================

def create_dashboard(
    position_report: pd.DataFrame,
    role_report: pd.DataFrame,
    universal_report: pd.DataFrame,
    errors: pd.DataFrame,
    output_path: Path,
) -> None:
    workbook = Workbook()

    dashboard = workbook.active
    dashboard.title = "Dashboard"

    universal_sheet = workbook.create_sheet(
        "Universal Costs"
    )
    role_sheet = workbook.create_sheet(
        "Role Costs"
    )
    position_sheet = workbook.create_sheet(
        "Position Costs"
    )
    methodology_sheet = workbook.create_sheet(
        "Methodology"
    )
    error_sheet = workbook.create_sheet(
        "Errors"
    )

    dark_blue = "25324A"
    medium_blue = "4F6D8A"
    light_blue = "DCE6F1"
    pale_blue = "EEF3F8"
    white = "FFFFFF"
    light_gray = "F8FAFC"

    thin_side = Side(
        style="thin",
        color="D1D5DB",
    )

    title_fill = PatternFill(
        "solid",
        fgColor=dark_blue,
    )
    section_fill = PatternFill(
        "solid",
        fgColor=light_blue,
    )
    header_fill = PatternFill(
        "solid",
        fgColor=medium_blue,
    )
    card_fill = PatternFill(
        "solid",
        fgColor=pale_blue,
    )
    body_fill = PatternFill(
        "solid",
        fgColor=light_gray,
    )

    title_font = Font(
        bold=True,
        color=white,
        size=20,
    )
    section_font = Font(
        bold=True,
        color=dark_blue,
        size=12,
    )
    header_font = Font(
        bold=True,
        color=white,
    )

    centered = Alignment(
        horizontal="center",
        vertical="center",
        wrap_text=True,
    )
    left_wrapped = Alignment(
        horizontal="left",
        vertical="top",
        wrap_text=True,
    )

    def merge_and_write(
        sheet,
        cell_range: str,
        value: object,
        fill=None,
        font=None,
        alignment=None,
    ) -> None:
        sheet.merge_cells(cell_range)
        top_left = sheet[
            cell_range.split(":")[0]
        ]
        top_left.value = value

        for row in sheet[cell_range]:
            for cell in row:
                if fill:
                    cell.fill = fill
                if font:
                    cell.font = font
                if alignment:
                    cell.alignment = alignment

    def style_header(
        sheet,
        row_number: int,
        column_count: int,
    ) -> None:
        for column in range(
            1,
            column_count + 1,
        ):
            cell = sheet.cell(
                row=row_number,
                column=column,
            )
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = centered
            cell.border = Border(
                left=thin_side,
                right=thin_side,
                top=thin_side,
                bottom=thin_side,
            )

    def write_dataframe(
        sheet,
        dataframe: pd.DataFrame,
        start_row: int,
        start_column: int = 1,
        table_name: str | None = None,
    ) -> tuple[int, int]:
        if dataframe.empty:
            sheet.cell(
                row=start_row,
                column=start_column,
                value="No data available.",
            )
            return start_row, start_column

        for column_offset, header in enumerate(
            dataframe.columns,
            start=0,
        ):
            sheet.cell(
                row=start_row,
                column=start_column + column_offset,
                value=header,
            )

        for row_offset, row_values in enumerate(
            dataframe.itertuples(
                index=False,
                name=None,
            ),
            start=1,
        ):
            for column_offset, value in enumerate(
                row_values,
                start=0,
            ):
                if pd.isna(value):
                    value = None

                sheet.cell(
                    row=start_row + row_offset,
                    column=start_column + column_offset,
                    value=value,
                )

        end_row = start_row + len(dataframe)
        end_column = (
            start_column
            + len(dataframe.columns)
            - 1
        )

        for row in sheet.iter_rows(
            min_row=start_row,
            max_row=end_row,
            min_col=start_column,
            max_col=end_column,
        ):
            for cell in row:
                cell.border = Border(
                    left=thin_side,
                    right=thin_side,
                    top=thin_side,
                    bottom=thin_side,
                )
                cell.alignment = Alignment(
                    vertical="center",
                )

        for column in range(
            start_column,
            end_column + 1,
        ):
            cell = sheet.cell(
                row=start_row,
                column=column,
            )
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = centered

        if table_name:
            reference = (
                f"{get_column_letter(start_column)}"
                f"{start_row}:"
                f"{get_column_letter(end_column)}"
                f"{end_row}"
            )

            table = Table(
                displayName=table_name,
                ref=reference,
            )

            table.tableStyleInfo = (
                TableStyleInfo(
                    name="TableStyleMedium2",
                    showFirstColumn=False,
                    showLastColumn=False,
                    showRowStripes=True,
                    showColumnStripes=False,
                )
            )

            sheet.add_table(table)

        return end_row, end_column

    # --------------------------------------------------------
    # Dashboard
    # --------------------------------------------------------

    merge_and_write(
        dashboard,
        "A1:N2",
        "Position-Aware Special Piece Costing",
        fill=title_fill,
        font=title_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    merge_and_write(
        dashboard,
        "A3:N3",
        (
            "Position estimates are aggregated into replacement-role costs "
            "and then into one risk-adjusted universal piece cost."
        ),
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    distinct_pieces = (
        universal_report[
            "special_piece"
        ].nunique()
        if not universal_report.empty
        else 0
    )

    role_count = (
        len(role_report)
    )

    context_count = (
        len(position_report)
    )

    total_games = (
        position_report.groupby(
            "workbook"
        )["games"].first().sum()
        if not position_report.empty
        else 0
    )

    cards = [
        (
            "A5:C5",
            "A6:C8",
            "Special pieces",
            distinct_pieces,
        ),
        (
            "D5:F5",
            "D6:F8",
            "Replacement roles",
            role_count,
        ),
        (
            "G5:I5",
            "G6:I8",
            "Position contexts",
            context_count,
        ),
        (
            "J5:L5",
            "J6:L8",
            "Unique simulations",
            int(total_games),
        ),
    ]

    for (
        label_range,
        value_range,
        label,
        value,
    ) in cards:
        merge_and_write(
            dashboard,
            label_range,
            label,
            fill=card_fill,
            font=Font(
                bold=True,
                color="4B5563",
            ),
            alignment=centered,
        )

        merge_and_write(
            dashboard,
            value_range,
            value,
            fill=PatternFill(
                "solid",
                fgColor=white,
            ),
            font=Font(
                bold=True,
                color="1F2937",
                size=18,
            ),
            alignment=centered,
        )

    if not universal_report.empty:
        top_piece = universal_report.iloc[0]

        merge_and_write(
            dashboard,
            "M5:N5",
            "Highest universal cost",
            fill=card_fill,
            font=Font(
                bold=True,
                color="4B5563",
            ),
            alignment=centered,
        )

        merge_and_write(
            dashboard,
            "M6:N8",
            (
                f"{str(top_piece['special_piece']).title()}\n"
                f"{int(top_piece['recommended_universal_cost'])} points"
            ),
            fill=PatternFill(
                "solid",
                fgColor=white,
            ),
            font=Font(
                bold=True,
                color="1F2937",
                size=13,
            ),
            alignment=centered,
        )

    dashboard_headers = [
        "Rank",
        "Special Piece",
        "Roles Tested",
        "Weighted Mean",
        "Context Std",
        "Risk-Adjusted Cost",
        "Recommended Cost",
    ]

    for column, header in enumerate(
        dashboard_headers,
        start=1,
    ):
        dashboard.cell(
            row=11,
            column=column,
            value=header,
        )

    style_header(
        dashboard,
        11,
        len(dashboard_headers),
    )

    for row_number, row in enumerate(
        universal_report.itertuples(
            index=False
        ),
        start=12,
    ):
        values = [
            row_number - 11,
            str(row.special_piece).title(),
            row.replacement_roles_tested,
            row.weighted_mean_cost,
            row.context_cost_std,
            row.risk_adjusted_universal_cost,
            row.recommended_universal_cost,
        ]

        for column, value in enumerate(
            values,
            start=1,
        ):
            dashboard.cell(
                row=row_number,
                column=column,
                value=value,
            )

    dashboard_end_row = (
        11 + len(universal_report)
    )

    if not universal_report.empty:
        dashboard.conditional_formatting.add(
            f"G12:G{dashboard_end_row}",
            DataBarRule(
                start_type="min",
                end_type="max",
                color=medium_blue,
                showValue=True,
            ),
        )

        chart_data_start_column = 9

        chart_headers = [
            "Special Piece",
            "Weighted Mean",
            "Risk-Adjusted Cost",
        ]

        for column_offset, header in enumerate(
            chart_headers,
            start=0,
        ):
            dashboard.cell(
                row=11,
                column=(
                    chart_data_start_column
                    + column_offset
                ),
                value=header,
            )

        for row_number, row in enumerate(
            universal_report.itertuples(
                index=False
            ),
            start=12,
        ):
            dashboard.cell(
                row=row_number,
                column=9,
                value=str(
                    row.special_piece
                ).title(),
            )

            dashboard.cell(
                row=row_number,
                column=10,
                value=row.weighted_mean_cost,
            )

            dashboard.cell(
                row=row_number,
                column=11,
                value=row.risk_adjusted_universal_cost,
            )

        chart = BarChart()
        chart.type = "bar"
        chart.style = 10
        chart.title = (
            "Universal Cost: Mean vs Position-Risk Adjustment"
        )
        chart.y_axis.title = "Special Piece"
        chart.x_axis.title = "Cost"
        chart.height = 12
        chart.width = 20
        chart.legend.position = "b"

        data = Reference(
            dashboard,
            min_col=10,
            max_col=11,
            min_row=11,
            max_row=dashboard_end_row,
        )

        categories = Reference(
            dashboard,
            min_col=9,
            min_row=12,
            max_row=dashboard_end_row,
        )

        chart.add_data(
            data,
            titles_from_data=True,
        )

        chart.set_categories(
            categories
        )

        dashboard.add_chart(
            chart,
            "I30",
        )

    merge_and_write(
        dashboard,
        "A30:G30",
        "Interpretation",
        fill=section_fill,
        font=section_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    merge_and_write(
        dashboard,
        "A31:G40",
        (
            "• Position Cost: one special-piece starting square compared with "
            "the mirrored black vanilla slot when available.\n"
            "• Role Cost: all observations where the special piece replaces "
            "the same vanilla piece.\n"
            "• Universal Cost: all observed roles and positions for the same "
            "special piece.\n"
            "• Final universal estimate = game-weighted mean + "
            f"{POSITION_RISK_FACTOR:.0%} of context standard deviation.\n"
            "• The standard-deviation adjustment prices the flexibility and "
            "risk created by stronger placements without always charging the "
            "full maximum observed cost."
        ),
        fill=body_fill,
        alignment=left_wrapped,
    )

    dashboard.freeze_panes = "A4"

    dashboard_widths = {
        "A": 9,
        "B": 24,
        "C": 28,
        "D": 15,
        "E": 13,
        "F": 18,
        "G": 18,
        "H": 3,
        "I": 26,
        "J": 16,
        "K": 18,
        "L": 3,
        "M": 22,
        "N": 16,
    }

    for column, width in dashboard_widths.items():
        dashboard.column_dimensions[
            column
        ].width = width

    # --------------------------------------------------------
    # Data sheets
    # --------------------------------------------------------

    merge_and_write(
        universal_sheet,
        "A1:N2",
        "Universal Piece Costs",
        fill=title_fill,
        font=title_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    write_dataframe(
        universal_sheet,
        universal_report,
        start_row=4,
        table_name="UniversalCostsTable",
    )

    universal_sheet.freeze_panes = "A5"

    merge_and_write(
        role_sheet,
        "A1:M2",
        "Replacement-Role Costs",
        fill=title_fill,
        font=title_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    write_dataframe(
        role_sheet,
        role_report,
        start_row=4,
        table_name="RoleCostsTable",
    )

    role_sheet.freeze_panes = "A5"

    merge_and_write(
        position_sheet,
        "A1:AD2",
        "Position-Specific Cost Estimates",
        fill=title_fill,
        font=title_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    write_dataframe(
        position_sheet,
        position_report,
        start_row=4,
        table_name="PositionCostsTable",
    )

    position_sheet.freeze_panes = "A5"

    for sheet in [
        universal_sheet,
        role_sheet,
        position_sheet,
    ]:
        for column in range(
            1,
            sheet.max_column + 1,
        ):
            header = sheet.cell(
                row=4,
                column=column,
            ).value

            if header in {
                "workbook",
                "matchup_strategy",
            }:
                width = 48
            elif header in {
                "special_piece",
                "replacement_roles_tested",
            }:
                width = 25
            elif header in {
                "position_match_method",
            }:
                width = 24
            else:
                width = 18

            sheet.column_dimensions[
                get_column_letter(column)
            ].width = width

    # --------------------------------------------------------
    # Methodology
    # --------------------------------------------------------

    merge_and_write(
        methodology_sheet,
        "A1:H2",
        "Formula and Modeling Considerations",
        fill=title_fill,
        font=title_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    merge_and_write(
        methodology_sheet,
        "A4:H4",
        "Layer 1 - Position-Specific Cost",
        fill=section_fill,
        font=section_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    merge_and_write(
        methodology_sheet,
        "A5:H12",
        (
            "Metric Ratio = clip("
            "(Special Metric + Smoothing) / "
            "(Mirrored Benchmark Metric + Smoothing), "
            f"{MIN_METRIC_RATIO}, {MAX_METRIC_RATIO})\n\n"
            "Performance Multiplier = "
            "exp(sum(Weight × ln(Metric Ratio)))\n\n"
            "Outcome Weight = "
            f"{TOTAL_OUTCOME_WEIGHT} / Number of Declared Swaps\n\n"
            "Outcome Multiplier = "
            "1 + Outcome Weight × (Score Rate - 0.50)\n\n"
            "Position Cost = Replacement Base Cost × "
            "Performance Multiplier × Outcome Multiplier"
        ),
        fill=body_fill,
        alignment=left_wrapped,
    )

    merge_and_write(
        methodology_sheet,
        "A14:H14",
        "Layer 2 - Replacement-Role Cost",
        fill=section_fill,
        font=section_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    merge_and_write(
        methodology_sheet,
        "A15:H19",
        (
            "Role Mean = game-weighted mean of all position costs where "
            "the special piece replaces the same vanilla piece.\n\n"
            "Risk-Adjusted Role Cost = Role Mean + "
            f"{POSITION_RISK_FACTOR} × Position Cost Standard Deviation"
        ),
        fill=body_fill,
        alignment=left_wrapped,
    )

    merge_and_write(
        methodology_sheet,
        "A21:H21",
        "Layer 3 - Universal Piece Cost",
        fill=section_fill,
        font=section_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    merge_and_write(
        methodology_sheet,
        "A22:H27",
        (
            "Universal Mean = game-weighted mean of every observed position "
            "and replacement-role cost for the special piece.\n\n"
            "Universal Cost = Universal Mean + "
            f"{POSITION_RISK_FACTOR} × Context Cost Standard Deviation\n\n"
            f"Recommended Cost = Universal Cost rounded to the nearest "
            f"{ROUND_TO} points."
        ),
        fill=body_fill,
        alignment=left_wrapped,
    )

    merge_and_write(
        methodology_sheet,
        "A29:H29",
        "Important Considerations",
        fill=section_fill,
        font=section_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    merge_and_write(
        methodology_sheet,
        "A30:H39",
        (
            "• Mirrored starting-square comparison is preferred. When no "
            "matching benchmark slot exists, the model falls back to all "
            "black instances of the replacement piece and records that fact.\n"
            "• Mixed-special armies can contain synergy or interference. "
            "Their outcome adjustment is divided across declared swaps, but "
            "single-special tests remain the cleanest source of independent cost.\n"
            "• A universal price is appropriate only when players may deploy "
            "the piece in multiple legal slots. If slot-specific pricing is "
            "acceptable, use the role-cost table instead.\n"
            "• Large standard deviations indicate that position or army "
            "composition strongly changes the piece's value. Such pieces may "
            "need placement restrictions, a surcharge, or additional testing."
        ),
        fill=body_fill,
        alignment=left_wrapped,
    )

    methodology_sheet.column_dimensions[
        "A"
    ].width = 22

    for column in range(2, 9):
        methodology_sheet.column_dimensions[
            get_column_letter(column)
        ].width = 17

    # --------------------------------------------------------
    # Errors
    # --------------------------------------------------------

    merge_and_write(
        error_sheet,
        "A1:B2",
        "Import and Validation Errors",
        fill=title_fill,
        font=title_font,
        alignment=Alignment(
            horizontal="left",
            vertical="center",
        ),
    )

    write_dataframe(
        error_sheet,
        errors,
        start_row=4,
        table_name=(
            "ErrorsTable"
            if not errors.empty
            else None
        ),
    )

    error_sheet.column_dimensions[
        "A"
    ].width = 48

    error_sheet.column_dimensions[
        "B"
    ].width = 90

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    workbook.save(
        output_path
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    position_rows: list[dict] = []
    error_rows: list[dict] = []

    vanilla_baseline = load_vanilla_baseline(
        VANILLA_CONTROL_WORKBOOK
    )

    print(
        f"Loaded vanilla control: {VANILLA_CONTROL_WORKBOOK.name}"
    )

    for workbook_name in STRATEGIES:
        workbook_path = (
            RESULTS_FOLDER
            / workbook_name
        )

        if not workbook_path.exists():
            error_rows.append({
                "workbook":
                    workbook_name,
                "error":
                    "Configured in STRATEGIES but the file was not found.",
            })
            continue

        try:
            print(
                f"Processing: {workbook_name}"
            )

            position_rows.extend(
                evaluate_workbook(
                    workbook_path,
                    vanilla_baseline,
                )
            )

        except Exception as error:
            print(
                f"ERROR processing {workbook_name}: {error}"
            )

            error_rows.append({
                "workbook":
                    workbook_name,
                "error":
                    str(error),
            })

    position_report = pd.DataFrame(
        position_rows
    )

    errors = pd.DataFrame(
        error_rows,
        columns=[
            "workbook",
            "error",
        ],
    )

    role_report = create_role_estimates(
        position_report
    )

    universal_report = (
        create_universal_estimates(
            position_report
        )
    )

    position_report.to_csv(
        POSITION_CSV,
        index=False,
    )

    role_report.to_csv(
        ROLE_CSV,
        index=False,
    )

    universal_report.to_csv(
        UNIVERSAL_CSV,
        index=False,
    )

    errors.to_csv(
        ERRORS_CSV,
        index=False,
    )

    if position_report.empty:
        print(
            "No valid position estimates were generated."
        )
        return

    create_dashboard(
        position_report=position_report,
        role_report=role_report,
        universal_report=universal_report,
        errors=errors,
        output_path=DASHBOARD_XLSX,
    )

    print()
    print(
        f"Position estimates: {POSITION_CSV.resolve()}"
    )
    print(
        f"Role estimates: {ROLE_CSV.resolve()}"
    )
    print(
        f"Universal costs: {UNIVERSAL_CSV.resolve()}"
    )
    print(
        f"Dashboard: {DASHBOARD_XLSX.resolve()}"
    )

    if not errors.empty:
        print(
            f"Errors: {ERRORS_CSV.resolve()}"
        )


if __name__ == "__main__":
    main()
