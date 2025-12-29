from pieces import Piece, PieceType, Color

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.setup_initial_position()

    def in_bounds(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece(self, row, col):
        return self.grid[row][col]

    def set_piece(self, row, col, piece):
        self.grid[row][col] = piece

    def setup_initial_position(self):
        order = [
            PieceType.ROOK,
            PieceType.KNIGHT,
            PieceType.BISHOP,
            PieceType.QUEEN,
            PieceType.KING,
            PieceType.BISHOP,
            PieceType.KNIGHT,
            PieceType.ROOK,
        ]

        for col, ptype in enumerate(order):
            self.set_piece(0, col, Piece(ptype, Color.WHITE))

        for col, ptype in enumerate(order):
            self.set_piece(7, col, Piece(ptype, Color.BLACK))

        for col in range(8):
            self.set_piece(1, col, Piece(PieceType.PAWN, Color.WHITE))
            self.set_piece(6, col, Piece(PieceType.PAWN, Color.BLACK))

    def is_empty(self, row, col) -> bool:
        return self.get_piece(row, col) is None

    def is_ally(self, row, col, color) -> bool:
        piece = self.get_piece(row, col)
        return piece is not None and piece.color == color

    def is_enemy(self, row, col, color) -> bool:
        piece = self.get_piece(row, col)
        return piece is not None and piece.color != color

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    return row, col
        raise ValueError(f"Nu am gasit regele pentru {color}.")

    def is_square_attacked(self, row, col, by_color):
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece and piece.color == by_color:
                    moves = self.get_legal_moves(r, c)
                    if (row, col) in moves:
                        return True
        return False


    def __str__(self):
        lines = []
        for row in range(7, -1, -1):
            line = [str(row + 1)]
            for col in range(8):
                piece = self.get_piece(row, col)
                line.append(piece.symbol if piece else ".")
            lines.append(" ".join(line))
        lines.append("  a b c d e f g h")
        return "\n".join(lines)

    def get_legal_moves(self, row, col):
        piece = self.get_piece(row, col)
        if piece is None:
            return []

        if piece.piece_type == PieceType.ROOK:
            return self._rook_moves(row, col)
        elif piece.piece_type == PieceType.BISHOP:
            return self._bishop_moves(row, col)
        elif piece.piece_type == PieceType.QUEEN:
            return self._queen_moves(row, col)
        elif piece.piece_type == PieceType.KNIGHT:
            return self._knight_moves(row, col)
        elif piece.piece_type == PieceType.KING:
            return self._king_moves(row, col)
        elif piece.piece_type == PieceType.PAWN:
            return self._pawn_moves(row, col, piece.color)

        return []

    def _linear_moves(self, row, col, directions):
        piece = self.get_piece(row, col)
        color = piece.color
        moves = []

        for d_row, d_col in directions:
            r, c = row + d_row, col + d_col
            while self.in_bounds(r, c):
                if self.is_empty(r, c):
                    moves.append((r, c))
                else:
                    if self.is_enemy(r, c, color):
                        moves.append((r, c))
                    break
                r += d_row
                c += d_col

        return moves


    def _rook_moves(self, row, col):
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]
        return self._linear_moves(row, col, directions)

    def _bishop_moves(self, row, col):
        directions = [
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        return self._linear_moves(row, col, directions)

    def _queen_moves(self, row, col):
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        return self._linear_moves(row, col, directions)

    def _knight_moves(self, row, col):
        piece = self.get_piece(row, col)
        color = piece.color
        moves = []
        offsets = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        for d_row, d_col in offsets:
            r, c = row + d_row, col + d_col
            if self.in_bounds(r, c):
                if self.is_empty(r, c) or self.is_enemy(r, c, color):
                    moves.append((r, c))
        return moves


    def _king_moves(self, row, col):
        piece = self.get_piece(row, col)
        color = piece.color
        moves = []
        for d_row in [-1, 0, 1]:
            for d_col in [-1, 0, 1]:
                if d_row == 0 and d_col == 0:
                    continue
                r, c = row + d_row, col + d_col
                if self.in_bounds(r, c):
                    if self.is_empty(r, c) or self.is_enemy(r, c, color):
                        moves.append((r, c))
        return moves


    def _pawn_moves(self, row, col, color):
        moves = []
        direction = 1 if color == Color.WHITE else -1
        one_step = row + direction
        if self.in_bounds(one_step, col) and self.is_empty(one_step, col):
            moves.append((one_step, col))

            start_row = 1 if color == Color.WHITE else 6
            two_step = row + 2 * direction
            if row == start_row and self.is_empty(two_step, col):
                moves.append((two_step, col))

        capture_row = row + direction
        for dc in (-1, 1):
            capture_col = col + dc
            if self.in_bounds(capture_row, capture_col):
                if self.is_enemy(capture_row, capture_col, color):
                    moves.append((capture_row, capture_col))

        return moves


    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.get_piece(from_row, from_col)
        if piece is None:
            raise ValueError("Nu exista piesa pe pozitia de start.")

        legal_moves = self.get_legal_moves(from_row, from_col)
        if (to_row, to_col) not in legal_moves:
            raise ValueError("Mutare ilegala pentru piesa selectata.")

        dest_piece = self.get_piece(to_row, to_col)
        if dest_piece is not None and dest_piece.color == piece.color:
            raise ValueError("Nu poti muta pe o piesa de aceeasi culoare.")

        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, None)



