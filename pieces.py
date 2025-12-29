from enum import Enum

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class PieceType(Enum):
    KING = "K"
    QUEEN = "Q"
    ROOK = "R"
    BISHOP = "B"
    KNIGHT = "N"
    PAWN = "P"

class Piece:
    def __init__(self, piece_type: PieceType, color: Color):
        self.piece_type = piece_type
        self.color = color

    @property
    def symbol(self) -> str:
        return (
            self.piece_type.value.upper()
            if self.color == Color.WHITE
            else self.piece_type.value.lower()
        )
