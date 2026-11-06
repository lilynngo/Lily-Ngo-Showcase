import random
from src.models import PieceInstance
from src.board import Board
from src.rules import copy_board, get_attack_squares, is_checkmate, is_in_check, is_square_attacked, other_player

from src.actions import(
    execute_swap,
    execute_leap,
    execute_opponent_control_move
)

CAPTURE_WEIGHT = 1.0
CHECK_BONUS = 5
CHECKMATE_BONUS = 10_000
PROMOTION_BONUS = 50
CENTER_BONUS = 2
UNSAFE_MOVE_PENALTY = 8
RANDOMNESS = 3

def get_piece_value(piece:PieceInstance):
    if piece is None:
        return 0
    return piece.definition.cost


def apply_action_to_copy(board:Board, move:dict, player:str):
    board_copy = copy_board(board)
    from_square = move["from_square"]
    to_square = move["to_square"]

    if move["type"] == "swap":
        execute_swap(board_copy, from_square, to_square)
    elif move["type"] == "leap":
        execute_leap(board_copy, from_square, to_square)
    elif move["type"] == "opponent_control_move":
        execute_opponent_control_move(board_copy, from_square, to_square, controller=player)
    else:
        board_copy.move_piece(from_square, to_square)
    return board_copy

def score_action(board:Board, move:dict, player:str):
    from_square = move["from_square"]
    to_square = move["to_square"]

    moving_piece = board.get_piece_at(from_square)
    target_piece = board.get_piece_at(to_square)
    opponent = other_player(player)
    score = 0

    ## Add prefernce for captures
    if target_piece is not None and target_piece.owner != player:
        score += target_piece.definition.cost * 10
        if moving_piece is not None:
            score -= moving_piece.definition.cost
    
    ## Pref special actions
    if move["type"] == "swap":
        score += 5

    if move["type"] == "leap":
        score += 5

    # if move["type"] == "opponent_control_move":
    #     score += 5

    try:
        board_after = apply_action_to_copy(board, move, player)

        # prefs checking the enemy after move
        if is_in_check(board_after, opponent):
            score += 25

        # if ends up in bad spot, decrease value
        moved_piece = board_after.get_piece_at(to_square)
        if moved_piece is not None and moved_piece.owner == player:
            if is_square_attacked(board_after, to_square, opponent):
                score -= moved_piece.definition.cost * 3
    except Exception:
        return -9999999
    
    score += random.randint(0,10) # gotta add some randomness :)
    return score

def is_promotion_move(board, move:dict, player: str) -> bool:
    moving_piece = board.get_piece_at(move["from_square"])

    if moving_piece is None:
        return False

    if moving_piece.definition.name not in {"pawn", "squire", "shield bearer", "adept"}:
        return False

    destination_row, _ = move["to_square"]

    if player == "white":
        return destination_row == 7

    return destination_row == 0

def score_action_ver2(board:Board, move:dict, player:str):
    score = random.uniform(0, 3)

    from_square = move["from_square"]
    to_square = move["to_square"]
    move_type = move["type"]

    moving_piece = board.get_piece_at(from_square)
    target_piece = board.get_piece_at(to_square)

    if target_piece is not None:
        score += target_piece.definition.cost
    target_piece = board.get_piece_at(to_square)
    simulated_board = copy_board(board)
    if move_type == "swap":
        swap_info = execute_swap(simulated_board, from_square, to_square)
    elif move_type == "leap":
        leap_info = execute_leap(simulated_board, from_square, to_square)
    elif move_type == "opponent_control_move":
        moving_piece = simulated_board.get_piece_at(from_square)
        if moving_piece is None:
            raise RuntimeError(f"No opponent controlled piece at {from_square}. Action was = {move}")
        opponent_control_info = execute_opponent_control_move(
            simulated_board,
            from_square,
            to_square,
            controller=player,
        )
    else:
        captured_piece = simulated_board.get_piece_at(to_square)
        if captured_piece and captured_piece.owner == player:
            raise RuntimeError("Friendly capture attempted.")
        simulated_board.move_piece(from_square, to_square)

    opponent = "black" if player == "white" else "white"

    if is_checkmate(simulated_board, opponent):
        score += 10_000
    elif is_in_check(simulated_board, opponent):
        score += 5

    if is_promotion_move(simulated_board, move, player):
        score += 50

    if move["to_square"] in {
        (3, 3), (3, 4), (4, 3), (4, 4)
    }:
        score += 2

    moved_piece:PieceInstance = simulated_board.get_piece_at(move["to_square"])

    if moved_piece is not None:
        if is_square_attacked(simulated_board,move["to_square"], opponent):
            if moved_piece.definition.type == "commoner":
                score -= 1
            else:
                score -= 5

    return score

def choose_smart_move(board:Board, player:str, legal_moves:list[dict]):
    if not legal_moves:
        return None
    return choose_weighted_ai_move(board, player, legal_moves)

def choose_weighted_ai_move(board:Board, player:str, legal_moves:list[dict]):

    scored = sorted(
        (
            (score_action_ver2(board, move, player), move)
            for move in legal_moves
        ),
        key=lambda item: item[0],
        reverse=True,
    )

    roll = random.random()

    if roll < 0.70:
        return scored[0][1]

    if roll < 0.90:
        candidates = scored[1:3] or scored[:1]
        return random.choice(candidates)[1]

    return random.choice(scored)[1]