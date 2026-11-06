from __future__ import annotations

from pathlib import Path
import re
import time
from typing import Iterable

import pandas as pd

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


# ============================================================
# CONFIGURATION
# ============================================================

RESULTS_FOLDER = Path("results")
OUTPUT_FILE = Path("generated_reports/mega_simulation_results.xlsx")

# Use your full STRATEGIES dictionary here.
STRATEGIES: dict[str, list[tuple[str, str]]] = {
    "Vanilla_arcane_priest_bishop_vs_Vanilla.xlsx": [
        ("arcane priest", "bishop"),
    ],
    "Vanilla_arcane_tower_rook_vs_Vanilla.xlsx": [
        ("arcane tower", "rook"),
    ],
    "Vanilla_armored_chariot_rook_vs_Vanilla.xlsx": [
        ("armored chariot", "rook"),
    ],
    "Vanilla_clergy_rider_bishop_vs_Vanilla.xlsx": [
        ("clergy riders", "bishop"),
    ],
    "Vanilla_corrupted_abbot_bishop_vs_Vanilla.xlsx": [
        ("corrupted abbot", "bishop"),
    ],
    "Vanilla_damaged_chariot_rook_vs_Vanilla.xlsx": [
        ("damaged chariot", "rook"),
    ],
    "Vanilla_fast_chariot_rook_vs_Vanilla.xlsx": [
        ("fast chariot", "rook"),
    ],
    "Vanilla_high_priest_bishop_vs_Vanilla.xlsx": [
        ("high priest", "bishop"),
    ],
    "Vanilla_joan_of_arc_queen_vs_Vanilla.xlsx": [
        ("joan of arc", "queen"),
    ],
    "Vanilla_lance_rider_knight_vs_Vanilla.xlsx": [
        ("lance rider", "knight"),
    ],
    "Vanilla_mule_pawn_vs_Vanilla.xlsx": [
        ("mule", "pawn"),
    ],
    "Vanilla_peasant_pawn_vs_Vanilla.xlsx": [
        ("peasant", "pawn"),
    ],
    "Vanilla_pegasus_knight_vs_Vanilla.xlsx": [
        ("pegasus", "knight"),
    ],
    "Vanilla_queen_of_air_bishop_vs_Vanilla.xlsx": [
        ("queen of air", "bishop"),
    ],
    "Vanilla_queen_of_air_queen_vs_Vanilla.xlsx": [
        ("queen of air", "queen"),
    ],
    "Vanilla_queen_of_air_rook_vs_Vanilla.xlsx": [
        ("queen of air", "rook"),
    ],
    "Vanilla_queen_of_darkness_bishop_vs_Vanilla.xlsx": [
        ("queen of darkness", "bishop"),
    ],
    "Vanilla_queen_of_darkness_queen_vs_Vanilla.xlsx": [
        ("queen of darkness", "queen"),
    ],
    "Vanilla_queen_of_darkness_rook_vs_Vanilla.xlsx": [
        ("queen of darkness", "rook"),
    ],
    "Vanilla_shield_bearer_pawn_vs_Vanilla.xlsx": [
        ("shield bearer", "pawn"),
    ],
    "Vanilla_the_old_queen_queen_vs_Vanilla.xlsx": [
        ("the old queen", "queen"),
    ],
    "Vanilla_wild_stallion_knight_vs_Vanilla.xlsx": [
        ("wild stallion", "knight"),
    ],
    "Vanilla_wild_stallion_pawn_vs_Vanilla.xlsx": [
        ("wild stallion", "pawn"),
    ],
}

# Include the standard vanilla control too.
EXCEL_FILES = [
    f"results/{workbook_name}"
    for workbook_name in STRATEGIES.keys()
]

VANILLA_CONTROL_FILE = "results/Vanilla_vs_Vanilla.xlsx"

if VANILLA_CONTROL_FILE not in EXCEL_FILES:
    EXCEL_FILES.append(VANILLA_CONTROL_FILE)

SHEETS_TO_COMBINE = [
    "Piece Summary",
    "Piece Instances",
    "Games",
    "Move History",
]

# Excel allows 1,048,576 rows total, including the header.
EXCEL_MAX_ROWS = 1_048_576
MAX_DATA_ROWS_PER_SHEET = EXCEL_MAX_ROWS - 1

# To keep generated workbooks responsive, you may lower this.
# Leave as None to use Excel's full row capacity.
CUSTOM_MAX_DATA_ROWS: int | None = None

TABLE_STYLE = "TableStyleMedium2"


# ============================================================
# HELPERS
# ============================================================

def format_duration(seconds: float) -> str:
    total_seconds = int(round(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def strategy_label(
    workbook_name: str,
) -> str:
    swaps = STRATEGIES.get(workbook_name, [])

    if not swaps:
        return "Vanilla control"

    return " + ".join(
        f"{special.title()} for {replacement.title()}"
        for special, replacement in swaps
    )


def special_piece_list(
    workbook_name: str,
) -> str:
    swaps = STRATEGIES.get(workbook_name, [])

    if not swaps:
        return ""

    return ", ".join(
        special
        for special, _ in swaps
    )


def replacement_piece_list(
    workbook_name: str,
) -> str:
    swaps = STRATEGIES.get(workbook_name, [])

    if not swaps:
        return ""

    return ", ".join(
        replacement
        for _, replacement in swaps
    )


def safe_table_name(
    value: str,
    existing: set[str],
) -> str:
    cleaned = re.sub(
        r"[^A-Za-z0-9_]",
        "_",
        value,
    )

    if not cleaned:
        cleaned = "Table"

    if cleaned[0].isdigit():
        cleaned = f"T_{cleaned}"

    cleaned = cleaned[:240]
    candidate = cleaned
    suffix = 1

    while candidate in existing:
        suffix += 1
        candidate = f"{cleaned[:230]}_{suffix}"

    existing.add(candidate)
    return candidate


def safe_sheet_name(
    value: str,
    existing: set[str],
) -> str:
    cleaned = re.sub(
        r'[:\\/?*\[\]]',
        "_",
        value,
    )

    cleaned = cleaned[:31] or "Sheet"
    candidate = cleaned
    suffix = 1

    while candidate in existing:
        suffix += 1
        suffix_text = f" {suffix}"
        candidate = (
            cleaned[:31 - len(suffix_text)]
            + suffix_text
        )

    existing.add(candidate)
    return candidate


def chunks(
    dataframe: pd.DataFrame,
    chunk_size: int,
) -> Iterable[pd.DataFrame]:
    for start in range(
        0,
        len(dataframe),
        chunk_size,
    ):
        yield dataframe.iloc[
            start:start + chunk_size
        ].copy()


def normalize_match_summary(
    path: Path,
) -> pd.DataFrame:
    """
    Match Summary is laid out as a title plus Metric/Value rows,
    rather than a normal table. This converts it to one summary row.
    """
    raw = pd.read_excel(
        path,
        sheet_name="Match Summary",
        header=None,
    )

    workbook_name = path.name

    output: dict[str, object] = {
        "source_workbook": workbook_name,
        "matchup_strategy": strategy_label(
            workbook_name
        ),
        "special_pieces": special_piece_list(
            workbook_name
        ),
        "replacement_pieces": replacement_piece_list(
            workbook_name
        ),
    }

    metric_header_row = None

    for row_index in range(len(raw)):
        row_values = [
            str(value).strip().lower()
            if pd.notna(value)
            else ""
            for value in raw.iloc[row_index].tolist()
        ]

        if (
            len(row_values) >= 2
            and row_values[0] == "metric"
            and row_values[1] == "value"
        ):
            metric_header_row = row_index
            break

    if metric_header_row is None:
        output["summary_import_error"] = (
            "Could not locate Metric/Value header."
        )
        return pd.DataFrame([output])

    for row_index in range(
        metric_header_row + 1,
        len(raw),
    ):
        metric = raw.iloc[row_index, 0]
        value = raw.iloc[row_index, 1]

        if pd.isna(metric):
            continue

        metric_name = str(metric).strip()

        if not metric_name:
            continue

        output[metric_name] = value

    return pd.DataFrame([output])


def add_source_columns(
    dataframe: pd.DataFrame,
    workbook_path: Path,
    sheet_name: str,
) -> pd.DataFrame:
    result = dataframe.copy()
    workbook_name = workbook_path.name

    source_columns = {
        "source_workbook":
            workbook_name,
        "source_sheet":
            sheet_name,
        "matchup_strategy":
            strategy_label(workbook_name),
        "special_pieces":
            special_piece_list(workbook_name),
        "replacement_pieces":
            replacement_piece_list(workbook_name),
        "source_row_number":
            range(2, len(result) + 2),
    }

    # Insert in reverse order so final order matches dictionary order.
    for column_name, values in reversed(
        list(source_columns.items())
    ):
        if column_name in result.columns:
            result = result.drop(
                columns=[column_name]
            )

        result.insert(
            0,
            column_name,
            values,
        )

    return result


def read_workbook(
    workbook_path: Path,
) -> tuple[
    dict[str, pd.DataFrame],
    dict[str, object],
]:
    """
    Read one simulation workbook and return:
      - normalized sheet data
      - one workbook summary record
    """
    imported: dict[str, pd.DataFrame] = {}

    summary_record: dict[str, object] = {
        "source_workbook":
            workbook_path.name,
        "file_path":
            str(workbook_path),
        "matchup_strategy":
            strategy_label(workbook_path.name),
        "special_pieces":
            special_piece_list(workbook_path.name),
        "replacement_pieces":
            replacement_piece_list(workbook_path.name),
        "declared_swaps":
            len(
                STRATEGIES.get(
                    workbook_path.name,
                    [],
                )
            ),
        "file_size_bytes":
            workbook_path.stat().st_size,
        "last_modified":
            pd.Timestamp(
                workbook_path.stat().st_mtime,
                unit="s",
            ),
        "import_status":
            "success",
        "import_error":
            "",
    }

    try:
        excel_file = pd.ExcelFile(
            workbook_path
        )

        available_sheets = set(
            excel_file.sheet_names
        )

        if "Match Summary" in available_sheets:
            match_summary = normalize_match_summary(
                workbook_path
            )

            imported[
                "Match Summary"
            ] = match_summary

            summary_record[
                "match_summary_rows"
            ] = len(match_summary)

        for sheet_name in SHEETS_TO_COMBINE:
            if sheet_name not in available_sheets:
                summary_record[
                    f"{sheet_name}_rows"
                ] = 0
                summary_record[
                    f"{sheet_name}_status"
                ] = "missing"
                continue

            dataframe = pd.read_excel(
                workbook_path,
                sheet_name=sheet_name,
            )

            dataframe = add_source_columns(
                dataframe,
                workbook_path,
                sheet_name,
            )

            imported[
                sheet_name
            ] = dataframe

            summary_record[
                f"{sheet_name}_rows"
            ] = len(dataframe)
            summary_record[
                f"{sheet_name}_status"
            ] = "loaded"

    except Exception as error:
        summary_record[
            "import_status"
        ] = "error"

        summary_record[
            "import_error"
        ] = str(error)

    return imported, summary_record


# ============================================================
# EXCEL WRITING
# ============================================================

def write_dataframe_to_sheet(
    worksheet,
    dataframe: pd.DataFrame,
    table_name: str,
) -> None:
    if dataframe.empty:
        worksheet["A1"] = "No rows available."
        return

    # Header
    for column_index, column_name in enumerate(
        dataframe.columns,
        start=1,
    ):
        worksheet.cell(
            row=1,
            column=column_index,
            value=str(column_name),
        )

    # Data
    for row_index, row_values in enumerate(
        dataframe.itertuples(
            index=False,
            name=None,
        ),
        start=2,
    ):
        for column_index, value in enumerate(
            row_values,
            start=1,
        ):
            if pd.isna(value):
                value = None

            # Convert timestamps into regular Python datetimes.
            if isinstance(value, pd.Timestamp):
                value = value.to_pydatetime()

            worksheet.cell(
                row=row_index,
                column=column_index,
                value=value,
            )

    end_row = len(dataframe) + 1
    end_column = len(dataframe.columns)

    table_reference = (
        f"A1:"
        f"{get_column_letter(end_column)}"
        f"{end_row}"
    )

    table = Table(
        displayName=table_name,
        ref=table_reference,
    )

    table.tableStyleInfo = TableStyleInfo(
        name=TABLE_STYLE,
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )

    worksheet.add_table(table)
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = table_reference


def apply_sheet_formatting(
    worksheet,
) -> None:
    header_fill = PatternFill(
        "solid",
        fgColor="4F6D8A",
    )

    header_font = Font(
        bold=True,
        color="FFFFFF",
    )

    thin_border = Border(
        left=Side(
            style="thin",
            color="D1D5DB",
        ),
        right=Side(
            style="thin",
            color="D1D5DB",
        ),
        top=Side(
            style="thin",
            color="D1D5DB",
        ),
        bottom=Side(
            style="thin",
            color="D1D5DB",
        ),
    )

    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )
        cell.border = thin_border

    worksheet.row_dimensions[1].height = 32

    text_heavy_headers = {
        "Game Moves",
        "matchup_strategy",
        "import_error",
        "file_path",
    }

    wide_headers = {
        "source_workbook",
        "special_pieces",
        "replacement_pieces",
    }

    # Inspect a bounded number of rows so formatting remains fast.
    inspection_limit = min(
        worksheet.max_row,
        501,
    )

    for column_index in range(
        1,
        worksheet.max_column + 1,
    ):
        header = worksheet.cell(
            row=1,
            column=column_index,
        ).value

        header_text = str(header or "")
        max_length = len(header_text)

        for row_index in range(
            2,
            inspection_limit + 1,
        ):
            value = worksheet.cell(
                row=row_index,
                column=column_index,
            ).value

            if value is not None:
                max_length = max(
                    max_length,
                    len(str(value)),
                )

        if header_text in text_heavy_headers:
            width = 60
        elif header_text in wide_headers:
            width = 35
        else:
            width = min(
                max(
                    max_length + 2,
                    10,
                ),
                28,
            )

        worksheet.column_dimensions[
            get_column_letter(
                column_index
            )
        ].width = width

    # Number formats based on common column names.
    for column_index in range(
        1,
        worksheet.max_column + 1,
    ):
        header = str(
            worksheet.cell(
                row=1,
                column=column_index,
            ).value
            or ""
        )

        if "Rate" in header:
            number_format = "0.0%"
        elif "Cost" in header:
            number_format = "0.00"
        elif header in {
            "last_modified",
        }:
            number_format = (
                "yyyy-mm-dd hh:mm:ss"
            )
        else:
            continue

        for row_index in range(
            2,
            worksheet.max_row + 1,
        ):
            worksheet.cell(
                row=row_index,
                column=column_index,
            ).number_format = (
                number_format
            )


def write_split_dataframe(
    workbook: Workbook,
    dataframe: pd.DataFrame,
    base_sheet_name: str,
    existing_sheet_names: set[str],
    existing_table_names: set[str],
) -> list[str]:
    """
    Write a dataframe across one or more Excel worksheets.
    Every sheet is an Excel table and therefore filterable.
    """
    max_rows = (
        CUSTOM_MAX_DATA_ROWS
        if CUSTOM_MAX_DATA_ROWS is not None
        else MAX_DATA_ROWS_PER_SHEET
    )

    written_sheets: list[str] = []

    if dataframe.empty:
        sheet_name = safe_sheet_name(
            base_sheet_name,
            existing_sheet_names,
        )

        worksheet = workbook.create_sheet(
            sheet_name
        )

        worksheet["A1"] = "No rows available."
        written_sheets.append(
            sheet_name
        )
        return written_sheets

    for chunk_number, dataframe_chunk in enumerate(
        chunks(dataframe, max_rows),
        start=1,
    ):
        requested_sheet_name = (
            base_sheet_name
            if len(dataframe) <= max_rows
            else f"{base_sheet_name} {chunk_number}"
        )

        sheet_name = safe_sheet_name(
            requested_sheet_name,
            existing_sheet_names,
        )

        worksheet = workbook.create_sheet(
            sheet_name
        )

        table_name = safe_table_name(
            f"{base_sheet_name}_{chunk_number}_Table",
            existing_table_names,
        )

        write_dataframe_to_sheet(
            worksheet,
            dataframe_chunk,
            table_name,
        )

        apply_sheet_formatting(
            worksheet
        )

        written_sheets.append(
            sheet_name
        )

    return written_sheets


# ============================================================
# MEGA WORKBOOK CREATION
# ============================================================

def create_mega_workbook(
    excel_files: list[str],
    output_file: Path,
) -> None:
    start_time = time.perf_counter()

    combined_by_sheet: dict[
        str,
        list[pd.DataFrame],
    ] = {
        "Match Summary": [],
        "Piece Summary": [],
        "Piece Instances": [],
        "Games": [],
        "Move History": [],
    }

    summary_records: list[
        dict[str, object]
    ] = []

    errors: list[dict[str, str]] = []

    for file_number, file_path in enumerate(
        excel_files,
        start=1,
    ):
        workbook_path = Path(
            file_path
        )

        print(
            f"[{file_number}/{len(excel_files)}] "
            f"Reading {workbook_path.name}"
        )

        if not workbook_path.exists():
            error_message = (
                "File was not found."
            )

            errors.append({
                "source_workbook":
                    workbook_path.name,
                "file_path":
                    str(workbook_path),
                "error":
                    error_message,
            })

            summary_records.append({
                "source_workbook":
                    workbook_path.name,
                "file_path":
                    str(workbook_path),
                "matchup_strategy":
                    strategy_label(
                        workbook_path.name
                    ),
                "special_pieces":
                    special_piece_list(
                        workbook_path.name
                    ),
                "replacement_pieces":
                    replacement_piece_list(
                        workbook_path.name
                    ),
                "declared_swaps":
                    len(
                        STRATEGIES.get(
                            workbook_path.name,
                            [],
                        )
                    ),
                "import_status":
                    "missing",
                "import_error":
                    error_message,
            })
            continue

        workbook_data, summary_record = (
            read_workbook(
                workbook_path
            )
        )

        summary_records.append(
            summary_record
        )

        if (
            summary_record[
                "import_status"
            ]
            != "success"
        ):
            errors.append({
                "source_workbook":
                    workbook_path.name,
                "file_path":
                    str(workbook_path),
                "error":
                    str(
                        summary_record[
                            "import_error"
                        ]
                    ),
            })
            continue

        for sheet_name, dataframe in (
            workbook_data.items()
        ):
            combined_by_sheet[
                sheet_name
            ].append(
                dataframe
            )

    combined_frames: dict[
        str,
        pd.DataFrame,
    ] = {}

    for sheet_name, dataframes in (
        combined_by_sheet.items()
    ):
        combined_frames[
            sheet_name
        ] = (
            pd.concat(
                dataframes,
                ignore_index=True,
                sort=False,
            )
            if dataframes
            else pd.DataFrame()
        )

    summary = pd.DataFrame(
        summary_records
    )

    error_report = pd.DataFrame(
        errors,
        columns=[
            "source_workbook",
            "file_path",
            "error",
        ],
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    excel_workbook = Workbook()

    # Remove the default worksheet.
    default_sheet = (
        excel_workbook.active
    )
    excel_workbook.remove(
        default_sheet
    )

    existing_sheet_names: set[str] = set()
    existing_table_names: set[str] = set()

    write_split_dataframe(
        workbook=excel_workbook,
        dataframe=summary,
        base_sheet_name="Workbook Summary",
        existing_sheet_names=existing_sheet_names,
        existing_table_names=existing_table_names,
    )

    display_names = {
        "Match Summary":
            "All Match Summaries",
        "Piece Summary":
            "All Piece Summaries",
        "Piece Instances":
            "All Piece Instances",
        "Games":
            "All Games",
        "Move History":
            "All Move History",
    }

    for source_sheet_name in [
        "Match Summary",
        "Piece Summary",
        "Piece Instances",
        "Games",
        "Move History",
    ]:
        dataframe = combined_frames[
            source_sheet_name
        ]

        print(
            f"Writing {source_sheet_name}: "
            f"{len(dataframe):,} rows"
        )

        write_split_dataframe(
            workbook=excel_workbook,
            dataframe=dataframe,
            base_sheet_name=display_names[
                source_sheet_name
            ],
            existing_sheet_names=existing_sheet_names,
            existing_table_names=existing_table_names,
        )

    if not error_report.empty:
        write_split_dataframe(
            workbook=excel_workbook,
            dataframe=error_report,
            base_sheet_name="Import Errors",
            existing_sheet_names=existing_sheet_names,
            existing_table_names=existing_table_names,
        )

    excel_workbook.save(
        output_file
    )

    elapsed = (
        time.perf_counter()
        - start_time
    )

    print()
    print(
        f"Mega workbook created: "
        f"{output_file.resolve()}"
    )
    print(
        f"Workbooks requested: "
        f"{len(excel_files):,}"
    )
    print(
        f"Workbooks imported: "
        f"{int((summary['import_status'] == 'success').sum()) if not summary.empty else 0:,}"
    )
    print(
        f"Games rows: "
        f"{len(combined_frames['Games']):,}"
    )
    print(
        f"Piece-instance rows: "
        f"{len(combined_frames['Piece Instances']):,}"
    )
    print(
        f"Move-history rows: "
        f"{len(combined_frames['Move History']):,}"
    )
    print(
        f"Runtime: "
        f"{format_duration(elapsed)}"
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    create_mega_workbook(
        excel_files=EXCEL_FILES,
        output_file=OUTPUT_FILE,
    )


if __name__ == "__main__":
    main()