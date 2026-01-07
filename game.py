from board import Board
from pieces import Color, PieceType, Piece


class Move:
    def __init__(self, from_pos, to_pos, piece, captured=None, promotion=None, en_passant=False, castling=False):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.piece = piece
        self.captured = captured
        self.promotion = promotion
        self.en_passant = en_passant
        self.castling = castling

    def __repr__(self):
        extra = ""
        if self.promotion:
            extra += f"={self.promotion}"
        if self.en_passant:
            extra += " ep"
        if self.castling:
            extra += " castle"
        return f"{self.piece.symbol}: {self.from_pos} -> {self.to_pos}{extra}"


class ChessGame:
    def __init__(self):
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
        file = square[0].lower()
        rank = int(square[1])
        col = ord(file) - ord("a")
        row = rank - 1
        return row, col

    @staticmethod
    def coords_to_algebraic(row: int, col: int):
        file = chr(ord("a") + col)
        rank = str(row + 1)
        return file + rank

    def is_in_check(self, color: Color) -> bool:
        king_row, king_col = self.board.find_king(color)
        enemy = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.board.is_square_attacked(king_row, king_col, enemy)

    def _starting_rook_square(self, color: Color, side: str):
        if color == Color.WHITE:
            return (0, 7) if side == "K" else (0, 0)
        return (7, 7) if side == "K" else (7, 0)

    def _starting_king_square(self, color: Color):
        return (0, 4) if color == Color.WHITE else (7, 4)

    def _castling_moves_for(self, color: Color):
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
        if len(to_square) == 2:
            return to_square, None
        if len(to_square) == 3:
            return to_square[:2], self._promotion_from_token(to_square[2])
        raise ValueError("Invalid destination format")

    def _en_passant_moves_for_pawn(self, from_row, from_col, color: Color):
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

    def _apply_move_on_board(self, from_row, from_col, to_row, to_col, promotion_piece_type=None):
        piece = self.board.get_piece(from_row, from_col)
        captured = self.board.get_piece(to_row, to_col)

        en_passant = False
        ep_captured_pos = None

        castling = False
        rook_from = None
        rook_to = None
        rook_piece = None

        promoted_from = None

        if piece.piece_type == PieceType.PAWN:
            if captured is None and to_col != from_col and self.en_passant_target == (to_row, to_col):
                direction = 1 if piece.color == Color.WHITE else -1
                cap_row = to_row - direction
                cap_col = to_col
                cap_piece = self.board.get_piece(cap_row, cap_col)
                if cap_piece and cap_piece.piece_type == PieceType.PAWN and cap_piece.color != piece.color:
                    en_passant = True
                    ep_captured_pos = (cap_row, cap_col)
                    captured = cap_piece
                    self.board.set_piece(cap_row, cap_col, None)

        if piece.piece_type == PieceType.KING and abs(to_col - from_col) == 2:
            castling = True
            if to_col == 6:
                rook_from = self._starting_rook_square(piece.color, "K")
                rook_to = (from_row, 5)
            else:
                rook_from = self._starting_rook_square(piece.color, "Q")
                rook_to = (from_row, 3)
            rook_piece = self.board.get_piece(rook_from[0], rook_from[1])
            if rook_piece is None or rook_piece.piece_type != PieceType.ROOK or rook_piece.color != piece.color:
                raise ValueError("Illegal castling rook state")
            self.board.set_piece(rook_to[0], rook_to[1], rook_piece)
            self.board.set_piece(rook_from[0], rook_from[1], None)

        self.board.set_piece(to_row, to_col, piece)
        self.board.set_piece(from_row, from_col, None)

        if piece.piece_type == PieceType.PAWN:
            last_row = 7 if piece.color == Color.WHITE else 0
            if to_row == last_row:
                pt = promotion_piece_type or PieceType.QUEEN
                promoted_from = piece.piece_type
                self.board.set_piece(to_row, to_col, Piece(pt, piece.color))

        return {
            "piece": piece,
            "captured": captured,
            "from": (from_row, from_col),
            "to": (to_row, to_col),
            "en_passant": en_passant,
            "ep_captured_pos": ep_captured_pos,
            "castling": castling,
            "rook_from": rook_from,
            "rook_to": rook_to,
            "rook_piece": rook_piece,
            "promoted_from": promoted_from,
        }

    def _undo_move_on_board(self, info):
        from_row, from_col = info["from"]
        to_row, to_col = info["to"]
        piece = info["piece"]
        captured = info["captured"]

        self.board.set_piece(from_row, from_col, piece)
        self.board.set_piece(to_row, to_col, captured)

        if info["en_passant"]:
            cap_row, cap_col = info["ep_captured_pos"]
            self.board.set_piece(cap_row, cap_col, captured)
            self.board.set_piece(to_row, to_col, None)

        if info["castling"]:
            rf = info["rook_from"]
            rt = info["rook_to"]
            rp = info["rook_piece"]
            self.board.set_piece(rf[0], rf[1], rp)
            self.board.set_piece(rt[0], rt[1], None)

    def _legal_moves_for_piece_with_specials(self, row, col, color: Color):
        piece = self.board.get_piece(row, col)
        if piece is None or piece.color != color:
            return []

        moves = list(self.board.get_legal_moves(row, col))

        if piece.piece_type == PieceType.PAWN:
            moves.extend(self._en_passant_moves_for_pawn(row, col, color))

        if piece.piece_type == PieceType.KING:
            for (k_from, k_to, r_from, r_to) in self._castling_moves_for(color):
                if k_from == (row, col):
                    moves.append(k_to)

        return moves

    def _is_legal_after_king_safety(self, from_row, from_col, to_row, to_col, color: Color, promotion_piece_type=None) -> bool:
        piece = self.board.get_piece(from_row, from_col)
        if piece is None or piece.color != color:
            return False

        legal_targets = self._legal_moves_for_piece_with_specials(from_row, from_col, color)
        if (to_row, to_col) not in legal_targets:
            return False

        info = self._apply_move_on_board(from_row, from_col, to_row, to_col, promotion_piece_type=promotion_piece_type)
        ok = not self.is_in_check(color)
        self._undo_move_on_board(info)
        return ok

    def get_all_legal_moves(self, color: Color):
        out = []
        for from_row, from_col in self.board.get_positions_of_color(color):
            piece = self.board.get_piece(from_row, from_col)
            if piece is None:
                continue
            targets = self._legal_moves_for_piece_with_specials(from_row, from_col, color)
            for to_row, to_col in targets:
                if piece.piece_type == PieceType.PAWN:
                    last_row = 7 if color == Color.WHITE else 0
                    if to_row == last_row:
                        for promo in (PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT):
                            if self._is_legal_after_king_safety(from_row, from_col, to_row, to_col, color, promotion_piece_type=promo):
                                out.append(((from_row, from_col), (to_row, to_col), promo))
                        continue
                if self._is_legal_after_king_safety(from_row, from_col, to_row, to_col, color, promotion_piece_type=None):
                    out.append(((from_row, from_col), (to_row, to_col), None))
        return out

    def has_any_legal_moves(self, color: Color) -> bool:
        for from_row, from_col in self.board.get_positions_of_color(color):
            piece = self.board.get_piece(from_row, from_col)
            if piece is None:
                continue
            targets = self._legal_moves_for_piece_with_specials(from_row, from_col, color)
            for to_row, to_col in targets:
                if piece.piece_type == PieceType.PAWN:
                    last_row = 7 if color == Color.WHITE else 0
                    if to_row == last_row:
                        for promo in (PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT):
                            if self._is_legal_after_king_safety(from_row, from_col, to_row, to_col, color, promotion_piece_type=promo):
                                return True
                        continue
                if self._is_legal_after_king_safety(from_row, from_col, to_row, to_col, color, promotion_piece_type=None):
                    return True
        return False

    def is_checkmate(self, color: Color) -> bool:
        return self.is_in_check(color) and not self.has_any_legal_moves(color)

    def is_stalemate(self, color: Color) -> bool:
        return (not self.is_in_check(color)) and (not self.has_any_legal_moves(color))

    def get_status_for(self, color: Color):
        if self.is_checkmate(color):
            return "checkmate"
        if self.is_stalemate(color):
            return "stalemate"
        if self.is_in_check(color):
            return "check"
        return "normal"

    def _update_castle_rights_on_move(self, piece, from_row, from_col, to_row, to_col, captured):
        color = piece.color
        enemy = Color.BLACK if color == Color.WHITE else Color.WHITE

        if piece.piece_type == PieceType.KING:
            self.castle_rights[color]["K"] = False
            self.castle_rights[color]["Q"] = False

        if piece.piece_type == PieceType.ROOK:
            if (from_row, from_col) == self._starting_rook_square(color, "K"):
                self.castle_rights[color]["K"] = False
            if (from_row, from_col) == self._starting_rook_square(color, "Q"):
                self.castle_rights[color]["Q"] = False

        if captured and captured.piece_type == PieceType.ROOK:
            if (to_row, to_col) == self._starting_rook_square(enemy, "K"):
                self.castle_rights[enemy]["K"] = False
            if (to_row, to_col) == self._starting_rook_square(enemy, "Q"):
                self.castle_rights[enemy]["Q"] = False

    def snapshot(self):
        grid_copy = [[None for _ in range(8)] for _ in range(8)]
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece(r, c)
                if p is None:
                    grid_copy[r][c] = None
                else:
                    grid_copy[r][c] = Piece(p.piece_type, p.color)
        rights_copy = {
            Color.WHITE: {"K": self.castle_rights[Color.WHITE]["K"], "Q": self.castle_rights[Color.WHITE]["Q"]},
            Color.BLACK: {"K": self.castle_rights[Color.BLACK]["K"], "Q": self.castle_rights[Color.BLACK]["Q"]},
        }
        ep = None if self.en_passant_target is None else (self.en_passant_target[0], self.en_passant_target[1])
        return {
            "grid": grid_copy,
            "current_player": self.current_player,
            "history_len": len(self.history),
            "en_passant_target": ep,
            "castle_rights": rights_copy,
        }

    def restore(self, snap):
        for r in range(8):
            for c in range(8):
                self.board.set_piece(r, c, snap["grid"][r][c])
        self.current_player = snap["current_player"]
        self.en_passant_target = snap["en_passant_target"]
        self.castle_rights = snap["castle_rights"]
        if len(self.history) > snap["history_len"]:
            self.history = self.history[:snap["history_len"]]

    def move(self, from_square: str, to_square: str):
        to_sq, promo_type = self._parse_to_square(to_square)
        from_row, from_col = self.algebraic_to_coords(from_square)
        to_row, to_col = self.algebraic_to_coords(to_sq)

        piece = self.board.get_piece(from_row, from_col)
        if piece is None:
            raise ValueError("No piece at start square")
        if piece.color != self.current_player:
            raise ValueError("Not your turn")

        if not self._is_legal_after_king_safety(from_row, from_col, to_row, to_col, self.current_player, promotion_piece_type=promo_type):
            raise ValueError("Illegal move")

        info = self._apply_move_on_board(from_row, from_col, to_row, to_col, promotion_piece_type=promo_type)
        captured = info["captured"]
        self._update_castle_rights_on_move(piece, from_row, from_col, to_row, to_col, captured)

        self.en_passant_target = None
        if piece.piece_type == PieceType.PAWN:
            direction = 1 if piece.color == Color.WHITE else -1
            if to_col == from_col and to_row == from_row + 2 * direction:
                self.en_passant_target = (from_row + direction, from_col)

        mv = Move(
            from_square,
            to_square,
            piece,
            captured=captured,
            promotion=(promo_type.value if promo_type else None),
            en_passant=info["en_passant"],
            castling=info["castling"],
        )
        self.history.append(mv)

        opponent = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        in_check = self.is_in_check(opponent)
        self.current_player = opponent
        status = self.get_status_for(self.current_player)

        return in_check, status
