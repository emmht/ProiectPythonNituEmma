from board import Board
from pieces import Color

class Move:
    def __init__(self, from_pos, to_pos, piece, captured=None):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.piece = piece
        self.captured = captured

    def __repr__(self):
        return f"{self.piece.symbol}: {self.from_pos} -> {self.to_pos}"


class ChessGame:
    def __init__(self):
        self.board = Board()
        self.current_player = Color.WHITE
        self.history: list[Move] = []

    @staticmethod
    def algebraic_to_coords(square: str):
        file = square[0].lower()  # litera
        rank = int(square[1])     # cifra

        col = ord(file) - ord('a')
        row = rank - 1
        return row, col

    def move(self, from_square: str, to_square: str):
        from_row, from_col = self.algebraic_to_coords(from_square)
        to_row, to_col = self.algebraic_to_coords(to_square)

        piece = self.board.get_piece(from_row, from_col)
        if piece is None:
            raise ValueError("Nu există piesă pe pătratul de start.")

        if piece.color != self.current_player:
            raise ValueError("Nu e rândul acestei culori.")

        dest_piece = self.board.get_piece(to_row, to_col)

        self.board.move_piece(from_row, from_col, to_row, to_col)

        if self.is_in_check(self.current_player):
            self.board.set_piece(from_row, from_col, piece)
            self.board.set_piece(to_row, to_col, dest_piece)
            raise ValueError("Mutare ilegală: regele ar rămâne în șah.")

        move = Move(from_square, to_square, piece, captured=dest_piece)
        self.history.append(move)

        opponent = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        in_check = self.is_in_check(opponent)

        self.current_player = opponent

        return in_check



    def is_in_check(self, color: Color) -> bool:
        king_row, king_col = self.board.find_king(color)
        enemy_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.board.is_square_attacked(king_row, king_col, enemy_color)

