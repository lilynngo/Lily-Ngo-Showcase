"""Estimate fair costs for custom chess pieces from simulation workbooks.

The estimator uses every game outcome and the actual starting armies stored in
"Piece Instances". It fits a ridge-regularized Bradley-Terry/logistic model:

    P(white wins) = logistic(white advantage + sum(piece strength differences))

Draws are treated as half a win for each side. Learned strength differences are
converted to points by calibrating them against the known costs of vanilla
pieces. A special piece's recommended cost is:

    replacement cost + learned strength premium over the replacement piece

Example:
    python cost_special_pieces.py --results-dir results --output piece_costs.xlsx

Dependencies:
    pip install pandas numpy openpyxl xlsxwriter
"""

from __future__ import annotations

import argparse
import json
import math
import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd


# Costs are scaled by 10, as used by the simulation project.
BASE_COSTS: dict[str, float] = {
    "pawn": 10.0,
    "knight": 30.0,
    "bishop": 30.0,
    "rook": 50.0,
    "queen": 100.0,
    # King is required and not normally purchased, so it is not a cost anchor.
}

# A special piece can have more than one legal replacement context.
REPLACEMENTS: dict[str, tuple[str, ...]] = {
    "arcane priest": ("bishop",),
    "arcane tower": ("rook",),
    "armored chariot": ("rook",),
    "clergy riders": ("knight",),
    "corrupted abbot": ("bishop",),
    "damaged chariot": ("rook",),
    "fast chariot": ("rook",),
    "high priest": ("bishop",),
    "joan of arc": ("queen",),
    "lance rider": ("knight",),
    "mule": ("knight",),
    "peasant": ("pawn",),
    "pegasus": ("knight",),
    "sorceress": ("bishop", "rook", "queen"),
    "queen of air": ("bishop", "rook", "queen"),
    "queen of darkness": ("bishop", "rook", "queen"),
    "shield bearer": ("pawn",),
    "the old queen": ("queen",),
    "wild stallion": ("pawn", "knight"),
    "adept": ("pawn",),
    "squire": ("pawn",),
}

# Used only as a fallback when a workbook cannot be read or when creating a
# manifest for known one-special-vs-vanilla files.
STRATEGIES: dict[str, list[tuple[str, str]]] = {
    "Vanilla_vs_Vanilla.xlsx": [],
    "Vanilla_arcane_priest_bishop_vs_Vanilla.xlsx": [("arcane priest", "bishop")],
    "Vanilla_arcane_tower_rook_vs_Vanilla.xlsx": [("arcane tower", "rook")],
    "Vanilla_armored_chariot_rook_vs_Vanilla.xlsx": [("armored chariot", "rook")],
    "Vanilla_clergy_rider_knight_vs_Vanilla.xlsx": [("clergy riders", "knight")],
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
    "Vanilla_sorceress_bishop_vs_Vanilla.xlsx": [("sorceress", "bishop")],
    "Vanilla_sorceress_queen_vs_Vanilla.xlsx": [("sorceress", "queen")],
    "Vanilla_sorceress_rook_vs_Vanilla.xlsx": [("sorceress", "rook")],
    "Vanilla_queen_of_darkness_bishop_vs_Vanilla.xlsx": [("queen of darkness", "bishop")],
    "Vanilla_queen_of_darkness_queen_vs_Vanilla.xlsx": [("queen of darkness", "queen")],
    "Vanilla_queen_of_darkness_rook_vs_Vanilla.xlsx": [("queen of darkness", "rook")],
    "Vanilla_shield_bearer_pawn_vs_Vanilla.xlsx": [("shield bearer", "pawn")],
    "Vanilla_the_old_queen_queen_vs_Vanilla.xlsx": [("the old queen", "queen")],
    "Vanilla_wild_stallion_knight_vs_Vanilla.xlsx": [("wild stallion", "knight")],
    "Vanilla_wild_stallion_pawn_vs_Vanilla.xlsx": [("wild stallion", "pawn")],
    "Vanilla_adept_pawn_vs_Vanilla.xlsx": [("adept", "pawn")],
    "Vanilla_squire_pawn_vs_Vanilla.xlsx": [("squire", "pawn")],
    "Vanilla_all_swap_custom_deployment_vs_Vanilla.xlsx": [("adept", "pawn"), ("arcane priest", "bishop"), ("arcane tower", "rook"), ("pegasus", "knight"), ("sorceress", "queen")],
    "Vanilla_all_swap_vanilla_deployment_vs_Vanilla":[("adept", "pawn"), ("arcane priest", "bishop"), ("arcane tower", "rook"), ("pegasus", "knight"), ("sorceress", "queen")],
    "Vanilla_custom_swap_custom_deployment_vs_Vanilla" :[("arcane priest", "bishop"), ("arcane tower", "rook"), ("pegasus", "knight"), ("sorceress", "queen")],
    "Vanilla_custom_swap_vanilla_deployment_vs_Vanilla": [("arcane priest", "bishop"), ("arcane tower", "rook"), ("pegasus", "knight"), ("sorceress", "queen")]
}

OWNER_COL = "Owner"
PIECE_COL = "Piece"
POSITION_COL = "Starting Position"
WINNER_COL = "Winner"


@dataclass(frozen=True)
class Matchup:
    path: Path
    white_army: Mapping[str, int]
    black_army: Mapping[str, int]
    white_positions: Mapping[str, int]
    black_positions: Mapping[str, int]
    white_wins: int
    black_wins: int
    draws: int
    games: int

    @property
    def white_score(self) -> float:
        return (self.white_wins + 0.5 * self.draws) / self.games


@dataclass(frozen=True)
class FitResult:
    feature_names: tuple[str, ...]
    coefficients: np.ndarray
    standard_errors: np.ndarray
    intercept: float
    intercept_se: float
    iterations: int
    converged: bool
    ridge: float

    def coefficient_map(self) -> dict[str, float]:
        return dict(zip(self.feature_names, self.coefficients, strict=True))

    def se_map(self) -> dict[str, float]:
        return dict(zip(self.feature_names, self.standard_errors, strict=True))


def normalize_name(value: object) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower().replace("_", " "))


def normalize_owner(value: object) -> str:
    owner = normalize_name(value)
    if owner not in {"white", "black"}:
        raise ValueError(f"Unexpected owner value: {value!r}")
    return owner


def read_matchup(path: Path) -> Matchup:
    instances = pd.read_excel(path, sheet_name="Piece Instances")
    games = pd.read_excel(path, sheet_name="Games")

    required_instance = {OWNER_COL, PIECE_COL, POSITION_COL}
    missing = required_instance - set(instances.columns)
    if missing:
        raise ValueError(f"{path.name}: Piece Instances is missing columns {sorted(missing)}")
    if WINNER_COL not in games.columns:
        raise ValueError(f"{path.name}: Games is missing column {WINNER_COL!r}")

    # Piece Instances is an aggregate sheet: one row per starting instance, not
    # one row per game. Therefore each row contributes one piece to the army.
    instances = instances.copy()
    instances[OWNER_COL] = instances[OWNER_COL].map(normalize_owner)
    instances[PIECE_COL] = instances[PIECE_COL].map(normalize_name)
    instances[POSITION_COL] = instances[POSITION_COL].map(normalize_name)

    def army(owner: str) -> dict[str, int]:
        rows = instances.loc[instances[OWNER_COL] == owner, PIECE_COL]
        return rows.value_counts().sort_index().astype(int).to_dict()

    def positioned_army(owner: str) -> dict[str, int]:
        rows = instances.loc[instances[OWNER_COL] == owner, [PIECE_COL, POSITION_COL]]
        keys = rows[PIECE_COL] + "@" + rows[POSITION_COL]
        return keys.value_counts().sort_index().astype(int).to_dict()

    winners = games[WINNER_COL].map(normalize_name)
    allowed = {"white", "black", "draw"}
    unexpected = sorted(set(winners.dropna()) - allowed)
    if unexpected:
        raise ValueError(f"{path.name}: unexpected Winner values: {unexpected}")

    white_wins = int((winners == "white").sum())
    black_wins = int((winners == "black").sum())
    draws = int((winners == "draw").sum())
    game_count = white_wins + black_wins + draws
    if game_count == 0:
        raise ValueError(f"{path.name}: Games contains no outcomes")

    return Matchup(
        path=path,
        white_army=army("white"),
        black_army=army("black"),
        white_positions=positioned_army("white"),
        black_positions=positioned_army("black"),
        white_wins=white_wins,
        black_wins=black_wins,
        draws=draws,
        games=game_count,
    )


def discover_workbooks(results_dir: Path, recursive: bool) -> list[Path]:
    pattern = "**/*.xlsx" if recursive else "*.xlsx"
    paths = sorted(
        p for p in results_dir.glob(pattern)
        if not p.name.startswith("~$") and p.is_file()
    )
    if not paths:
        raise FileNotFoundError(f"No .xlsx files found in {results_dir}")
    return paths


def load_matchups(paths: Iterable[Path], strict: bool) -> tuple[list[Matchup], list[dict[str, str]]]:
    loaded: list[Matchup] = []
    errors: list[dict[str, str]] = []
    for path in paths:
        try:
            loaded.append(read_matchup(path))
        except Exception as exc:  # continue across a large simulation folder
            errors.append({"workbook": path.name, "error": str(exc)})
            if strict:
                raise
    if not loaded:
        details = "; ".join(f"{x['workbook']}: {x['error']}" for x in errors[:5])
        raise RuntimeError(f"No valid matchup workbooks were loaded. {details}")
    return loaded, errors


def build_aggregate_design(
    matchups: Sequence[Matchup],
    use_positions: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, tuple[str, ...]]:
    army_attr = "white_positions" if use_positions else "white_army"
    black_attr = "black_positions" if use_positions else "black_army"

    feature_names = sorted({
        feature
        for matchup in matchups
        for army in (getattr(matchup, army_attr), getattr(matchup, black_attr))
        for feature in army
        if not feature.startswith("king@") and feature != "king"
    })
    index = {name: i for i, name in enumerate(feature_names)}

    x = np.zeros((len(matchups), len(feature_names)), dtype=float)
    successes = np.zeros(len(matchups), dtype=float)
    trials = np.zeros(len(matchups), dtype=float)

    for row, matchup in enumerate(matchups):
        for name, count in getattr(matchup, army_attr).items():
            if name in index:
                x[row, index[name]] += count
        for name, count in getattr(matchup, black_attr).items():
            if name in index:
                x[row, index[name]] -= count
        successes[row] = matchup.white_wins + 0.5 * matchup.draws
        trials[row] = matchup.games

    return x, successes, trials, tuple(feature_names)


def sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-values))


def fit_fractional_logistic_ridge(
    x: np.ndarray,
    successes: np.ndarray,
    trials: np.ndarray,
    feature_names: Sequence[str],
    ridge: float,
    max_iterations: int = 200,
    tolerance: float = 1e-9,
) -> FitResult:
    """Fit aggregate-binomial logistic regression with ridge regularization.

    The intercept is not regularized. Fractional successes are valid here and
    implement the common convention that a draw contributes 0.5 to each side.
    """
    if ridge < 0:
        raise ValueError("ridge must be non-negative")
    if np.any(trials <= 0):
        raise ValueError("all trial counts must be positive")

    n_rows, n_features = x.shape
    design = np.column_stack([np.ones(n_rows), x])
    beta = np.zeros(n_features + 1, dtype=float)
    penalty = np.diag(np.r_[0.0, np.full(n_features, ridge)])
    converged = False

    for iteration in range(1, max_iterations + 1):
        eta = design @ beta
        probability = sigmoid(eta)
        weights = np.maximum(trials * probability * (1.0 - probability), 1e-8)
        gradient = design.T @ (successes - trials * probability) - penalty @ beta
        hessian_positive = (design.T * weights) @ design + penalty

        try:
            step = np.linalg.solve(hessian_positive, gradient)
        except np.linalg.LinAlgError:
            step = np.linalg.pinv(hessian_positive) @ gradient

        beta_new = beta + step
        if np.max(np.abs(beta_new - beta)) < tolerance:
            beta = beta_new
            converged = True
            break
        beta = beta_new

    eta = design @ beta
    probability = sigmoid(eta)
    weights = np.maximum(trials * probability * (1.0 - probability), 1e-8)
    information = (design.T * weights) @ design + penalty
    covariance = np.linalg.pinv(information)
    standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0.0))

    return FitResult(
        feature_names=tuple(feature_names),
        coefficients=beta[1:],
        standard_errors=standard_errors[1:],
        intercept=float(beta[0]),
        intercept_se=float(standard_errors[0]),
        iterations=iteration,
        converged=converged,
        ridge=ridge,
    )


def calculate_anchor_slope(
    coefficients: Mapping[str, float],
    base_costs: Mapping[str, float],
    fallback_slope: float,
) -> tuple[float, pd.DataFrame]:
    """Convert model log-odds strength into points using vanilla pair deltas.

    The slope is fitted through the origin using every available pair:
        coefficient_a - coefficient_b = slope * (cost_a - cost_b)
    Equal-cost pairs are omitted.
    """
    anchors = [piece for piece in base_costs if piece in coefficients]
    rows: list[dict[str, float | str]] = []
    numerator = 0.0
    denominator = 0.0

    for i, left in enumerate(anchors):
        for right in anchors[i + 1:]:
            point_delta = base_costs[left] - base_costs[right]
            if math.isclose(point_delta, 0.0):
                continue
            strength_delta = coefficients[left] - coefficients[right]
            rows.append({
                "piece_a": left,
                "piece_b": right,
                "known_cost_delta": point_delta,
                "learned_strength_delta": strength_delta,
            })
            numerator += point_delta * strength_delta
            denominator += point_delta * point_delta

    calculated_slope = numerator / denominator if denominator else float("nan")
    used_fallback = not math.isfinite(calculated_slope) or calculated_slope <= 0
    slope = fallback_slope if used_fallback else calculated_slope
    if slope <= 0:
        raise ValueError("fallback_slope must be positive")
    if used_fallback:
        warnings.warn(
            "Vanilla anchors could not produce a positive point calibration. "
            f"Using fallback strength-per-point={fallback_slope:.6f}. Run the full "
            "cross-piece dataset for data-driven calibration.",
            stacklevel=2,
        )

    diagnostics = pd.DataFrame(rows)
    if diagnostics.empty:
        diagnostics = pd.DataFrame(columns=[
            "piece_a", "piece_b", "known_cost_delta", "learned_strength_delta"
        ])
    diagnostics["calculated_slope"] = calculated_slope
    diagnostics["used_fallback"] = used_fallback
    diagnostics["predicted_strength_delta"] = diagnostics["known_cost_delta"] * slope
    diagnostics["residual"] = (
        diagnostics["learned_strength_delta"] - diagnostics["predicted_strength_delta"]
    )
    return float(slope), diagnostics


def context_support(
    matchups: Sequence[Matchup],
    special: str,
    base: str,
) -> int:
    support = 0

    for matchup in matchups:
        declared_contexts = STRATEGIES.get(matchup.path.name, [])

        if (special, base) in declared_contexts:
            support += matchup.games

    return support


def recommend_costs(
    fit: FitResult,
    matchups: Sequence[Matchup],
    replacements: Mapping[str, Sequence[str]],
    base_costs: Mapping[str, float],
    slope: float,
    min_cost: float,
    max_cost: float,
    round_to: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    coef = fit.coefficient_map()
    se = fit.se_map()
    context_rows: list[dict[str, float | int | str | bool]] = []

    for special, bases in replacements.items():
        if special not in coef:
            context_rows.append({
                "special_piece": special,
                "replacement_piece": "",
                "replacement_cost": np.nan,
                "strength_premium": np.nan,
                "cost_premium": np.nan,
                "raw_context_cost": np.nan,
                "lower_95_cost": np.nan,
                "upper_95_cost": np.nan,
                "supporting_games": 0,
                "status": "missing from loaded matchups",
            })
            continue

        for base in bases:
            if base not in coef or base not in base_costs:
                context_rows.append({
                    "special_piece": special,
                    "replacement_piece": base,
                    "replacement_cost": base_costs.get(base, np.nan),
                    "strength_premium": np.nan,
                    "cost_premium": np.nan,
                    "raw_context_cost": np.nan,
                    "lower_95_cost": np.nan,
                    "upper_95_cost": np.nan,
                    "supporting_games": 0,
                    "status": "replacement anchor not identifiable",
                })
                continue

            premium = coef[special] - coef[base]
            premium_se = math.sqrt(se[special] ** 2 + se[base] ** 2)
            cost_premium = premium / slope
            raw_cost = base_costs[base] + cost_premium
            lower = base_costs[base] + (premium - 1.96 * premium_se) / slope
            upper = base_costs[base] + (premium + 1.96 * premium_se) / slope
            support = context_support(matchups, special, base)
            context_rows.append({
                "special_piece": special,
                "replacement_piece": base,
                "replacement_cost": base_costs[base],
                "strength_premium": premium,
                "strength_premium_se": premium_se,
                "cost_premium": cost_premium,
                "raw_context_cost": raw_cost,
                "lower_95_cost": lower,
                "upper_95_cost": upper,
                "supporting_games": support,
                "status": "ok",
            })

    contexts = pd.DataFrame(context_rows)
    valid = contexts.loc[contexts["status"] == "ok"].copy()
    summary_rows: list[dict[str, object]] = []

    for special in replacements:
        rows = valid.loc[valid["special_piece"] == special]
        if rows.empty:
            summary_rows.append({
                "special_piece": special,
                "recommended_cost": np.nan,
                "raw_weighted_cost": np.nan,
                "lower_95_cost": np.nan,
                "upper_95_cost": np.nan,
                "replacement_contexts": ", ".join(replacements[special]),
                "supporting_games": 0,
                "context_spread": np.nan,
                "confidence": "not estimable",
            })
            continue

        weights = rows["supporting_games"].to_numpy(dtype=float)
        if weights.sum() <= 0:
            weights = np.ones(len(rows), dtype=float)
        raw = float(np.average(rows["raw_context_cost"], weights=weights))
        lower = float(np.average(rows["lower_95_cost"], weights=weights))
        upper = float(np.average(rows["upper_95_cost"], weights=weights))
        spread = float(rows["raw_context_cost"].max() - rows["raw_context_cost"].min())
        clipped = min(max(raw, min_cost), max_cost)
        rounded = round(clipped / round_to) * round_to
        total_support = int(rows["supporting_games"].sum())
        interval_width = upper - lower

        if total_support >= 5000 and interval_width <= 10 and spread <= 10:
            confidence = "high"
        elif total_support >= 1000 and interval_width <= 25 and spread <= 25:
            confidence = "medium"
        else:
            confidence = "low"

        summary_rows.append({
            "special_piece": special,
            "recommended_cost": rounded,
            "raw_weighted_cost": raw,
            "lower_95_cost": lower,
            "upper_95_cost": upper,
            "replacement_contexts": ", ".join(replacements[special]),
            "supporting_games": total_support,
            "context_spread": spread,
            "confidence": confidence,
        })

    summary = pd.DataFrame(summary_rows).sort_values(
        ["recommended_cost", "special_piece"], na_position="last"
    )
    return summary, contexts


def build_matchup_diagnostics(matchups: Sequence[Matchup], fit: FitResult) -> pd.DataFrame:
    coef = fit.coefficient_map()
    rows: list[dict[str, object]] = []
    for matchup in matchups:
        advantage = fit.intercept
        for piece, count in matchup.white_army.items():
            advantage += coef.get(piece, 0.0) * count
        for piece, count in matchup.black_army.items():
            advantage -= coef.get(piece, 0.0) * count
        predicted = float(sigmoid(np.array([advantage]))[0])
        rows.append({
            "workbook": matchup.path.name,
            "games": matchup.games,
            "white_wins": matchup.white_wins,
            "black_wins": matchup.black_wins,
            "draws": matchup.draws,
            "observed_white_score": matchup.white_score,
            "predicted_white_score": predicted,
            "residual": matchup.white_score - predicted,
            "white_army": json.dumps(matchup.white_army, sort_keys=True),
            "black_army": json.dumps(matchup.black_army, sort_keys=True),
        })
    return pd.DataFrame(rows).sort_values("residual", key=lambda s: s.abs(), ascending=False)


def build_position_report(
    matchups: Sequence[Matchup],
    ridge: float,
    piece_slope: float,
) -> pd.DataFrame:
    x, successes, trials, names = build_aggregate_design(matchups, use_positions=True)
    if x.shape[1] == 0:
        return pd.DataFrame()
    fit = fit_fractional_logistic_ridge(x, successes, trials, names, ridge)
    coef = fit.coefficient_map()
    se = fit.se_map()
    rows: list[dict[str, object]] = []
    for feature in names:
        piece, _, square = feature.partition("@")
        rows.append({
            "piece": piece,
            "starting_position": square,
            "position_strength": coef[feature],
            "position_strength_se": se[feature],
            "approximate_point_strength": coef[feature] / piece_slope,
        })
    return pd.DataFrame(rows).sort_values(["piece", "starting_position"])


def export_results(
    output_path: Path,
    summary: pd.DataFrame,
    contexts: pd.DataFrame,
    coefficients: pd.DataFrame,
    matchup_diagnostics: pd.DataFrame,
    calibration: pd.DataFrame,
    position_report: pd.DataFrame,
    load_errors: Sequence[Mapping[str, str]],
    settings: Mapping[str, object],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        summary.to_excel(writer, sheet_name="Recommended Costs", index=False)
        contexts.to_excel(writer, sheet_name="Replacement Contexts", index=False)
        coefficients.to_excel(writer, sheet_name="Learned Strengths", index=False)
        matchup_diagnostics.to_excel(writer, sheet_name="Matchup Diagnostics", index=False)
        calibration.to_excel(writer, sheet_name="Calibration", index=False)
        if not position_report.empty:
            position_report.to_excel(writer, sheet_name="Position Diagnostics", index=False)
        pd.DataFrame(load_errors).to_excel(writer, sheet_name="Load Errors", index=False)
        pd.DataFrame(
            [{"setting": key, "value": json.dumps(value) if isinstance(value, (dict, list, tuple)) else value}
             for key, value in settings.items()]
        ).to_excel(writer, sheet_name="Settings", index=False)

        workbook = writer.book
        header_format = workbook.add_format({
            "bold": True, "font_color": "white", "bg_color": "#1F4E78",
            "border": 1, "align": "center", "valign": "vcenter",
        })
        percent_format = workbook.add_format({"num_format": "0.0%"})
        decimal_format = workbook.add_format({"num_format": "0.000"})
        cost_format = workbook.add_format({"num_format": "0.0"})

        for sheet_name, frame in {
            "Recommended Costs": summary,
            "Replacement Contexts": contexts,
            "Learned Strengths": coefficients,
            "Matchup Diagnostics": matchup_diagnostics,
            "Calibration": calibration,
            "Position Diagnostics": position_report,
            "Load Errors": pd.DataFrame(load_errors),
        }.items():
            if sheet_name not in writer.sheets:
                continue
            worksheet = writer.sheets[sheet_name]
            worksheet.freeze_panes(1, 0)
            worksheet.autofilter(0, 0, max(len(frame), 1), max(len(frame.columns) - 1, 0))
            for col_index, column in enumerate(frame.columns):
                worksheet.write(0, col_index, column, header_format)
                max_len = max(
                    len(str(column)),
                    *(len(str(v)) for v in frame[column].head(500).fillna("")),
                )
                worksheet.set_column(col_index, col_index, min(max(max_len + 2, 11), 42))

            for col in ("recommended_cost", "raw_weighted_cost", "lower_95_cost", "upper_95_cost",
                        "replacement_cost", "cost_premium", "raw_context_cost", "context_spread"):
                if col in frame.columns:
                    idx = frame.columns.get_loc(col)
                    worksheet.set_column(idx, idx, 16, cost_format)
            for col in ("observed_white_score", "predicted_white_score"):
                if col in frame.columns:
                    idx = frame.columns.get_loc(col)
                    worksheet.set_column(idx, idx, 18, percent_format)
            for col in ("coefficient", "standard_error", "strength_premium", "strength_premium_se", "residual"):
                if col in frame.columns:
                    idx = frame.columns.get_loc(col)
                    worksheet.set_column(idx, idx, 18, decimal_format)

        # Helpful conditional formatting on the main result sheet.
        main = writer.sheets["Recommended Costs"]
        if not summary.empty:
            confidence_col = summary.columns.get_loc("confidence")
            main.conditional_format(1, confidence_col, len(summary), confidence_col, {
                "type": "text", "criteria": "containing", "value": "low",
                "format": workbook.add_format({"bg_color": "#FCE4D6", "font_color": "#9C0006"}),
            })
            main.conditional_format(1, confidence_col, len(summary), confidence_col, {
                "type": "text", "criteria": "containing", "value": "high",
                "format": workbook.add_format({"bg_color": "#E2F0D9", "font_color": "#375623"}),
            })


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output", type=Path, default=Path("special_piece_costs.xlsx"))
    parser.add_argument("--recursive", action="store_true", help="Search subdirectories for .xlsx files")
    parser.add_argument("--strict", action="store_true", help="Stop immediately on an invalid workbook")
    parser.add_argument("--ridge", type=float, default=2.0, help="Regularization strength; larger is more conservative")
    parser.add_argument(
        "--strength-per-point", type=float, default=math.log(0.60 / 0.40) / 10.0,
        help=("Fallback calibration. Default means a 10-point army advantage "
              "predicts roughly a 60%% expected score when anchors cannot calibrate."),
    )
    parser.add_argument("--round-to", type=float, default=5.0, help="Round final costs to this increment")
    parser.add_argument("--min-cost", type=float, default=0.0)
    parser.add_argument("--max-cost", type=float, default=200.0)
    parser.add_argument("--position-report", action="store_true", help="Also fit piece-by-starting-position diagnostics")
    parser.add_argument(
        "--replacement-json", type=Path,
        help="Optional JSON object overriding REPLACEMENTS, e.g. {\"adept\":[\"pawn\"]}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    replacements: Mapping[str, Sequence[str]] = REPLACEMENTS
    if args.replacement_json:
        with args.replacement_json.open("r", encoding="utf-8") as file:
            raw = json.load(file)
        replacements = {
            normalize_name(piece): tuple(normalize_name(base) for base in bases)
            for piece, bases in raw.items()
        }

    paths = discover_workbooks(args.results_dir, args.recursive)
    matchups, load_errors = load_matchups(paths, args.strict)
    x, successes, trials, feature_names = build_aggregate_design(matchups)

    if len(matchups) <= x.shape[1]:
        warnings.warn(
            f"Only {len(matchups)} distinct matchup rows for {x.shape[1]} piece features. "
            "Ridge regularization will stabilize the result, but more cross-piece "
            "matchups are needed for strong confidence.",
            stacklevel=2,
        )

    fit = fit_fractional_logistic_ridge(
        x=x,
        successes=successes,
        trials=trials,
        feature_names=feature_names,
        ridge=args.ridge,
    )
    coefficient_map = fit.coefficient_map()
    slope, calibration = calculate_anchor_slope(
        coefficient_map, BASE_COSTS, args.strength_per_point
    )

    summary, contexts = recommend_costs(
        fit=fit,
        matchups=matchups,
        replacements=replacements,
        base_costs=BASE_COSTS,
        slope=slope,
        min_cost=args.min_cost,
        max_cost=args.max_cost,
        round_to=args.round_to,
    )

    coefficients = pd.DataFrame({
        "piece": fit.feature_names,
        "coefficient": fit.coefficients,
        "standard_error": fit.standard_errors,
        "approximate_point_strength": fit.coefficients / slope,
        "is_vanilla_anchor": [name in BASE_COSTS for name in fit.feature_names],
        "known_base_cost": [BASE_COSTS.get(name, np.nan) for name in fit.feature_names],
    }).sort_values("coefficient", ascending=False)

    diagnostics = build_matchup_diagnostics(matchups, fit)
    position_report = (
        build_position_report(matchups, args.ridge, slope)
        if args.position_report else pd.DataFrame()
    )

    settings = {
        "loaded_workbooks": len(matchups),
        "skipped_workbooks": len(load_errors),
        "total_games": sum(m.games for m in matchups),
        "ridge": args.ridge,
        "round_to": args.round_to,
        "min_cost": args.min_cost,
        "max_cost": args.max_cost,
        "strength_per_point": slope,
        "fallback_strength_per_point": args.strength_per_point,
        "white_advantage_log_odds": fit.intercept,
        "fit_iterations": fit.iterations,
        "fit_converged": fit.converged,
        "draw_scoring": "draw = 0.5 white win + 0.5 black win",
        "base_costs": BASE_COSTS,
        "replacement_rules": replacements,
    }

    export_results(
        output_path=args.output,
        summary=summary,
        contexts=contexts,
        coefficients=coefficients,
        matchup_diagnostics=diagnostics,
        calibration=calibration,
        position_report=position_report,
        load_errors=load_errors,
        settings=settings,
    )

    print(f"Loaded {len(matchups)} workbooks containing {sum(m.games for m in matchups):,} games.")
    print(f"Skipped {len(load_errors)} invalid workbooks.")
    print(f"Model converged: {fit.converged} in {fit.iterations} iterations.")
    print(f"Calibration: {slope:.6f} learned-strength units per point.")
    print(f"Saved: {args.output.resolve()}")


if __name__ == "__main__":
    main()
