from enum import Enum


class Color(Enum):
    """
    Enum care reprezinta culoarea unei piese de sah.

    WHITE  - piesele albe
    BLACK  - piesele negre
    """
    WHITE = "white"
    BLACK = "black"


class PieceType(Enum):
    """
    Enum care defineste tipurile de piese din sah.

    KING   - Rege
    QUEEN  - Regina
    ROOK   - Tura
    BISHOP - Nebun
    KNIGHT - Cal
    PAWN   - Pion
    """
    KING = "K"
    QUEEN = "Q"
    ROOK = "R"
    BISHOP = "B"
    KNIGHT = "N"
    PAWN = "P"


class Piece:
    """
    Clasa care reprezinta o piesa de sah.

    Fiecare piesa are:
    - un tip (PieceType)
    - o culoare (Color)
    """

    def __init__(self, piece_type: PieceType, color: Color):
        """
        Creeaza o piesa de sah.

        :param piece_type: tipul piesei (rege, regina, etc)
        :param color: culoarea piesei (alb sau negru)
        """
        self.piece_type = piece_type
        self.color = color

    @property
    def symbol(self) -> str:
        """
        Returneaza simbolul piesei pentru afisare.

        - litera mare pentru piesele albe
        - litera mica pentru piesele negre

        Exemple:
        - Rege alb   -> 'K'
        - Regina neagra -> 'q'
        """
        return self.piece_type.value.upper() if self.color == Color.WHITE else self.piece_type.value.lower()
