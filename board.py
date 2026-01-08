from pieces import Piece, PieceType, Color


class Board:
    """
    Reprezinta tabla de sah 8x8 si operatiile de baza pe tabla.

    Se ocupa de:
    - stocarea pieselor intr-o matrice 8x8
    - initializarea pozitiei de start
    - generarea mutarilor de baza pentru fiecare piesa
    - detectarea patratelor atacate (util pentru sah)
    - efectuarea mutarilor simple pe tabla (fara rand, fara reguli avansate)
    """

    def __init__(self):
        """
        Creeaza o tabla goala 8x8 si pune piesele in pozitia initiala.
        """
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.setup_initial_position()

    def in_bounds(self, row, col):
        """
        Verifica daca o pozitie (row, col) se afla in interiorul tablei.

        :return: True daca 0 <= row < 8 si 0 <= col < 8, altfel False
        """
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece(self, row, col):
        """
        Returneaza piesa de pe patratul (row, col) sau None daca este gol.
        """
        return self.grid[row][col]

    def set_piece(self, row, col, piece):
        """
        Plaseaza o piesa (sau None) pe patratul (row, col).
        """
        self.grid[row][col] = piece

    def setup_initial_position(self):
        """
        Seteaza tabla in pozitia initiala standard de sah.
        """
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
        """
        Verifica daca patratul este gol (nu are piesa).

        :return: True daca pe patrat este None, altfel False
        """
        return self.get_piece(row, col) is None

    def is_ally(self, row, col, color) -> bool:
        """
        Verifica daca pe patrat este o piesa de aceeasi culoare.

        :return: True daca exista piesa si are aceeasi culoare, altfel False
        """
        piece = self.get_piece(row, col)
        return piece is not None and piece.color == color

    def is_enemy(self, row, col, color) -> bool:
        """
        Verifica daca pe patrat este o piesa inamica.

        :return: True daca exista piesa si are culoare diferita, altfel False
        """
        piece = self.get_piece(row, col)
        return piece is not None and piece.color != color

    def find_king(self, color):
        """
        Gaseste pozitia regelui pentru o anumita culoare.

        :return: (row, col) unde se afla regele
        :raises ValueError: daca regele nu este gasit pe tabla
        """
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    return row, col
        raise ValueError(f"King not found for {color}")

    def get_positions_of_color(self, color):
        """
        Returneaza toate pozitiile pieselor unei culori.

        :return: lista de tuple (row, col)
        """
        positions = []
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece and piece.color == color:
                    positions.append((r, c))
        return positions

    def _attack_squares(self, row, col):
        """
        Calculeaza patratele pe care le ataca piesa de la (row, col).

        Important:
        - pentru pion: atacul este pe diagonale, nu in fata
        - pentru piesele liniare (tura/nebun/regina): atacul merge pana la prima piesa intalnita
        """
        piece = self.get_piece(row, col)
        if piece is None:
            return []

        pt = piece.piece_type
        color = piece.color

        if pt == PieceType.PAWN:
            direction = 1 if color == Color.WHITE else -1
            out = []
            r = row + direction
            for dc in (-1, 1):
                c = col + dc
                if self.in_bounds(r, c):
                    out.append((r, c))
            return out

        if pt == PieceType.KNIGHT:
            out = []
            offsets = [
                (2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2),
            ]
            for dr, dc in offsets:
                r, c = row + dr, col + dc
                if self.in_bounds(r, c):
                    out.append((r, c))
            return out

        if pt == PieceType.KING:
            out = []
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if self.in_bounds(r, c):
                        out.append((r, c))
            return out

        directions = []
        if pt == PieceType.ROOK:
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        elif pt == PieceType.BISHOP:
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        elif pt == PieceType.QUEEN:
            directions = [
                (1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1),
            ]

        out = []
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while self.in_bounds(r, c):
                out.append((r, c))
                if not self.is_empty(r, c):
                    break
                r += dr
                c += dc
        return out

    def is_square_attacked(self, row, col, by_color):
        """
        Verifica daca un patrat (row, col) este atacat de o anumita culoare.

        :return: True daca exista cel putin o piesa a culorii by_color care ataca patratul
        """
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece and piece.color == by_color:
                    if (row, col) in self._attack_squares(r, c):
                        return True
        return False

    def __str__(self):
        """
        Returneaza o reprezentare ASCII a tablei pentru debug.
        """
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
        """
        Returneaza mutarile de baza legale pentru piesa de la (row, col),
        fara a verifica daca regele ramane in sah.

        :return: lista de patrate tinta (row, col)
        """
        piece = self.get_piece(row, col)
        if piece is None:
            return []

        if piece.piece_type == PieceType.ROOK:
            return self._rook_moves(row, col)
        if piece.piece_type == PieceType.BISHOP:
            return self._bishop_moves(row, col)
        if piece.piece_type == PieceType.QUEEN:
            return self._queen_moves(row, col)
        if piece.piece_type == PieceType.KNIGHT:
            return self._knight_moves(row, col)
        if piece.piece_type == PieceType.KING:
            return self._king_moves(row, col)
        if piece.piece_type == PieceType.PAWN:
            return self._pawn_moves(row, col, piece.color)

        return []

    def _linear_moves(self, row, col, directions):
        """
        Functie generica pentru piesele care se misca in linie:
        tura, nebun, regina.

        Merge pe directii pana cand iese din tabla sau intalneste o piesa.
        """
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
        """
        Mutari pentru tura (orizontal si vertical).
        """
        return self._linear_moves(row, col, [(1, 0), (-1, 0), (0, 1), (0, -1)])

    def _bishop_moves(self, row, col):
        """
        Mutari pentru nebun (diagonale).
        """
        return self._linear_moves(row, col, [(1, 1), (1, -1), (-1, 1), (-1, -1)])

    def _queen_moves(self, row, col):
        """
        Mutari pentru regina (tura + nebun).
        """
        return self._linear_moves(
            row,
            col,
            [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
        )

    def _knight_moves(self, row, col):
        """
        Mutari pentru cal (salturi in forma de L).
        """
        piece = self.get_piece(row, col)
        color = piece.color
        moves = []
        offsets = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2),
        ]
        for d_row, d_col in offsets:
            r, c = row + d_row, col + d_col
            if self.in_bounds(r, c):
                if self.is_empty(r, c) or self.is_enemy(r, c, color):
                    moves.append((r, c))
        return moves

    def _king_moves(self, row, col):
        """
        Mutari pentru rege (un pas in orice directie),
        fara a verifica daca pasul intra intr-un patrat atacat.
        """
        piece = self.get_piece(row, col)
        color = piece.color
        moves = []
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                if d_row == 0 and d_col == 0:
                    continue
                r, c = row + d_row, col + d_col
                if self.in_bounds(r, c):
                    if self.is_empty(r, c) or self.is_enemy(r, c, color):
                        moves.append((r, c))
        return moves

    def _pawn_moves(self, row, col, color):
        """
        Mutari pentru pion:
        - un pas in fata daca e liber
        - doi pasi din pozitia initiala daca sunt libere patratele
        - capturi pe diagonala daca exista piesa inamica
        """
        moves = []
        direction = 1 if color == Color.WHITE else -1

        one_step = row + direction
        if self.in_bounds(one_step, col) and self.is_empty(one_step, col):
            moves.append((one_step, col))
            start_row = 1 if color == Color.WHITE else 6
            two_step = row + 2 * direction
            if row == start_row and self.in_bounds(two_step, col) and self.is_empty(two_step, col):
                moves.append((two_step, col))

        capture_row = row + direction
        for dc in (-1, 1):
            capture_col = col + dc
            if self.in_bounds(capture_row, capture_col):
                if self.is_enemy(capture_row, capture_col, color):
                    moves.append((capture_row, capture_col))

        return moves

    def move_piece(self, from_row, from_col, to_row, to_col):
        """
        Muta o piesa pe tabla folosind regulile de baza de miscare.

        Verifica:
        - exista piesa la start
        - destinatia este in lista mutarilor legale ale piesei
        - nu se poate muta peste o piesa de aceeasi culoare

        Important:
        - nu verifica randul
        - nu verifica sah
        - nu gestioneaza rocada/en passant/promovare (acestea sunt in game.py)
        """
        piece = self.get_piece(from_row, from_col)
        if piece is None:
            raise ValueError("No piece at start square")

        legal_moves = self.get_legal_moves(from_row, from_col)
        if (to_row, to_col) not in legal_moves:
            raise ValueError("Illegal move for selected piece")

        dest_piece = self.get_piece(to_row, to_col)
        if dest_piece is not None and dest_piece.color == piece.color:
            raise ValueError("Cannot move onto same color piece")

        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, None)
