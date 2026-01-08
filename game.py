from board import Board
from pieces import Color, PieceType, Piece


class Move:
    """
    Reprezinta o mutare efectuata in joc.

    Contine informatii despre:
    - pozitia initiala
    - pozitia finala
    - piesa mutata
    - piesa capturata (daca exista)
    - promovare
    - en passant
    - castling
    """

    def __init__(self, from_pos, to_pos, piece, captured=None, promotion=None, en_passant=False, castling=False):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.piece = piece
        self.captured = captured
        self.promotion = promotion
        self.en_passant = en_passant
        self.castling = castling

    def __repr__(self):
        """
        Returneaza o reprezentare text a mutarii,
        folosita pentru debug si istoric.
        """
        extra = ""
        if self.promotion:
            extra += f"={self.promotion}"
        if self.en_passant:
            extra += " ep"
        if self.castling:
            extra += " castle"
        return f"{self.piece.symbol}: {self.from_pos} -> {self.to_pos}{extra}"


class ChessGame:
    """
    Clasa principala care gestioneaza logica jocului de sah.

    Se ocupa de:
    - tabla de joc
    - jucatorul curent
    - mutari legale
    - reguli speciale
    - check, checkmate, stalemate
    - istoric mutari
    """

    def __init__(self):
        """
        Initializeaza un joc nou de sah.
        """
        self.board = Board()
        self.current_player = Color.WHITE
        self.history = []
        self.en_passant_target = None
        self.castle_rights = {
            Color.WHITE: {"K": True, "Q": True},
            Color.BLACK: {"K": True, "Q": True},
        }

    @staticmethod
    def algebraic_to_coords(square: str):
        """
        Converteste o pozitie algebraica (ex: e2)
        in coordonate interne (row, col).
        """
        file = square[0].lower()
        rank = int(square[1])
        col = ord(file) - ord("a")
        row = rank - 1
        return row, col

    @staticmethod
    def coords_to_algebraic(row: int, col: int):
        """
        Converteste coordonatele interne (row, col)
        in notatie algebraica (ex: e2).
        """
        file = chr(ord("a") + col)
        rank = str(row + 1)
        return file + rank

    def is_in_check(self, color: Color) -> bool:
        """
        Verifica daca regele unei culori este in sah.
        """
        king_row, king_col = self.board.find_king(color)
        enemy = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.board.is_square_attacked(king_row, king_col, enemy)

    def _starting_rook_square(self, color: Color, side: str):
        """
        Returneaza pozitia initiala a turei pentru castling.
        """
        if color == Color.WHITE:
            return (0, 7) if side == "K" else (0, 0)
        return (7, 7) if side == "K" else (7, 0)

    def _starting_king_square(self, color: Color):
        """
        Returneaza pozitia initiala a regelui.
        """
        return (0, 4) if color == Color.WHITE else (7, 4)

    def _castling_moves_for(self, color: Color):
        """
        Genereaza mutarile de castling posibile pentru o culoare.
        """
        moves = []
        king_row, king_col = self._starting_king_square(color)
        king = self.board.get_piece(king_row, king_col)
        if king is None or king.piece_type != PieceType.KING or king.color != color:
            return moves

        enemy = Color.BLACK if color == Color.WHITE else Color.WHITE

        if self.is_in_check(color):
            return moves

        if self.castle_rights[color]["K"]:
            rook_row, rook_col = self._starting_rook_square(color, "K")
            rook = self.board.get_piece(rook_row, rook_col)
            if rook and rook.piece_type == PieceType.ROOK and rook.color == color:
                if self.board.is_empty(king_row, 5) and self.board.is_empty(king_row, 6):
                    if (not self.board.is_square_attacked(king_row, 5, enemy)) and (not self.board.is_square_attacked(king_row, 6, enemy)):
                        moves.append(((king_row, king_col), (king_row, 6), (rook_row, rook_col), (king_row, 5)))

        if self.castle_rights[color]["Q"]:
            rook_row, rook_col = self._starting_rook_square(color, "Q")
            rook = self.board.get_piece(rook_row, rook_col)
            if rook and rook.piece_type == PieceType.ROOK and rook.color == color:
                if self.board.is_empty(king_row, 3) and self.board.is_empty(king_row, 2) and self.board.is_empty(king_row, 1):
                    if (not self.board.is_square_attacked(king_row, 3, enemy)) and (not self.board.is_square_attacked(king_row, 2, enemy)):
                        moves.append(((king_row, king_col), (king_row, 2), (rook_row, rook_col), (king_row, 3)))
        return moves

    def _promotion_from_token(self, token: str):
        """
        Converteste litera de promovare intr-un PieceType.
        """
        if token is None:
            return None
        t = token.lower()
        if t == "q":
            return PieceType.QUEEN
        if t == "r":
            return PieceType.ROOK
        if t == "b":
            return PieceType.BISHOP
        if t == "n":
            return PieceType.KNIGHT
        return None

    def _parse_to_square(self, to_square: str):
        """
        Parseaza destinatia mutarii si extrage promovarea daca exista.
        """
        if len(to_square) == 2:
            return to_square, None
        if len(to_square) == 3:
            return to_square[:2], self._promotion_from_token(to_square[2])
        raise ValueError("Invalid destination format")

    def _en_passant_moves_for_pawn(self, from_row, from_col, color: Color):
        """
        Genereaza mutarile en passant pentru un pion.
        """
        if self.en_passant_target is None:
            return []
        tr, tc = self.en_passant_target
        direction = 1 if color == Color.WHITE else -1
        if tr != from_row + direction:
            return []
        if abs(tc - from_col) != 1:
            return []
        if not self.board.is_empty(tr, tc):
            return []
        return [(tr, tc)]

    def get_status_for(self, color: Color):
        """
        Returneaza starea jocului pentru o culoare:
        normal, check, checkmate sau stalemate.
        """
        if self.is_checkmate(color):
            return "checkmate"
        if self.is_stalemate(color):
            return "stalemate"
        if self.is_in_check(color):
            return "check"
        return "normal"
