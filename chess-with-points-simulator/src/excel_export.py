from pathlib import Path
from typing import Any
import xlsxwriter
from src.balance import (
    build_piece_match_report,
    build_piece_instance_match_report,
)
from src.game_record import GameRecord
from src.models import PieceDefinition
from src.notation import (
    build_game_notation,
    move_to_notation,
    square_to_chess,
)


def export_matchup_to_excel(
    records: list[GameRecord],
    piece_definitions: dict[str, PieceDefinition],
    output_path: str,
    matchup_name: str
):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    piece_summary = build_piece_match_report(records, piece_definitions)
    piece_instance_summary = build_piece_instance_match_report(records)

    workbook = xlsxwriter.Workbook(str(output_file))
    try:
        formats = create_workbook_formats(workbook)
        write_match_summary_sheet(workbook=workbook, records=records, matchup_name=matchup_name, formats=formats)
        write_dictionary_report_sheet(workbook=workbook, sheet_name="Piece Summary", rows=piece_summary, formats=formats)
        write_dictionary_report_sheet(workbook=workbook, sheet_name="Piece Instances", rows=piece_instance_summary, formats=formats)
        write_games_sheet (workbook=workbook, records=records, formats=formats)
        write_move_history_sheet(workbook=workbook, records=records, formats=formats)
    finally:
        workbook.close()

    return str(output_file)

def create_workbook_formats(workbook: xlsxwriter.Workbook):
    return {
        "title": workbook.add_format({
            "bold": True,
            "font_size": 16,
            "align": "center",
            "valign": "vcenter",
        }),

        "header": workbook.add_format({
            "bold": True,
            "border": 1,
            "text_wrap": True,
            "align": "center",
            "valign": "vcenter",
        }),

        "text": workbook.add_format({
            "border": 1,
            "valign": "top",
        }),

        "wrapped_text": workbook.add_format({
            "border": 1,
            "text_wrap": True,
            "valign": "top",
        }),

        "integer": workbook.add_format({
            "border": 1,
            "num_format": "0",
        }),

        "decimal": workbook.add_format({
            "border": 1,
            "num_format": "0.00",
        }),

        "percent": workbook.add_format({
            "border": 1,
            "num_format": "0.00%",
        }),
    }

def write_match_summary_sheet(workbook:xlsxwriter.Workbook, records: list[GameRecord], matchup_name:str, formats:dict[str, Any]):
    worksheet = workbook.add_worksheet("Match Summary")
    game_count = len(records)
    white_wins = sum(1 for record in records if record.winner=="white")
    black_wins = sum(1 for record in records if record.winner=="black")
    draws = sum(1 for record in records if record.winner is None)

    total_moves = sum(record.total_moves for record in records)
    average_moves = (total_moves / game_count if game_count else 0)
    total_captures =sum(len(record.captures) for record in records)
    total_checks =sum(len(record.checks) for record in records)
    total_checkmates =sum(len(record.checkmates) for record in records)
    total_promotions =sum(len(record.promotions) for record in records)
    total_swaps =sum(len(record.swaps) for record in records)
    total_leaps =sum(len(record.leaps) for record in records)
    total_opponent_control_moves  =sum(len(record.opponent_control_moves) for record in records)
    total_shield_blocks  = sum(
        move.shield_blocks_used
        for record in records
        for move in record.move_history
    )
    worksheet.merge_range(
        "A1:B1",
        matchup_name,
        formats["title"],
    )
    summary_rows = [
        ("Games", game_count),
        ("White Wins", white_wins),
        ("Black Wins", black_wins),
        ("Draws", draws),
        ("White Win Rate", white_wins / game_count if game_count else 0),
        ("Black Win Rate", black_wins / game_count if game_count else 0),
        ("Draw Rate", draws / game_count if game_count else 0),
        ("Total Moves", total_moves),
        ("Average Moves per Game", average_moves),
        ("Total Captures", total_captures),
        ("Total Checks", total_checks),
        ("Total Checkmates", total_checkmates),
        ("Total Promotions", total_promotions),
        ("Total Shield Blocks", total_shield_blocks),
        ("Total Swaps", total_swaps),
        ("Total Leaps", total_leaps),
        (
            "Total Opponent-Controlled Moves",
            total_opponent_control_moves,
        ),
    ]
    worksheet.write(
        2,
        0,
        "Metric",
        formats["header"],
    )
    worksheet.write(
        2,
        1,
        "Value",
        formats["header"],
    )

    percentage_metrics = {
        "White Win Rate",
        "Black Win Rate",
        "Draw Rate",
    }

    decimal_metrics = {
        "Average Moves per Game",
    }
    for row_index, (metric, value) in enumerate(
        summary_rows,
        start=3,
    ):
        worksheet.write(
            row_index,
            0,
            metric,
            formats["text"],
        )

        if metric in percentage_metrics:
            value_format = formats["percent"]
        elif metric in decimal_metrics:
            value_format = formats["decimal"]
        else:
            value_format = formats["integer"]

        worksheet.write(
            row_index,
            1,
            value,
            value_format,
        )

    worksheet.set_column("A:A", 34)
    worksheet.set_column("B:B", 18)
    worksheet.freeze_panes(3, 0)

def write_dictionary_report_sheet(workbook:xlsxwriter.Workbook, sheet_name:str, rows:list[dict], formats:dict[str, Any]):
    worksheet = workbook.add_worksheet(
        sheet_name[:31]
    )
    if not rows:
        worksheet.write(
            0,
            0,
            "No data available",
        )
        return
    columns = list(rows[0].keys())
    
    for column_index, column_name in enumerate(
        columns
    ):
        worksheet.write(
            0,
            column_index,
            format_column_name(column_name),
            formats["header"],
        )

    for row_index, row in enumerate(
        rows,
        start=1,
    ):
        for column_index, column_name in enumerate(
            columns
        ):
            value = row.get(column_name)

            write_report_value(
                worksheet=worksheet,
                row_index=row_index,
                column_index=column_index,
                column_name=column_name,
                value=value,
                formats=formats,
            )

    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(
        0,
        0,
        len(rows),
        len(columns) - 1,
    )

    for column_index, column_name in enumerate(
        columns
    ):
        width = calculate_column_width(
            column_name=column_name,
            rows=rows,
        )

        worksheet.set_column(
            column_index,
            column_index,
            width,
        )
def format_column_name(column_name: str) -> str:
    special_names = {
        "piece_id": "Piece ID",
        "piece_instance_id": "Piece Instance ID",
        "piece_cost": "Piece Cost",
        "starting_position": "Starting Position",
        "moves_per_game": "Moves per Game",
        "number_of_wins_white": "Number of Wins (White)",
        "number_of_wins_black": "Number of Wins (Black)",
        "number_of_draws": "Number of Draws",
        "median_pieces_captured": "Median Pieces Captured",
        "median_piece_cost_captured":
            "Median Pieces × Cost Captured",
        "median_number_of_shields_used":
            "Median Number of Shields Used",
        "median_number_of_swaps":
            "Median Number of Swaps",
        "median_number_of_opponent_controlled":
            "Median Number of Opponent Controlled",
        "median_number_of_times_used":
            "Median Number of Times Used",
        "median_number_of_times_used_to_check_or_checkmate":
            "Median Times Used to Check/Checkmate",
        "median_number_of_legal_moves":
            "Median Number of Legal Moves",
        "survival_rate": "Survival Rate",
    }

    if column_name in special_names:
        return special_names[column_name]

    return column_name.replace(
        "_",
        " ",
    ).title()

def write_report_value(
    worksheet,
    row_index: int,
    column_index: int,
    column_name: str,
    value,
    formats: dict[str, Any],
) -> None:
    if value is None:
        worksheet.write_blank(
            row_index,
            column_index,
            None,
            formats["text"],
        )
        return

    if column_name == "starting_position":
        if isinstance(value, tuple):
            value = square_to_chess(value)

        worksheet.write(
            row_index,
            column_index,
            value,
            formats["text"],
        )
        return

    if column_name.endswith("_rate"):
        worksheet.write(
            row_index,
            column_index,
            value,
            formats["percent"],
        )
        return

    if isinstance(value, bool):
        worksheet.write_boolean(
            row_index,
            column_index,
            value,
            formats["text"],
        )
        return

    if isinstance(value, int):
        worksheet.write_number(
            row_index,
            column_index,
            value,
            formats["integer"],
        )
        return

    if isinstance(value, float):
        worksheet.write_number(
            row_index,
            column_index,
            value,
            formats["decimal"],
        )
        return

    if isinstance(value, tuple):
        value = str(value)

    worksheet.write(
        row_index,
        column_index,
        value,
        formats["text"],
    )

def calculate_column_width(
    column_name: str,
    rows: list[dict],
) -> int:
    header_length = len(
        format_column_name(column_name)
    )

    value_lengths = [
        len(str(row.get(column_name, "")))
        for row in rows[:200]
    ]

    longest = max(
        [header_length, *value_lengths]
    )

    return min(
        max(longest + 2, 12),
        45,
    )

def write_games_sheet(workbook:xlsxwriter.Workbook, records:list[GameRecord], formats:dict[str, Any]):
    worksheet = workbook.add_worksheet("Games")

    headers = [
        "Game",
        "Seed",
        "Winner",
        "Reason",
        "Total Moves",
        "Captures",
        "Checks",
        "Checkmates",
        "Promotions",
        "Shield Blocks",
        "Swaps",
        "Leaps",
        "Opponent-Controlled Moves",
        "Game Moves",
    ]

    for column_index, header in enumerate(headers):
        worksheet.write(
            0,
            column_index,
            header,
            formats["header"],
        )

    for game_index, record in enumerate(
        records,
        start=1,
    ):
        row_index = game_index

        game_notation = build_game_notation(
            record.move_history
        )

        shield_count = sum(
            move.shield_blocks_used
            for move in record.move_history
        )

        values = [
            game_index,
            record.seed,
            record.winner or "draw",
            record.reason,
            record.total_moves,
            len(record.captures),
            len(record.checks),
            len(record.checkmates),
            len(record.promotions),
            shield_count,
            len(record.swaps),
            len(record.leaps),
            len(record.opponent_control_moves),
            game_notation,
        ]

        for column_index, value in enumerate(values):
            if column_index == 12:
                cell_format = formats["wrapped_text"]
            elif isinstance(value, int):
                cell_format = formats["integer"]
            else:
                cell_format = formats["text"]

            worksheet.write(
                row_index,
                column_index,
                value,
                cell_format,
            )

    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(
        0,
        0,
        len(records),
        len(headers) - 1,
    )

    worksheet.set_column("A:A", 10)
    worksheet.set_column("B:B", 10)
    worksheet.set_column("C:C", 10)
    worksheet.set_column("D:D", 18)
    worksheet.set_column("E:M", 18)
    worksheet.set_column("N:N", 100)

def write_move_history_sheet(
    workbook: xlsxwriter.Workbook,
    records: list[GameRecord],
    formats: dict[str, Any],
) -> None:
    worksheet = workbook.add_worksheet(
        "Move History"
    )

    headers = [
        "Game",
        "Turn",
        "Move Number",
        "Player",
        "Piece Instance ID",
        "Piece",
        "Piece ID",
        "Piece Cost",
        "From",
        "To",
        "Notation",
        "Captured Piece",
        "Captured Instance ID",
        "Captured Piece ID",
        "Captured Piece Cost",
        "Check",
        "Checkmate",
        "Legal Moves",
        "Promoted From",
        "Promoted To",
        "Shield Blocks Used",
        "Swap Used",
        "Swapped With",
        "Swapped With Instance ID",
        "Leap Used",
        "Opponent Control Used",
        "Controlled Piece",
        "Controlled Piece Instance ID",
    ]

    for column_index, header in enumerate(headers):
        worksheet.write(
            0,
            column_index,
            header,
            formats["header"],
        )

    row_index = 1

    for game_index, record in enumerate(
        records,
        start=1,
    ):
        for move in record.move_history:
            move_number = (
                move.turn + 1
            ) // 2

            values = [
                game_index,
                move.turn,
                move_number,
                move.player,
                move.piece_instance_id,
                move.piece,
                move.piece_id,
                move.piece_cost,
                square_to_chess(move.from_square),
                square_to_chess(move.to_square),
                move_to_notation(move),
                move.captured,
                move.captured_piece_instance_id,
                move.captured_piece_id,
                move.captured_piece_cost,
                move.created_check,
                move.created_checkmate,
                move.legal_move_count,
                move.promoted_from,
                move.promoted_to,
                move.shield_blocks_used,
                move.swap_used,
                move.swapped_with,
                move.swapped_with_instance_id,
                move.leap_used,
                move.opponent_control_used,
                move.controlled_piece,
                move.controlled_piece_instance_id,
            ]

            for column_index, value in enumerate(values):
                if value is None:
                    worksheet.write_blank(
                        row_index,
                        column_index,
                        None,
                        formats["text"],
                    )
                elif isinstance(value, bool):
                    worksheet.write_boolean(
                        row_index,
                        column_index,
                        value,
                        formats["text"],
                    )
                elif isinstance(value, int):
                    worksheet.write_number(
                        row_index,
                        column_index,
                        value,
                        formats["integer"],
                    )
                else:
                    worksheet.write(
                        row_index,
                        column_index,
                        value,
                        formats["text"],
                    )

            row_index += 1

    worksheet.freeze_panes(1, 0)

    if row_index > 1:
        worksheet.autofilter(
            0,
            0,
            row_index - 1,
            len(headers) - 1,
        )

    worksheet.set_column("A:D", 12)
    worksheet.set_column("E:E", 24)
    worksheet.set_column("F:H", 16)
    worksheet.set_column("I:K", 12)
    worksheet.set_column("L:O", 22)
    worksheet.set_column("P:AB", 20)