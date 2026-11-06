from dataclasses import dataclass, field
from statistics import median
from src.game_record import GameRecord
from src.models import PieceDefinition

CHECK_VALUE = 3
CHECKMATE_VALUE = 5
SURVIVAL_RATE = 0.5
ADJUSTMENT_RATE = 0.25
MINIMUM_COST = 10
PROMOTION_VALUE = 0
SHIELD_BLOCK_VALUE = 5
SWAP_VALUE = 3

@dataclass
class PieceStats:
    piece_id:int
    name:str
    current_cost:int
    games_seen:int = 0
    moves: int=0
    total_legal_moves: int=0
    capture_value:int =0
    checks_created: int=0
    checkmates_created: int=0
    survivals:int=0
    total_value:float=0.0
    promotions: int = 0
    shield_blocks: int = 0
    swaps_used: int = 0

    def average_mobility(self):
        if self.moves == 0:
            return 0.0
        return self.total_legal_moves / self.moves
    def average_value(self):
        if self.games_seen==0:
            return 0.0
        return self.total_value / self.games_seen
    def efficiency(self):
        if self.current_cost <= 0:
            return None
        return self.average_value() / self.current_cost

def initialize_piece_stats(piece_definitions:dict[str, PieceDefinition]):
    stats = {}
    for piece in piece_definitions.values():
        stats[piece.id] = PieceStats(piece.id, piece.name, piece.cost)
    return stats

def calculate_total_values(stats:dict[int, PieceStats]):
    for piece_stat in stats.values():
        survival_value = piece_stat.survivals * piece_stat.current_cost * SURVIVAL_RATE
        check_value = piece_stat.checks_created * CHECK_VALUE
        checkmate_value = piece_stat.checkmates_created * CHECKMATE_VALUE
        mobility_value = piece_stat.average_mobility()
        promotion_value = piece_stat.promotions * PROMOTION_VALUE
        shield_value = piece_stat.shield_blocks * SHIELD_BLOCK_VALUE
        swap_value = piece_stat.swaps_used * SWAP_VALUE
        piece_stat.total_value = (
            piece_stat.capture_value 
            + survival_value 
            + check_value 
            + checkmate_value 
            + mobility_value
            + promotion_value
            + shield_value
            + swap_value
        )

def collect_piece_stats(records:list[GameRecord], piece_definitions:dict[str, PieceDefinition]):
    stats = initialize_piece_stats(piece_definitions)
    for record in records:
        piece_ids_seen_this_game = set()
        for move in record.move_history:
            piece_stat = stats[move.piece_id]
            piece_ids_seen_this_game.add(move.piece_id)
            piece_stat.moves+=1
            piece_stat.total_legal_moves += move.legal_move_count
            piece_stat.capture_value += move.captured_piece_cost
            if move.created_check:
                piece_stat.checks_created+=1
            if move.created_checkmate:
                piece_stat.checkmates_created+=1
            if move.promoted_to is not None:
                piece_stat.promotions += 1
            for shield_event in move.shield_events:
                shield_piece_id = shield_event["shield_piece_id"]
                if shield_piece_id in stats:
                    stats[shield_piece_id].shield_blocks += 1
            if move.swap_used:
                piece_stat.swaps_used += 1
        for piece_id in record.surviving_piece_ids:
            if piece_id in stats:
                stats[piece_id].survivals += 1
                piece_ids_seen_this_game.add(piece_id)
        for piece_id in piece_ids_seen_this_game:
            stats[piece_id].games_seen +=1
    calculate_total_values(stats)
    return stats

def calculate_average_efficiency(stats:dict[int, PieceStats]):
    efficiencies = [piece_stat.efficiency() for piece_stat in stats.values() if piece_stat.efficiency() is not None]
    if not efficiencies:
        return 0.0
    return sum(efficiencies) / len(efficiencies)

def round_cost(cost:float):
    rounded = int(round(cost/5)*5)
    if rounded < MINIMUM_COST:
        return MINIMUM_COST
    return rounded

def suggest_new_costs(stats:dict[int, PieceStats], adjustment_rate:float = ADJUSTMENT_RATE):
    average_efficiency = calculate_average_efficiency(stats)
    new_costs = {}

    for piece_id, piece_stat in stats.items():
        efficiency = piece_stat.efficiency()
        if efficiency is None:
            new_costs[piece_id] = piece_stat.current_cost
            continue
        if average_efficiency == 0:
            new_costs[piece_id] = piece_stat.current_cost
            continue

        suggested_cost = (piece_stat.current_cost * efficiency / average_efficiency)
        adjusted_cost = (piece_stat.current_cost + adjustment_rate * (suggested_cost - piece_stat.current_cost))
        new_costs[piece_id] = round_cost(adjusted_cost)
    return new_costs

def build_balance_report(stats:dict[int, PieceStats], new_costs:dict[int, int]):
    report = []
    average_efficiency = calculate_average_efficiency(stats)

    for piece_stat in stats.values():
        efficiency = piece_stat.efficiency()
        if efficiency is None:
            efficiency_status = "fixed"
        elif efficiency > average_efficiency * 1.2:
            efficiency_status = "overperforming"
        elif efficiency < average_efficiency * 0.8:
            efficiency_status = "underperforming"
        else:
            efficiency_status = "normal"
        report.append({
            "piece_id": piece_stat.piece_id,
            "name": piece_stat.name,
            "current_cost": piece_stat.current_cost,
            "average_value": piece_stat.average_value(),
            "efficiency": efficiency,
            "new_cost": new_costs[piece_stat.piece_id],
            "moves": piece_stat.moves,
            "promotions": piece_stat.promotions,
            "captures_value": piece_stat.capture_value,
            "checks": piece_stat.checks_created,
            "checkmates": piece_stat.checkmates_created,
            "survivals": piece_stat.survivals,
            "average_mobility": piece_stat.average_mobility(),
            "status": efficiency_status,
            "shield_blocks": piece_stat.shield_blocks,
            "swaps_used": piece_stat.swaps_used,
        })

    return report

def build_piece_instance_match_report(records:list[GameRecord]):
    if not records:
        return []

    starting_instances: dict[str, dict] = {}

    for record in records:
        for instances in record.starting_piece_instances.values():
            for instance in instances:
                starting_instances[
                    instance["instance_id"]
                ] = instance

    report = []
    game_count = len(records)

    white_wins = sum(
        record.winner == "white"
        for record in records
    )

    draws = sum(
        record.winner is None
        for record in records
    )
    black_wins = sum(
        record.winner == "black"
        for record in records
    )

    for instance_id, instance in sorted(
        starting_instances.items()
    ):
        moves_by_game = []
        captures_by_game = []
        captured_cost_by_game = []
        shields_by_game = []
        swaps_by_game = []
        opponent_controlled_by_game = []
        checks_by_game = []
        legal_moves_by_game = []
        survived_by_game = []

        for record in records:
            instance_moves = [
                move
                for move in record.move_history
                if move.piece_instance_id == instance_id
            ]

            moves_by_game.append(len(instance_moves))

            captures_by_game.append(
                sum(
                    move.captured_piece_instance_id is not None
                    for move in instance_moves
                )
            )

            captured_cost_by_game.append(
                sum(
                    move.captured_piece_cost
                    for move in instance_moves
                )
            )

            shields_by_game.append(
                sum(
                    1
                    for move in record.move_history
                    for event in move.shield_events
                    if event.get(
                        "shield_piece_instance_id"
                    ) == instance_id
                )
            )

            swaps_by_game.append(
                sum(
                    move.swap_used
                    for move in instance_moves
                )
            )

            opponent_controlled_by_game.append(
                sum(
                    move.opponent_control_used
                    and move.controlled_piece_instance_id
                    == instance_id
                    for move in record.move_history
                )
            )

            checks_by_game.append(
                sum(
                    move.created_check
                    or move.created_checkmate
                    for move in instance_moves
                )
            )

            legal_counts = [
                move.legal_move_count
                for move in instance_moves
            ]

            legal_moves_by_game.append(
                median(legal_counts)
                if legal_counts
                else 0
            )
            survived_by_game.append(
                int(
                    instance_id
                    in record.surviving_piece_instance_ids
                )
            )

        report.append({
            "piece_instance_id": instance_id,
            "owner": instance["owner"],
            "piece": instance["piece"],
            "piece_id": instance["piece_id"],
            "piece_cost": instance["piece_cost"],
            "starting_position": instance["starting_position"],
            "games": game_count,
            "moves_per_game": (
                sum(moves_by_game) / game_count
            ),

            "number_of_wins_white": white_wins,
            "number_of_wins_black": black_wins,
            "number_of_draws": draws,

            "median_pieces_captured": median(
                captures_by_game
            ),

            "median_piece_cost_captured": median(
                captured_cost_by_game
            ),

            "median_number_of_shields_used": median(
                shields_by_game
            ),

            "median_number_of_swaps": median(
                swaps_by_game
            ),

            "median_number_of_opponent_controlled": median(
                opponent_controlled_by_game
            ),

            "median_number_of_times_used": median(
                moves_by_game
            ),

            "median_number_of_times_used_to_check_or_checkmate":
                median(checks_by_game),

            "median_number_of_legal_moves": median(
                legal_moves_by_game
            ),
            "survival_rate": (
                sum(survived_by_game) / game_count
            ),
        })

    return report

def build_piece_match_report(
    records: list[GameRecord],
    piece_definitions: dict[str, PieceDefinition],
) :
    
    if not records:
        return []

    definitions_by_id = {
        definition.id: definition
        for definition in piece_definitions.values()
    }

    participating_piece_ids: set[int] = set()

    for record in records:
        for piece_ids in record.starting_piece_ids.values():
            participating_piece_ids.update(piece_ids)

        for move in record.move_history:
            participating_piece_ids.add(move.piece_id)

    game_count = len(records)

    white_wins = sum(
        record.winner == "white"
        for record in records
    )

    black_wins = sum(
        record.winner == "black"
        for record in records
    )

    draws = sum(
        record.winner is None
        for record in records
    )

    report = []

    for piece_id in sorted(participating_piece_ids):
        definition = definitions_by_id.get(piece_id)

        if definition is None:
            continue

        moves_by_game = []
        captures_by_game = []
        captured_cost_by_game = []
        shields_by_game = []
        swaps_by_game = []
        opponent_controlled_by_game = []
        checks_by_game = []
        legal_moves_by_game = []

        for record in records:
            piece_moves = [
                move
                for move in record.move_history
                if move.piece_id == piece_id
            ]

            moves_by_game.append(
                len(piece_moves)
            )

            captures_by_game.append(
                sum(
                    move.captured_piece_instance_id is not None
                    for move in piece_moves
                )
            )

            captured_cost_by_game.append(
                sum(
                    move.captured_piece_cost
                    for move in piece_moves
                )
            )

            shields_by_game.append(
                sum(
                    1
                    for move in record.move_history
                    for event in move.shield_events
                    if event.get("shield_piece_id") == piece_id
                )
            )

            swaps_by_game.append(
                sum(
                    1
                    for move in piece_moves
                    if move.swap_used
                )
            )

            opponent_controlled_by_game.append(
                sum(
                    1
                    for move in record.move_history
                    if (
                        move.opponent_control_used
                        and move.controlled_piece_id == piece_id
                    )
                )
            )

            checks_by_game.append(
                sum(
                    1
                    for move in piece_moves
                    if (
                        move.created_check
                        or move.created_checkmate
                    )
                )
            )

            legal_counts = [
                move.legal_move_count
                for move in piece_moves
            ]

            legal_moves_by_game.append(
                median(legal_counts)
                if legal_counts
                else 0
            )

        report.append({
            "piece_id": piece_id,
            "piece": definition.name,
            "piece_cost": definition.cost,
            "games": game_count,

            "number_of_wins_white": white_wins,
            "number_of_wins_black": black_wins,
            "number_of_draws": draws,

            "moves_per_game": (
                sum(moves_by_game) / game_count
            ),

            "median_pieces_captured": median(
                captures_by_game
            ),

            "median_piece_cost_captured": median(
                captured_cost_by_game
            ),

            "median_number_of_shields_used": median(
                shields_by_game
            ),

            "median_number_of_swaps": median(
                swaps_by_game
            ),

            "median_number_of_opponent_controlled": median(
                opponent_controlled_by_game
            ),

            "median_number_of_times_used": median(
                moves_by_game
            ),

            "median_number_of_times_used_to_check_or_checkmate":
                median(checks_by_game),

            "median_number_of_legal_moves": median(
                legal_moves_by_game
            ),
        })

    return report