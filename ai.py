import math
from pieces import Color, PieceType


PIECE_VALUE = {
    PieceType.PAWN: 100,
    PieceType.KNIGHT: 320,
    PieceType.BISHOP: 330,
    PieceType.ROOK: 500,
    PieceType.QUEEN: 900,
    PieceType.KING: 20000,
}
"""
Dictionar care asociaza fiecarei piese o valoare numerica.

Valorile sunt folosite pentru evaluarea materialului pe tabla:
- valori pozitive favorizeaza albul
- valori negative favorizeaza negrul (aplicate ulterior)
"""


def evaluate_material(game) -> int:
    """
    Evalueaza pozitia curenta a jocului pe baza materialului.

    Se parcurge intreaga tabla si se aduna valorile pieselor:
    - piesele albe adauga scor
    - piesele negre scad scor

    :param game: instanta ChessGame
    :return: scorul material al pozitiei (int)
    """
    score = 0
    for r in range(8):
        for c in range(8):
            p = game.board.get_piece(r, c)
            if p is None:
                continue
            v = PIECE_VALUE[p.piece_type]
            score += v if p.color == Color.WHITE else -v
    return score


class ChessAI:
    """
    Clasa care implementeaza un adversar AI pentru sah.

    AI-ul foloseste algoritmul minimax cu alpha-beta pruning
    pentru a cauta cea mai buna mutare posibila.
    """

    def __init__(self, depth: int = 3):
        """
        Initializeaza AI-ul cu o anumita adancime de cautare.

        :param depth: cate mutari inainte analizeaza AI-ul
        """
        self.depth = max(1, int(depth))

    def choose_move(self, game):
        """
        Alege cea mai buna mutare pentru jucatorul curent.

        Se genereaza toate mutarile legale, se ordoneaza
        astfel incat capturile si promovarile sa fie evaluate primele,
        apoi se aplica minimax pentru fiecare mutare.

        :param game: instanta ChessGame
        :return: tuplu (from_square, to_square) sau None daca nu exista mutari
        """
        color = game.current_player
        best = None
        best_score = -math.inf if color == Color.WHITE else math.inf

        moves = game.get_all_legal_moves(color)

        ordered = []
        for (fp, tp, promo) in moves:
            fr, fc = fp
            tr, tc = tp
            mover = game.board.get_piece(fr, fc)
            cap = game.board.get_piece(tr, tc)
            cap_value = 0 if cap is None else PIECE_VALUE[cap.piece_type]
            promo_value = 0 if promo is None else PIECE_VALUE[promo]
            ordered.append((cap_value + promo_value, fp, tp, promo))

        ordered.sort(reverse=True, key=lambda x: x[0])

        for _, fp, tp, promo in ordered:
            snap = game.snapshot()
            from_alg = game.coords_to_algebraic(fp[0], fp[1])
            to_alg = game.coords_to_algebraic(tp[0], tp[1])
            if promo is not None:
                to_alg = to_alg + promo.value
            try:
                game.move(from_alg, to_alg)
                score = self._minimax(game, self.depth - 1, -math.inf, math.inf)
            except Exception:
                game.restore(snap)
                continue
            game.restore(snap)

            if color == Color.WHITE:
                if score > best_score:
                    best_score = score
                    best = (from_alg, to_alg)
            else:
                if score < best_score:
                    best_score = score
                    best = (from_alg, to_alg)

        return best

    def _terminal_score(self, game, depth):
        """
        Returneaza scorul pentru o pozitie terminala.

        - checkmate: scor foarte mare negativ (pierdere)
        - stalemate: scor neutru

        :param game: instanta ChessGame
        :param depth: adancimea ramasa
        :return: scor int sau None daca pozitia nu este terminala
        """
        status = game.get_status_for(game.current_player)
        if status == "checkmate":
            return -1000000 + (self.depth - depth)
        if status == "stalemate":
            return 0
        return None

    def _minimax(self, game, depth: int, alpha: float, beta: float) -> int:
        """
        Algoritmul minimax cu alpha-beta pruning.

        Simuleaza mutari alternative pentru ambii jucatori
        si elimina ramurile care nu pot influenta rezultatul final.

        :param game: instanta ChessGame
        :param depth: adancimea ramasa de cautare
        :param alpha: cel mai bun scor garantat pentru maximizator
        :param beta: cel mai bun scor garantat pentru minimizator
        :return: scorul evaluat al pozitiei
        """
        term = self._terminal_score(game, depth)
        if term is not None:
            return term

        if depth == 0:
            return evaluate_material(game)

        color = game.current_player
        moves = game.get_all_legal_moves(color)

        if not moves:
            return evaluate_material(game)

        if color == Color.WHITE:
            value = -math.inf
            for fp, tp, promo in moves:
                snap = game.snapshot()
                from_alg = game.coords_to_algebraic(fp[0], fp[1])
                to_alg = game.coords_to_algebraic(tp[0], tp[1])
                if promo is not None:
                    to_alg = to_alg + promo.value
                try:
                    game.move(from_alg, to_alg)
                    value = max(value, self._minimax(game, depth - 1, alpha, beta))
                except Exception:
                    game.restore(snap)
                    continue
                game.restore(snap)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return int(value)
        else:
            value = math.inf
            for fp, tp, promo in moves:
                snap = game.snapshot()
                from_alg = game.coords_to_algebraic(fp[0], fp[1])
                to_alg = game.coords_to_algebraic(tp[0], tp[1])
                if promo is not None:
                    to_alg = to_alg + promo.value
                try:
                    game.move(from_alg, to_alg)
                    value = min(value, self._minimax(game, depth - 1, alpha, beta))
                except Exception:
                    game.restore(snap)
                    continue
                game.restore(snap)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return int(value)
