
from concurrent.futures import ProcessPoolExecutor
import os
import re

from src.army import Army
from src.excel_export import export_matchup_to_excel
from src.models import PieceDefinition
from src.simulation import create_board_from_armies, simulate_game_with_armies


def print_army_summary(army, player):
    print(f"{player} Army Summary:")
    print(f"Total Pieces: {army.size()}")
    print(f"Commoners: {army.count_by_type('Commoner')}")
    print(f"Nobles: {army.count_by_type('Noble')}")
    print(f"Total Cost: {army.total_cost()}")
    print(f"Has King Status: {army.has_king_status_piece()}")
    print()

    piece_counts = {}

    for piece in army.pieces:
        piece_counts[piece.name] = piece_counts.get(piece.name, 0) + 1

    print("Pieces:")
    for name, count in piece_counts.items():
        print(f"- {name}: {count}")

    print()    

def print_gameboard(white_army:Army, black_army:Army):
    board = create_board_from_armies(white_army, black_army)
    print(board.print_starting_game_board())


def make_safe_filename(value: str, replacement: str = "_") -> str:
    # Replace Windows-invalid filename characters.
    value = re.sub(r'[<>:"/\\|?*]', replacement, value)

    # Replace repeated whitespace with underscores.
    value = re.sub(r"\s+", replacement, value.strip())

    # Collapse repeated replacement characters.
    value = re.sub(
        rf"{re.escape(replacement)}+",
        replacement,
        value,
    )

    # Windows filenames cannot end with a space or period.
    value = value.rstrip(" .")

    return value or "unnamed_matchup"

def simulate_matchups(white_army:Army, black_army:Army, piece_definitions:dict[str, PieceDefinition], max_turns:int=1000, games_per_matchup:int=100, max_workers:int=4, seed:int=1234):

    print( "\n".join([
        "",
        "=" * 45,
        f"Starting simulation for {white_army.name} vs {black_army.name}",
        "=" * 45,
        "",
    ]))
    print_gameboard(white_army, black_army)
    records = simulate_matchup_parallel(
        white_army=white_army,
        black_army=black_army,
        games_per_matchup=games_per_matchup,
        max_turns=max_turns,
        seed=seed,
        max_workers=max_workers,
    )    
    matchup_name = make_safe_filename(
        f"{white_army.name}_vs_{black_army.name}"
    )
    saved_file = export_matchup_to_excel(
        records=records,
        piece_definitions=piece_definitions,
        output_path=f"results/{matchup_name}.xlsx",
        matchup_name=matchup_name,
    )
    print(f"Saved workbook: {saved_file}")

def simulate_matchup_parallel(
    white_army: Army,
    black_army: Army,
    games_per_matchup: int = 10,
    max_turns: int = 100,
    seed: int | None = None,
    max_workers: int | None = None,
) :
    if max_workers is None:
        max_workers = os.cpu_count() or 1

    jobs = []

    for game_index in range(games_per_matchup):
        game_seed = None

        if seed is not None:
            game_seed = seed + game_index

        jobs.append(
            (
                white_army,
                black_army,
                max_turns,
                game_seed,
                game_index
            )
        )

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        records = list(executor.map(simulate_single_game_worker, jobs))

    return records

def simulate_single_game_worker(args):
    white_army, black_army, max_turns, seed, game_index = args

    return simulate_game_with_armies(
        white_army=white_army,
        black_army=black_army,
        max_turns=max_turns,
        seed=seed,
        match_number = game_index
    )

