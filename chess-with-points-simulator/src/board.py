from src.models import PieceInstance, Square

class Board:
    def __init__(self):
        self.squares: dict[Square, PieceInstance] = {}
        self.current_player: str = "white"
        self.move_number: int=0
        self.last_moved_piece_by_owner: dict[str, str | None] = {
            "white": None,
            "black": None,
        }

    def is_square_on_board(self, square:Square):
        row, col = square
        return 0 <= row <= 7 and 0 <= col <= 7
    
    def get_piece_at(self, square:Square):
        return self.squares.get(square)
        
    def is_square_empty(self, square:Square):
        return self.get_piece_at(square) is None
    
    def place_piece(self, piece:PieceInstance, square:Square):
        if not self.is_square_on_board(square):
            raise ValueError(f"Square {square} is not a valid square on the board.")
        
        if not self.is_square_empty(square):
            raise ValueError(f"Square {square} is already ocupied")
        
        piece.position = square
        self.squares[square] = piece

    def remove_piece(self, square:Square):
        return self.squares.pop(square, None)
    
    def move_piece(self, from_square:Square, to_square:Square):
        if not self.is_square_on_board(to_square):
            raise ValueError(f"square {to_square} is not on the board.")
        
        piece = self.get_piece_at(from_square)
        piece.position = to_square
        piece.has_moved = True
        piece.stats.moves += 1
        
        if piece is None:
            raise ValueError(f"No piece is on {from_square}")
        
        captured_piece = self.get_piece_at(to_square)
        if captured_piece and captured_piece.owner == piece.owner:
            raise ValueError(f"Ya can't capture your own piece {captured_piece.name} using {piece.name}")
        
        self.remove_piece(from_square)

        if captured_piece:
            self.remove_piece(to_square)

        piece.position = to_square
        piece.has_moved = True
        self.squares[to_square] = piece
        self.last_moved_piece_by_owner[self.current_player] = piece.instance_id
        return captured_piece
    
    def get_current_player_last_piece(self):
        return self.last_moved_piece_by_owner[self.current_player]
    
    def switch_turn(self):
        self.current_player = "black" if self.current_player == "white" else "white"
        self.move_number += 1

    @staticmethod
    def piece_symbol(piece_name: str) -> str:
        symbols = {
            "king": "K",
            "queen": "Q",
            "rook": "R",
            "bishop": "B",
            "knight": "N",
            "pawn": "P",

            # Custom pieces.
            "squire": "Sq",
            "shield bearer": "SB",
            "peasant": "Pe",
            "adept": "A",
            "mule": "M",
            "wild stallion": "WS",
            "clergy riders": "CR",
            "lance rider": "LR",
            "pegasus": "Pg",
            "high priest": "HP",
            "corrupted abbot": "CA",
            "arcane priest": "AP",
            "damaged chariot": "DC",
            "fast chariot": "FC",
            "armored chariot": "AC",
            "arcane tower": "AT",
            "sorceress": "S",
            "joan of arc": "JA",
            "queen of air": "QA",
            "queen of darkness": "QD",
            "the old queen": "OQ",
        }

        piece_name = piece_name.lower()
        return symbols.get(piece_name, piece_name[:2].upper())
    
    def get_piece_display(self, piece: PieceInstance) -> str:
        piece_name = piece.name.lower()
        owner = piece.owner.lower()

        symbol = self.piece_symbol(piece_name)

        if owner == "black":
            symbol = symbol.lower()

        return symbol

    def print_game_board(self, match_number:int=0):
        lines = [
            "",
            "=" * 45,
            f"GAME BOARD for Match {match_number}",
            "=" * 45,
            "",
            f"Current Player: {self.current_player.title()}",
            f"Move Number   : {self.move_number}",
            "",
            "                  BLACK",
            "",
            "       a    b    c    d    e    f    g    h",
            "    +----+----+----+----+----+----+----+----+",
        ]
        # Row 7 is rank 8, and row 0 is rank 1.
        for row in range(7, -1, -1):
            rank = row + 1
            cells = []

            for col in range(8):
                piece = self.get_piece_at((row, col))

                if piece is None:
                    symbol = ""
                else:
                    symbol = self.get_piece_display(piece)

                cells.append(f"{symbol:^4}")

            row_contents = "|".join(cells)

            lines.append(f" {rank}  |{row_contents}|  {rank}")
            lines.append(
                "    +----+----+----+----+----+----+----+----+"
            )

        lines.extend([
            "       a    b    c    d    e    f    g    h",
            "",
            "                  WHITE",
            "",
        ])

        return "\n".join(lines)
    
    def print_starting_game_board(self):
        lines = [
            "",
            "=" * 45,
            f"                 GAME BOARD",
            "=" * 45,
            "",
            "                  BLACK",
            "",
            "       a    b    c    d    e    f    g    h",
            "    +----+----+----+----+----+----+----+----+",
        ]
        # Row 7 is rank 8, and row 0 is rank 1.
        for row in range(7, -1, -1):
            rank = row + 1
            cells = []

            for col in range(8):
                piece = self.get_piece_at((row, col))

                if piece is None:
                    symbol = ""
                else:
                    symbol = self.get_piece_display(piece)

                cells.append(f"{symbol:^4}")

            row_contents = "|".join(cells)

            lines.append(f" {rank}  |{row_contents}|  {rank}")
            lines.append(
                "    +----+----+----+----+----+----+----+----+"
            )

        lines.extend([
            "       a    b    c    d    e    f    g    h",
            "",
            "                  WHITE",
            "",
        ])

        return "\n".join(lines)