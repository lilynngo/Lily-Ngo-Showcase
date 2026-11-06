import json
from pathlib import Path
from src.models import PieceDefinition

from pathlib import Path


REQUIRED_FIELDS = {
    "id",
    "name",
    "type",
    "cost",
    "movement",
    "traits",
    "drawbacks",
    "is_king_status",
}

def validate_piece_json(raw_piece:dict) -> None:
    missing_fields = REQUIRED_FIELDS - set(raw_piece.keys())
    if missing_fields:
        raise ValueError(
            f"Piece definition is missing required fields: {missing_fields}"
        )

    if not isinstance(raw_piece["id"], int):
        raise ValueError(f"Piece id must be an integer: {raw_piece}")

    if not isinstance(raw_piece["name"], str) or not raw_piece["name"].strip():
        raise ValueError(f"Piece name must be a non-empty string: {raw_piece}")

    if raw_piece["type"] not in {"commoner", "noble", "both"}:
        raise ValueError(
            f"Invalid piece type for {raw_piece['name']}: {raw_piece['type']}"
        )

    if not isinstance(raw_piece["cost"], int) or raw_piece["cost"] < 0:
        raise ValueError(
            f"Piece cost must be a non-negative integer: {raw_piece['name']}"
        )

    if not isinstance(raw_piece["movement"], str) or not raw_piece["movement"].strip():
        raise ValueError(
            f"Piece movement must be a non-empty string: {raw_piece['name']}"
        )

    if not isinstance(raw_piece["traits"], list):
        raise ValueError(f"Traits must be a list: {raw_piece['name']}")

    if not isinstance(raw_piece["drawbacks"], list):
        raise ValueError(f"Drawbacks must be a list: {raw_piece['name']}")

    if not isinstance(raw_piece["is_king_status"], bool):
        raise ValueError(
            f"is_king_status must be true or false: {raw_piece['name']}"
        )
    
def load_piece_definitions_from_json(file_path):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Piece Definition not found at {path}")

    with path.open("r", encoding="utf-8") as file:
        raw_pieces = json.load(file)
    
    if not isinstance(raw_pieces, list):
        raise ValueError("Piece JSON must contain a list of all the piece definitions")
    pieces: dict[str, PieceDefinition] = {}

    for raw_piece in raw_pieces:
        validate_piece_json(raw_piece)
        piece = PieceDefinition(
            id=raw_piece["id"],
            name=raw_piece["name"].strip(),
            type=raw_piece["type"].strip(),
            cost=raw_piece["cost"],
            movement=raw_piece["movement"].strip().lower(),
            traits=list(raw_piece["traits"]),
            drawbacks=list(raw_piece["drawbacks"]),
            is_king_status=raw_piece["is_king_status"],
        )

        key = piece.name.lower()
        if key in pieces:
            raise ValueError(f"Duplicate piece name found: {key}")
        pieces[key] = piece
    return pieces