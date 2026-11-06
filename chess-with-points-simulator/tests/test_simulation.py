from src.army import generate_group_a_army
from src.piece_loader import load_piece_definitions_from_json
from src.simulation import (
    create_standard_board,
    get_all_legal_moves_for_player,
    simulate_game_with_armies,
    simulate_random_game,
)

def test_standard_board_has_32_pieces():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    board = create_standard_board(pieces)

    assert len(board.squares) == 32


def test_game_starts_with_white():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    board = create_standard_board(pieces)

    assert board.current_player == "white"


def test_white_has_legal_moves_at_start():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    board = create_standard_board(pieces)

    legal_moves = get_all_legal_moves_for_player(board, "white")

    assert len(legal_moves) > 0


def test_random_game_completes():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    result = simulate_random_game(
        piece_definitions=pieces,
        max_turns=20,
        seed=123,
    )

    assert "winner" in result
    assert "reason" in result
    assert "turns" in result
    assert result["turns"] <= 20

from src.piece_loader import load_piece_definitions_from_json
from src.simulation import create_standard_board, choose_random_move
from src.rules import get_legal_moves, validate_board_state, is_in_check


def test_random_game_only_uses_valid_moves():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")
    board = create_standard_board(pieces)

    for turn in range(80):
        current_player = board.current_player

        move, move_context = choose_random_move(board, current_player)

        if move is None:
            break

        from_square = move["from_square"]
        to_square = move["to_square"]
        piece = board.get_piece_at(from_square)

        assert piece is not None
        assert piece.owner == current_player
        assert to_square in get_legal_moves(board, piece)

        captured_piece = board.get_piece_at(to_square)

        if captured_piece is not None:
            assert captured_piece.owner != current_player

        board.move_piece(from_square, to_square)

        validate_board_state(board)

        assert is_in_check(board, current_player) is False

        board.switch_turn()

def test_group_a_army_with_adepts_can_simulate_game():
    pieces = load_piece_definitions_from_json("data/standard_pieces.json")

    white_army = generate_group_a_army(pieces)
    black_army = generate_group_a_army(pieces)

    record = simulate_game_with_armies(
        white_army=white_army,
        black_army=black_army,
        max_turns=25,
        seed=123,
    )

    assert record.reason in {"checkmate", "no legal actions", "no legal moves", "move limit"}
    assert record.total_moves <= 25
    assert hasattr(record, "swaps")
