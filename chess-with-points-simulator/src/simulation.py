import random
import time

from src.notation import get_san_disambiguation
from src.actions import (
    execute_swap,
    execute_leap,
    execute_opponent_control_move
)
from src.moves import is_white_square, is_black_square
from src.game_record import GameRecord, MoveRecord
from src.army import Army, assign_piece_instance_ids, validate_army, generate_random_army_assignments, place_assignments_on_board,get_starting_noble_lineup
from src.board import Board
from src.models import PieceDefinition, PieceInstance
from src.rules import get_all_legal_moves_for_player, get_enemy_player, get_legal_moves,  is_checkmate, is_in_check, opponent_control_move_leaves_king_in_check, other_player, validate_board_state
from src.move_ai import choose_smart_move

def create_random_board_from_lineups(
    white_nobles: list[PieceDefinition],
    white_commoners: list[PieceDefinition],
    black_nobles: list[PieceDefinition],
    black_commoners: list[PieceDefinition],
    seed: int | None = None):
    
    rng = random.Random(seed)

    board = Board()

    white_assignments = generate_random_army_assignments(
        nobles=white_nobles,
        commoners=white_commoners,
        owner="white",
        rng=rng,
    )

    black_assignments = generate_random_army_assignments(
        nobles=black_nobles,
        commoners=black_commoners,
        owner="black",
        rng=rng,
    )

    place_assignments_on_board(board, white_assignments)
    place_assignments_on_board(board, black_assignments)

    board.current_player = "white"
    validate_board_state(board)

    starting_noble_lineup = {
        "white": get_starting_noble_lineup(white_assignments),
        "black": get_starting_noble_lineup(black_assignments),
    }

    return board, starting_noble_lineup

def create_standard_board(piece_definitions:dict[str, PieceDefinition]):
    board = Board()
    back_rank = [
        "rook",
        "knight",
        "bishop",
        "queen",
        "king",
        "bishop",
        "knight",
        "rook",
    ]

    front_rank = [
        "pawn",
        "pawn",
        "pawn",
        "pawn",
        "pawn",
        "pawn",
        "pawn",
        "pawn"
    ]

    for col, piece_name in enumerate(back_rank):
        white_piece = PieceInstance(piece_definitions[piece_name], "white", (0, col))
        board.place_piece(white_piece, (0, col))

    for col, piece_name in enumerate(front_rank):
        white_piece = PieceInstance(piece_definitions[piece_name], "white", (1, col))
        board.place_piece(white_piece, (1, col))

    for col, piece_name in enumerate(front_rank):
        black_piece = PieceInstance(piece_definitions[piece_name], "black", (6, col))
        board.place_piece(black_piece, (6, col))

    for col, piece_name in enumerate(back_rank):
        black_piece = PieceInstance(piece_definitions[piece_name], "black", (7, col))
        board.place_piece(black_piece, (7, col))
    
    board.current_player = "white"
    return board

def count_legal_moves_for_selected_piece(board:Board, player:str, selected_move:dict, possible_moves:list[dict]):
    selected_from_square = selected_move["from_square"]
    selected_piece = board.get_piece_at(selected_from_square)
    if selected_piece is None:
        return 0
    return sum (1 for candidate in possible_moves if candidate["from_square"] == selected_from_square)


def choose_random_move(board:Board, player:str):
    possible_moves = get_all_legal_moves_for_player(board, player)
    shield_events = []
    prevented_moves = set()
    while possible_moves:
        move = choose_smart_move(board, player, possible_moves)
        # piece = board.get_piece_at(move["from_square"])
        # if piece is not None and piece.name.lower() == "queen":
        #     print("\nQUEEN MOVE DEBUG")
        #     print("Player:", player)
        #     print("Internal from:", move["from_square"])
        #     print("Internal to:", move["to_square"])
        #     print("Piece position:", piece.position)
        #     print("Move type:", move["type"])
        #     print(board.print_game_board())
        legal_action_count = count_legal_moves_for_selected_piece(
            board=board,
            player=player,
            selected_move=move,
            possible_moves=possible_moves,
        )
        move_key = (
            move["type"],
            move["from_square"],
            move["to_square"],
        )
        if move_key in prevented_moves:
            possible_moves.remove(move)
            continue

        if move["type"] == "swap":
            return move, {"shield_events": shield_events, 
                "legal_action_count": legal_action_count,
                "prevented_actions": list(prevented_moves)}
        
        if move["type"] == "opponent_control_move":
            if opponent_control_move_leaves_king_in_check(board,move["from_square"],move["to_square"],player):
                possible_moves.remove(move)
                continue
            return move, {
                "shield_events": shield_events, 
                "legal_action_count": legal_action_count,
                "prevented_actions": list(prevented_moves)
            }
        
        from_square = move["from_square"]
        to_square = move["to_square"]
        type = move["type"]
        attacking_piece = board.get_piece_at(from_square)
        shield_result = get_shielded_capture_target(board, from_square, to_square)
        if shield_result is None:
            return move, {"shield_events":shield_events, 
                "legal_action_count": legal_action_count,
                "prevented_actions": list(prevented_moves)}
        shield_piece = shield_result
        shield_square = to_square
        target_piece = shield_piece
        shield_piece.shield_charges -= 1
        shield_events.append({
            "shield_piece": shield_piece.name,
            "shield_piece_id": shield_piece.definition.id,
            "shield_piece_instance_id": shield_piece.instance_id,
            "shield_square": shield_square,

            "protected_piece": target_piece.name,
            "protected_piece_id": target_piece.definition.id,
            "protected_square": to_square,
            "blocked_from_square": from_square,
            "blocked_to_square": to_square,

            # The rejected action.
            "blocked_move_type": move["type"],
            "blocked_from_square": from_square,
            "blocked_to_square": to_square,

            # The attacking piece.
            "attacking_piece": attacking_piece.name,
            "attacking_piece_id": attacking_piece.definition.id,
            "attacking_piece_instance_id": attacking_piece.instance_id,
            "attacking_piece_owner": attacking_piece.owner,

            # The piece whose shield was consumed.
            "shield_piece": shield_piece.name,
            "shield_piece_id": shield_piece.definition.id,
            "shield_piece_instance_id": shield_piece.instance_id,
            "shield_square": shield_piece.position,

            # Optional snapshot for later debugging.
            "shield_charges_remaining": shield_piece.shield_charges,
        })
        prevented_moves.add(move_key)
        possible_moves.remove(move)
    return None, None

def is_adjacent(square_a:tuple[int, int], square_b:tuple[int, int]):
    row_a, col_a = square_a
    row_b, col_b = square_b
    return max(abs(row_a - row_b), abs(col_a - col_b)) == 1

def get_shielded_capture_target(board: Board,from_square: tuple[int, int],to_square: tuple[int, int]):
    moving_piece = board.get_piece_at(from_square)

    if moving_piece is None:
        return None

    target_piece = board.get_piece_at(to_square)

    if target_piece is None:
        return None

    if target_piece.owner == moving_piece.owner:
        return None

    if "shield" not in target_piece.definition.traits:
        return None

    if target_piece.shield_charges <= 0:
        return None

    return target_piece

def find_available_shield_bearer_protecting(board:Board, protected_piece):
    for square, piece in board.squares.items():
        if piece.owner != protected_piece.owner:
            continue
        if "shield" not in piece.definition.traits:
            continue
        if piece.shield_charges <= 0:
            continue

        protects_self = ("protect_self" in piece.definition.traits and square == protected_piece.position)
        protects_adjacent = ("protect_adjacent" in piece.definition.traits and is_adjacent(square, protected_piece.position))
        
        if protects_self or protects_adjacent:
            return square, piece
    return None

def get_shield_block_for_move(board:Board, from_square:tuple[int, int], to_square:tuple[int, int]):
    moving_piece = board.get_piece_at(from_square)
    if moving_piece is None:
        return None
    target_piece = board.get_piece_at(to_square)
    if target_piece is None:
        return None
    if target_piece.owner == moving_piece.owner:
        return None
    return find_available_shield_bearer_protecting(board, target_piece)

def apply_capture_or_shield_block(board:Board, from_square:tuple[int, int], to_square:tuple[int, int]):
    moving_piece = board.get_piece_at(from_square)
    if moving_piece is None:
        raise ValueError(f"No piece at {from_square}")
    captured_piece = board.get_piece_at(to_square)
    if captured_piece is None:
        board.move_piece(from_square, to_square)
        return {
            "actual_to_square": to_square,
            "captured_piece": None,
            "shield_blocked": False,
            "shield_piece": None,
            "protected_piece": None,
        }
    if captured_piece.owner == moving_piece.owner:
        raise ValueError("Friendly capture attempted")
    shield_result = find_available_shield_bearer_protecting(board, captured_piece)
    if shield_result is not None:
        shield_square, shielding_piece = shield_result
        board.remove_piece(shield_square)

        return {
            "actual_to_square": from_square,
            "captured_piece": None,
            "shield_blocked": True,
            "shield_piece": shielding_piece,
            "protected_piece": captured_piece,
        }
    board.move_piece(from_square, to_square)
    return {
        "actual_to_square": to_square,
        "captured_piece": captured_piece,
        "shield_blocked": False,
        "shield_piece": None,
        "protected_piece": None,
    }

def simulate_random_game(piece_definitions:dict[str, PieceDefinition], max_turns:int=80, seed:int | None=None):
    if seed is not None:
        random.seed(seed)

    board = create_standard_board(piece_definitions)
    move_history = []

    for turn in range(max_turns):
        current_player = board.current_player
        enemy = get_enemy_player(current_player)
        
        if is_checkmate(board, current_player):
            return {
                "winner": enemy,
                "reason": "checkmate",
                "turns": turn,
                "move_history": move_history,
            }
        move, shield_context = choose_random_move(board, current_player)
        if move is None:
            return {
                "winner": None,
                "reason": "no legal moves",
                "turns": turn,
                "move_history": move_history,
            }
        
        from_square=move["from_square"]
        to_square = move["to_square"]
        moving_piece = board.get_piece_at(from_square)

        if moving_piece is None:
            raise RuntimeError(f"No piece at selected square {from_square}")
        if  move["type"] != "opponent_control_move" and moving_piece.owner != current_player:
            raise RuntimeError(
                f"Wrong player moved on turn {turn + 1}: "
                f"expected {current_player}, got {moving_piece.owner}"
            )
        legal_moves = get_legal_moves(board, moving_piece)
        if to_square not in legal_moves:
            raise RuntimeError(
                f"Illegal move chosen on turn {turn + 1}: "
                f"{current_player} {moving_piece.name} "
                f"{from_square} -> {to_square}. "
                f"Legal moves were: {legal_moves}"
            )
        
        captured_piece = board.get_piece_at(to_square)
        if captured_piece and captured_piece.owner == current_player:
            raise RuntimeError(
                f"Friendly capture attempted on turn {turn + 1}: "
                f"{current_player} {moving_piece.name} "
                f"{from_square} -> {to_square}"
            )
        piece = board.get_piece_at(move["from_square"])

        board.move_piece(from_square, to_square)
        validate_board_state(board)
        move_history.append({
            "turn": turn + 1,
            "player": current_player,
            "piece": moving_piece.name,
            "piece_id": moving_piece.definition.id,
            "from": from_square,
            "to": to_square,
            "captured": captured_piece.name if captured_piece else None,
            "captured_owner": captured_piece.owner if captured_piece else None,
            "enemy_in_check": is_in_check(board, enemy),
            "white_in_check": is_in_check(board, "white"),
            "black_in_check": is_in_check(board, "black"),
            "piece_count": len(board.squares),
        })
        if is_checkmate(board, enemy):
            return {
                "winner": current_player, 
                "reason": "checkmate",
                "turns": turn + 1,
                "move_history": move_history,
            }
        board.switch_turn()


    return {
        "winner":None, 
        "reason": "move limit", 
        "turns": max_turns,
        "move_history": move_history,
    }

def place_army_on_board(board:Board, army:Army, player:str):
    commoners = [piece for piece in army.commoners]
    nobles = [piece for piece in army.nobles]
    if player == "white":
        noble_row = 0
        commoner_row = 1
    elif player == "black":
        noble_row = 7
        commoner_row = 6
    else:
        raise ValueError(f"Invalid player: {player}")
    
    for col, piece_definition in enumerate(nobles):
        piece = PieceInstance(piece_definition, player, (noble_row, col))
        board.place_piece(piece, (noble_row, col))
    for col, piece_definition in enumerate(commoners):
        piece = PieceInstance(piece_definition, player, (commoner_row, col))
        board.place_piece(piece, (commoner_row, col))

def create_board_from_armies(white_army:Army, black_army:Army):
    white_valid, white_errors = validate_army(white_army)
    black_valid, black_errors = validate_army(black_army)

    if not white_valid:
        raise ValueError(f"White army is invalid: {white_errors}")
    if not black_valid:
        raise ValueError(f"Black army is invalid: {black_errors}")
    
    board = Board()
    place_army_on_board(board, white_army, "white")
    place_army_on_board(board, black_army, "black")

    assign_piece_instance_ids(board)
    validate_piece_instance_ids(board)

    board.current_player = "white"
    validate_board_state(board)
    return board

def validate_piece_instance_ids(board: Board):
    seen_ids: set[str] = set()

    for square, piece in board.squares.items():
        if not piece.instance_id:
            raise ValueError(
                f"{piece.owner} {piece.name} at {square} "
                "has no instance ID"
            )
        if piece.instance_id in seen_ids:
            raise ValueError(
                f"Duplicate piece instance ID: "
                f"{piece.instance_id}"
            )
        seen_ids.add(piece.instance_id)

def record_survivors(board: Board, record: GameRecord) -> None:
    record.surviving_piece_ids = [
        piece.definition.id
        for piece in board.squares.values()
    ]

    record.surviving_piece_instance_ids = [
        piece.instance_id
        for piece in board.squares.values()
    ]


def reaches_promotion_rank(piece, destination:tuple[int, int]):
    row, _ = destination
    if piece.owner == "white":
        return row ==7
    
    if piece.owner == "black":
        return row == 0
    
    return False

def can_promote_piece(piece):
    return piece.name in {"pawn", "squire", "shield bearer", "adept"}



def can_promote_to_piece(player:str, promotion_square:tuple[int, int], target_definition:PieceDefinition, starting_noble_lineup:dict[str, list[int]]):
    allowed_nobles = starting_noble_lineup.get(player, [])
    if target_definition.id not in allowed_nobles:
        return False
    if target_definition.name == "queen of air":
        return is_white_square(promotion_square)
    
    if target_definition.name == "queen of darkness":
        return is_black_square(promotion_square)
    
    return True

def get_valid_promotion_options(player: str,promotion_square: tuple[int, int],army: Army, starting_noble_lineup: dict[str, list[int]]):
    options = []
    seen_ids = set()

    for piece_definition in army.pieces:
        if piece_definition.id in seen_ids:
            continue
        if piece_definition.type.lower() not in {"noble", "both"}:
            continue

        if can_promote_to_piece(
            player=player,
            promotion_square=promotion_square,
            target_definition=piece_definition,
            starting_noble_lineup=starting_noble_lineup,
        ):
            options.append(piece_definition)
            seen_ids.add(piece_definition.id)
            

    return options

def choose_promotion_piece(valid_options:list[PieceDefinition]):
    by_name = {
        definition.name.lower(): definition for definition in valid_options
    }
    if "queen of air" in by_name:
        return by_name["queen of air"]
    if "queen of darkness" in by_name:
        return by_name["queen of darkness"]
    if "queen" in by_name:
        return by_name["queen"]
    if "the old queen" in by_name:
        old_queen_fallbacks = [
            "knight",
            "mule",
            "wild stallion",
            "pegasus"
        ]
        for piece_name in old_queen_fallbacks:
            if piece_name in by_name:
                return by_name[piece_name]
        random_nobles = [
            definition
            for definition in valid_options
            if (
                definition.type.lower() in {"noble", "both"}
                and definition.name.lower() != "king"
            )
        ]
        if random_nobles:
            return random.choice(random_nobles)

        return None

def is_no_promotion_piece(piece):
    return "no_promotion" in piece.definition.drawbacks

def handle_promotion(piece:PieceInstance, destination: tuple[int, int], army:Army, starting_noble_lineup: dict[str, list[int]]):
    if not reaches_promotion_rank(piece, destination):
        return None, None, None, None
    if is_no_promotion_piece(piece):
        return None, None, None, None
    if not can_promote_piece(piece):
        return None, None, None, None
        
    valid_options = get_valid_promotion_options(
        player=piece.owner,
        promotion_square=destination,
        army=army,
        starting_noble_lineup=starting_noble_lineup,
    )

    if not valid_options:
        return None, None, None, None

    ## TODO: If queen_spot is NOT the empress, promote to the queen_spot piece; otherwise promote to knight
    # promotion_piece = random.choice(valid_options)
    promotion_piece = choose_promotion_piece(valid_options)
    if promotion_piece is None:
        return None, None, None, None

    promoted_from = piece.name
    promoted_from_id = piece.definition.id

    piece.definition = promotion_piece

    return (
        promoted_from,
        promoted_from_id,
        promotion_piece.name,
        promotion_piece.id,
    )

def get_starting_noble_ids_from_army(army: Army):
    return [
        piece.id
        for piece in army.pieces
        if piece.type.lower() in {"noble", "both"}
    ]

def simulate_game_with_armies(white_army:Army, black_army:Army, max_turns:int=80, seed:int | None=None, match_number:int = 0):
    used_seed = time.time_ns()
    if seed is not None:
        used_seed = seed

    random.seed(used_seed)
    
    board = create_board_from_armies(white_army, black_army)
    # print(board.print_game_board(match_number+1))
    armies_by_player = {
        "white": white_army,
        "black": black_army
    }

    record = GameRecord()
    record.seed = used_seed
    record.starting_noble_lineup = {
        "white": get_starting_noble_ids_from_army(white_army),
        "black": get_starting_noble_ids_from_army(black_army),
    }
    record.starting_piece_ids = {
        "white": [
            piece.id
            for piece in white_army.pieces
        ],
        "black": [
            piece.id
            for piece in black_army.pieces
        ],
    }
    record.starting_piece_instances = {
        "white": [],
        "black": [],
    }
    for piece in board.squares.values():
        record.starting_piece_instances[piece.owner].append({
            "instance_id": piece.instance_id,
            "instance_number": piece.instance_number,
            "piece_id": piece.definition.id,
            "piece": piece.name,
            "owner": piece.owner,
            "starting_position": piece.starting_position,
            "piece_cost": piece.definition.cost,
        })

    current_player = "white"
    halfmove_clock = 0

    for turn in range(1, max_turns+1):
        current_player = board.current_player
        enemy = get_enemy_player(current_player)
        
        if is_checkmate(board, current_player):
            record.winner = enemy
            record.reason = "checkmate"
            record_survivors(board, record)
            return record
        
        move_result, move_context = choose_random_move(board, current_player)

        if move_result is None:
            if is_in_check(board, current_player):
                record.winner = other_player(current_player) 
                record.reason = "checkmate" 
                record_survivors(board, record)
                return record
            else:
                record.winner = None
                record.reason = "stalemate" 
                record_survivors(board, record)
                return record
        
        from_square = move_result["from_square"]
        to_square = move_result["to_square"]
        

        move_type = move_result["type"]
        shield_events = move_context["shield_events"]
        moving_piece = board.get_piece_at(from_square)
        if moving_piece is None:
            raise RuntimeError(
                f"No piece at selected from_square {from_square}. "
                f"Action was: {move_result}. "
                f"Current player: {current_player}."
            )

        if move_type != "opponent_control_move" and moving_piece.owner != current_player:
            raise RuntimeError(
                f"Wrong player moved: expected {current_player}, "
                f"got {moving_piece.owner}. Action was: {move_result}"
            )
        
        original_piece_name = moving_piece.name
        original_piece_id = moving_piece.definition.id
        original_piece_cost = moving_piece.definition.cost
        original_piece_instance_id = moving_piece.instance_id
        original_piece_instance_number = moving_piece.instance_number

        san_disambiguation = get_san_disambiguation(
            board=board,
            moving_piece=moving_piece,
            from_square=from_square,
            to_square=to_square,
        )
        swap_info = {
            "swap_used": False,
            "swapped_with": None,
            "swapped_with_id": None,
            "swapped_with_instance_id": None,
            "swapped_from_square": None,
            "swapped_to_square": None,
        }

        leap_info = {
            "leap_used": False,
            "leap_captured": None,
            "leap_captured_id": None,
            "leap_captured_cost": 0,
        }

        opponent_control_info = {
            "opponent_control_used": False,
            "controlled_piece": None,
            "controlled_piece_id": None,
            "controlled_piece_owner": None,
            "controlled_piece_instance_id": None,
            "controlled_piece_instance_number": None,
        }
        
        captured_piece = None
        captured_piece_instance_id = None
        captured_piece_instance_number = None

        if moving_piece is None:
            raise RuntimeError(f"No piece is at selected square {from_square}")
        if  move_type != "opponent_control_move" and  moving_piece.owner != current_player:
            raise RuntimeError(f"Wrong player moved: expected {current_player} but got {moving_piece.owner}.")
        
        if move_type == "swap":
            swap_info = execute_swap(board, from_square, to_square)
            validate_board_state(board)
        elif move_type == "leap":
            captured_piece = board.get_piece_at(to_square)
            if captured_piece is not None:
                captured_piece_instance_id = captured_piece.instance_id
                captured_piece_instance_number = (
                    captured_piece.instance_number
                )
            leap_info = execute_leap(board, from_square, to_square)
        elif move_type == "opponent_control_move":
            moving_piece = board.get_piece_at(from_square)
            if moving_piece is None:
                raise RuntimeError(f"No opponent controlled piece at {from_square}. Action was = {move_result}")
            opponent_control_info = execute_opponent_control_move(
                board,
                from_square,
                to_square,
                controller=current_player,
            )
            
        else:
            legal_moves = get_legal_moves(board, moving_piece)
            if to_square not in legal_moves:
                raise RuntimeError(f"Illegal move chosen: {current_player} {moving_piece.name}: {from_square}->{to_square}. Legal moves: {legal_moves}")
            
            captured_piece = board.get_piece_at(to_square)
            if captured_piece is not None:
                captured_piece_instance_id = captured_piece.instance_id
                captured_piece_instance_number = (
                    captured_piece.instance_number
                )

            if captured_piece and captured_piece.owner == current_player:
                raise RuntimeError("Friendly capture attempted.")
            
            
            board.move_piece(from_square, to_square)
        validate_board_state(board)
        halfmove_clock = next_halfmove_clock(halfmove_clock, moving_piece, captured_piece)

        promoted_from = None
        promoted_from_id = None
        promoted_to = None
        promoted_to_id = None

        if move_type == "move":
            promotion_result = handle_promotion(
                piece=moving_piece,
                destination=to_square,
                army=armies_by_player[current_player],
                starting_noble_lineup=record.starting_noble_lineup,
            )
            (
                promoted_from,
                promoted_from_id,
                promoted_to,
                promoted_to_id,
            ) = promotion_result

        validate_board_state(board)
        if is_in_check(board, current_player):
            raise RuntimeError(
                f"{current_player} ended their own turn in check. "
                f"Action: {move_result}. "
                f"From: {from_square}. "
                f"To: {to_square}. "
                f"Piece: {original_piece_name}. "
                f"Swap used: {swap_info['swap_used']}. "
                f"Captured: {captured_piece.name if captured_piece else None}. "
                f"Shield events: {shield_events}."
            )
        enemy_in_check = is_in_check(board, enemy)
        enemy_checkmated = is_checkmate(board, enemy)

        move_record = MoveRecord(
            turn=turn ,
            player=current_player,
            piece=original_piece_name,
            piece_id=original_piece_id,
            piece_cost=original_piece_cost,
            piece_instance_id=original_piece_instance_id,
            piece_instance_number=original_piece_instance_number,
            from_square=from_square,
            to_square=to_square,
            captured=captured_piece.name if captured_piece else None,
            captured_piece_id=(
                captured_piece.definition.id
                if captured_piece
                else None
            ),
            captured_piece_cost=(
                captured_piece.definition.cost
                if captured_piece
                else 0
            ),
            captured_piece_instance_id=captured_piece_instance_id,
            captured_piece_instance_number=captured_piece_instance_number,
            created_check=enemy_in_check,
            created_checkmate=enemy_checkmated,
            legal_move_count= move_context["legal_action_count"],
            promoted_from=promoted_from,
            promoted_from_id=promoted_from_id,
            promoted_to=promoted_to,
            promoted_to_id=promoted_to_id,
            shield_blocks_used=len(shield_events),
            shield_events=shield_events,
            swap_used=swap_info["swap_used"],
            swapped_with=swap_info["swapped_with"],
            swapped_with_id=swap_info["swapped_with_id"],
            swapped_with_instance_id=swap_info[
                "swapped_with_instance_id"
            ],
            swapped_from_square=swap_info["swapped_from_square"],
            swapped_to_square=swap_info["swapped_to_square"],
            leap_used=leap_info["leap_used"],
            leap_captured=leap_info["leap_captured"],
            leap_captured_id=leap_info["leap_captured_id"],
            leap_captured_cost=leap_info["leap_captured_cost"],
            opponent_control_used=opponent_control_info["opponent_control_used"],
            controlled_piece=opponent_control_info["controlled_piece"],
            controlled_piece_id=opponent_control_info["controlled_piece_id"],
            controlled_piece_owner=opponent_control_info["controlled_piece_owner"],
            controlled_piece_instance_id=opponent_control_info[
                "controlled_piece_instance_id"
            ],
            controlled_piece_instance_number=opponent_control_info[
                "controlled_piece_instance_number"
            ],
            san_disambiguation=san_disambiguation,

        )
        record.log_move(move_record)

        if enemy_checkmated:
            record.winner=current_player
            record.reason = "checkmate"
            record_survivors(board, record)
            return record
        if is_stalemate(board, other_player(current_player)):
            record.winner=None
            record.reason = "stalemate"
            record_survivors(board, record)
            return record
        if halfmove_clock >= 150:
            record.winner=None
            record.reason = "seventy_five_move_rule"
            record_survivors(board, record)
            return record
         
        board.switch_turn()   
    record.winner = None
    record.reason = "move limit"
    record_survivors(board, record)
    return record

def next_halfmove_clock(halfmove_clock:int, moving_piece:PieceInstance, captured_piece:PieceInstance | None):
    if captured_piece is not None:
        return 0
    if not moving_piece.is_noble:
        return 0
    else:
        return halfmove_clock + 1
    
def simulate_matchup(white_army:Army, black_army:Army, games_per_matchup:int=10, max_turns:int=80, seed:int | None=None):
    records = []
    for game_index in range(games_per_matchup):
        game_seed = None
        if seed is not None:
            game_seed = seed + game_index
        record = simulate_game_with_armies(white_army, black_army, max_turns, game_seed)
        records.append(record)
    return records

def summarize_matchup(records:list[GameRecord]):
    white_wins = sum(1 for record in records if record.winner == "white")
    black_wins = sum(1 for record in records if record.winner == "black")
    draws = sum(1 for record in records if record.winner is None)

    total_captures = sum(len(record.captures) for record in records)
    total_checks = sum(len(record.checks) for record in records)
    total_checkmates = sum(len(record.checkmates) for record in records)
    total_moves = sum(record.total_moves for record in records)
    total_promotions = sum(len(record.promotions) for record in records)
    total_shield_blocks = sum(
        move.shield_blocks_used
        for record in records
        for move in record.move_history
    )
    total_swaps = sum(len(record.swaps) for record in records)
    total_leaps = sum(len(record.leaps) for record in records)
    total_opponent_control_moves = sum(
        len(record.opponent_control_moves)
        for record in records
    )
    return {
        "games": len(records),
        "white_wins": white_wins,
        "black_wins": black_wins,
        "draws": draws,
        "total_moves": total_moves,
        "average_moves": total_moves / len(records) if records else 0,
        "total_captures": total_captures,
        "total_checks": total_checks,
        "total_checkmates": total_checkmates,
        "total_promotions": total_promotions,
        "total_shield_blocks": total_shield_blocks,
        "total_swaps": total_swaps,
        "total_leaps": total_leaps,
        "total_opponent_control_moves": total_opponent_control_moves,
    }
def is_stalemate(
        board: Board,
        player: str,
    ) -> bool:
        if is_in_check(board, player):
            return False

        for piece in board.squares.values():
            if piece.owner != player:
                continue

            if piece.is_captured:
                continue

            legal_moves = get_legal_moves(
                board,
                piece,
            )

            if legal_moves:
                return False

        return True
