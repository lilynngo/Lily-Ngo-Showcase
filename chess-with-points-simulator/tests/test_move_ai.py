from src.board import Board
from src.move_ai import score_action, choose_smart_move
from tests.helpers import make_piece

def test_smart_action_scores_capture_higher_than_non_capture():
    board = Board()

    white_king = make_piece("king", "white", (7, 7))
    black_king = make_piece("king", "black", (7, 0))

    rook = make_piece("rook", "white", (0, 0))
    enemy_queen = make_piece("queen", "black", (0, 5))

    board.place_piece(white_king, (7, 7))
    board.place_piece(black_king, (7, 0))
    board.place_piece(rook, (0, 0))
    board.place_piece(enemy_queen, (0, 5))

    quiet_action = {
        "type": "move",
        "from_square": (0, 0),
        "to_square": (0, 1),
    }

    capture_action = {
        "type": "move",
        "from_square": (0, 0),
        "to_square": (0, 5),
    }

    assert score_action(board, capture_action, "white") > score_action(
        board,
        quiet_action,
        "white",
    )

def test_smart_action_scores_capture_higher_than_quiet_move():
    board = Board()

    white_king = make_piece("king", "white", (7, 7))
    black_king = make_piece("king", "black", (7, 0))

    rook = make_piece("rook", "white", (0, 0))
    enemy_queen = make_piece("queen", "black", (0, 5))

    board.place_piece(white_king, (7, 7))
    board.place_piece(black_king, (7, 0))
    board.place_piece(rook, (0, 0))
    board.place_piece(enemy_queen, (0, 5))

    quiet_action = {
        "type": "move",
        "from_square": (0, 0),
        "to_square": (0, 1),
    }

    capture_action = {
        "type": "move",
        "from_square": (0, 0),
        "to_square": (0, 5),
    }

    assert score_action(board, capture_action, "white") > score_action(
        board,
        quiet_action,
        "white",
    )