"""Run a small reproducible matchup without generating large spreadsheets.

From the chess-with-points-simulator folder:
    python -m examples.quick_matchup --games 4 --turns 40 --seed 123
"""

import argparse
from pathlib import Path

from src.army import generate_standard_army
from src.piece_loader import load_piece_definitions_from_json
from src.simulation import simulate_matchup, summarize_matchup


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small Chess with Points matchup")
    parser.add_argument("--games", type=int, default=4)
    parser.add_argument("--turns", type=int, default=40)
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()

    if args.games < 1 or args.turns < 1:
        parser.error("--games and --turns must be positive")

    project_root = Path(__file__).resolve().parents[1]
    pieces = load_piece_definitions_from_json(project_root / "data" / "standard_pieces.json")
    white_army = generate_standard_army(pieces, "Standard (White)")
    black_army = generate_standard_army(pieces, "Standard (Black)")

    records = simulate_matchup(
        white_army=white_army,
        black_army=black_army,
        games_per_matchup=args.games,
        max_turns=args.turns,
        seed=args.seed,
    )

    print("Chess with Points — Standard matchup")
    print(f"Games: {args.games} | Max turns: {args.turns} | Seed: {args.seed}")
    for metric, value in summarize_matchup(records).items():
        print(f"{metric.replace('_', ' ').title()}: {value}")


if __name__ == "__main__":
    main()
