from src.models import PieceInstance
from src.piece_loader import load_piece_definitions_from_json

PIECES = load_piece_definitions_from_json("data/standard_pieces.json")


def make_piece(name: str, owner: str = "white", position=(0, 0), is_noble = False) -> PieceInstance:
    return PieceInstance(PIECES[name], owner, position, is_noble=is_noble)

def get_piece_definition(name: str):
    global PIECES
    return PIECES[name]