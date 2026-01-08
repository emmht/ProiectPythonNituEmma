import tkinter as tk
from tkinter import messagebox, filedialog

from game import ChessGame
from pieces import Color
from ai import ChessAI
from pgn_tools import save_pgn_like, load_pgn_like


UNICODE_MAP = {
    "K": "♔",
    "Q": "♕",
    "R": "♖",
    "B": "♗",
    "N": "♘",
    "P": "♙",
    "k": "♚",
    "q": "♛",
    "r": "♜",
    "b": "♝",
    "n": "♞",
    "p": "♟",
}
"""
Dictionar care mapeaza simbolurile interne ale pieselor (K, q, etc.)
catre simboluri Unicode pentru afisare in interfata grafica.
"""


class ChessGUI:
    """
    Interfata grafica pentru jocul de sah folosind Tkinter.

    Se ocupa de:
    - desenarea tablei si pieselor
    - selectarea pieselor cu mouse-ul
    - evidentierea mutarilor legale
    - aplicarea mutarilor in engine (ChessGame)
    - afisarea statusului (check, checkmate, stalemate)
    - salvare/incarcare fisier (PGN-like)
    - control AI (pornit/oprit, side, depth, mutare AI)
    """

    def __init__(self, root: tk.Tk):
        """
        Construieste interfata:
        - zona de status (Turn/Status/Mesaje)
        - tabla 8x8 din butoane
        - zona de control (New/Reset/Save/Load/AI)

        :param root: fereastra principala Tkinter
        """
        self.root = root
        self.root.title("Chess")

        self.game = ChessGame()

        self.selected = None
        self.legal_map = {}
        self.legal_targets = set()

        self.status_var = tk.StringVar()
        self.turn_var = tk.StringVar()
        self.info_var = tk.StringVar()

        self.ai_enabled = tk.BooleanVar(value=False)
        self.ai_side = tk.StringVar(value="BLACK")
        self.ai_depth = tk.IntVar(value=3)

        top = tk.Frame(root)
        top.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top, textvariable=self.turn_var, anchor="w").pack(side=tk.LEFT, padx=8, pady=6)
        tk.Label(top, textvariable=self.status_var, anchor="w").pack(side=tk.LEFT, padx=8, pady=6)
        tk.Label(top, textvariable=self.info_var, anchor="w").pack(side=tk.LEFT, padx=8, pady=6)

        board_frame = tk.Frame(root)
        board_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.buttons = [[None for _ in range(8)] for _ in range(8)]

        for ui_r in range(8):
            for c in range(8):
                r = 7 - ui_r
                btn = tk.Button(
                    board_frame,
                    width=4,
                    height=2,
                    font=("Arial", 20),
                    command=lambda rr=r, cc=c: self.on_square_click(rr, cc),
                )
                btn.grid(row=ui_r, column=c, padx=0, pady=0, sticky="nsew")
                self.buttons[r][c] = btn

        control = tk.Frame(root)
        control.pack(side=tk.TOP, fill=tk.X, padx=10, pady=6)

        tk.Button(control, text="New Game", command=self.new_game).pack(side=tk.LEFT)
        tk.Button(control, text="Reset Selection", command=self.reset_selection).pack(side=tk.LEFT, padx=8)
        tk.Button(control, text="Save", command=self.save_game).pack(side=tk.LEFT, padx=8)
        tk.Button(control, text="Load", command=self.load_game).pack(side=tk.LEFT, padx=8)

        tk.Label(control, text="AI").pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(control, variable=self.ai_enabled, command=self.on_ai_toggle).pack(side=tk.LEFT)
        tk.Label(control, text="Side").pack(side=tk.LEFT, padx=6)
        tk.OptionMenu(control, self.ai_side, "WHITE", "BLACK").pack(side=tk.LEFT)
        tk.Label(control, text="Depth").pack(side=tk.LEFT, padx=6)
        tk.OptionMenu(control, self.ai_depth, 1, 2, 3, 4).pack(side=tk.LEFT)
        tk.Button(control, text="AI Move", command=self.ai_move).pack(side=tk.LEFT, padx=8)

        self.refresh()

    def on_ai_toggle(self):
        """
        Este apelata cand se bifeaza/debifeaza AI-ul.
        Daca AI-ul este activ si este randul lui, poate muta automat.
        """
        self.maybe_ai_autoplay()

    def new_game(self):
        """
        Reseteaza jocul complet la pozitia initiala.
        """
        self.game = ChessGame()
        self.reset_selection()
        self.refresh()

    def reset_selection(self):
        """
        Sterge selectia curenta si toate highlight-urile pentru mutari.
        """
        self.selected = None
        self.legal_map = {}
        self.legal_targets = set()
        self.info_var.set("")
        self.refresh()

    def piece_to_text(self, piece):
        """
        Converteste o piesa in text pentru afisare pe buton.
        Foloseste UNICODE_MAP daca exista.

        :param piece: Piece sau None
        :return: string afisabil in GUI
        """
        if piece is None:
            return ""
        return UNICODE_MAP.get(piece.symbol, piece.symbol)

    def square_colors(self, r, c):
        """
        Returneaza culoarea de fundal pentru un patrat,
        alternand intre patrate deschise si inchise.

        :return: cod hex pentru culoare
        """
        light = (r + c) % 2 == 0
        return "#EEEED2" if light else "#769656"

    def refresh(self):
        """
        Re-deseneaza intreaga interfata:
        - recalculeaza mutarile legale
        - actualizeaza textele Turn/Status
        - actualizeaza piesele pe tabla
        - aplica highlight pentru selectie si mutari legale
        """
        self.rebuild_legal_cache()

        turn = "WHITE" if self.game.current_player == Color.WHITE else "BLACK"
        self.turn_var.set(f"Turn: {turn}")

        status = self.game.get_status_for(self.game.current_player)
        self.status_var.set(f"Status: {status}")

        for r in range(8):
            for c in range(8):
                btn = self.buttons[r][c]
                base = self.square_colors(r, c)
                btn.configure(bg=base, activebackground=base)

                piece = self.game.board.get_piece(r, c)
                btn.configure(text=self.piece_to_text(piece))

        if self.selected is not None:
            sr, sc = self.selected
            self.buttons[sr][sc].configure(bg="#BACA44", activebackground="#BACA44")

        for (tr, tc) in self.legal_targets:
            if self.selected is None:
                continue
            if (tr, tc) == self.selected:
                continue
            self.buttons[tr][tc].configure(bg="#F6F669", activebackground="#F6F669")

    def rebuild_legal_cache(self):
        """
        Construieste un cache cu mutarile legale pentru jucatorul curent.

        legal_map:
        - cheie: (from_row, from_col)
        - valoare: lista de (to_row, to_col) si promovare posibila

        legal_targets:
        - set de patrate tinta pentru piesa selectata (pentru highlight)
        """
        self.legal_map = {}
        all_moves = self.game.get_all_legal_moves(self.game.current_player)
        for (from_pos, to_pos, promo) in all_moves:
            self.legal_map.setdefault(from_pos, []).append((to_pos, promo))

        if self.selected is None:
            self.legal_targets = set()
        else:
            self.legal_targets = set(tp for (tp, _promo) in self.legal_map.get(self.selected, []))

    def coords_to_alg(self, r, c):
        """
        Converteste coordonate interne (row, col) in notatie algebraica (ex: e2).
        """
        file = chr(ord("a") + c)
        rank = str(r + 1)
        return file + rank

    def ask_promotion(self):
        """
        Afiseaza o fereastra mica pentru a alege piesa de promovare.

        :return: una dintre literele "Q", "R", "B", "N" sau None daca se inchide
        """
        win = tk.Toplevel(self.root)
        win.title("Promotion")
        win.transient(self.root)
        win.grab_set()

        chosen = {"v": None}

        def pick(v):
            chosen["v"] = v
            win.destroy()

        tk.Label(win, text="Choose promotion:").pack(padx=10, pady=10)

        row = tk.Frame(win)
        row.pack(padx=10, pady=10)

        tk.Button(row, text="Q", width=4, command=lambda: pick("Q")).pack(side=tk.LEFT, padx=4)
        tk.Button(row, text="R", width=4, command=lambda: pick("R")).pack(side=tk.LEFT, padx=4)
        tk.Button(row, text="B", width=4, command=lambda: pick("B")).pack(side=tk.LEFT, padx=4)
        tk.Button(row, text="N", width=4, command=lambda: pick("N")).pack(side=tk.LEFT, padx=4)

        self.root.wait_window(win)
        return chosen["v"]

    def current_ai_color(self):
        """
        Intoarce culoarea pentru care joaca AI-ul, daca AI este activ.

        :return: Color.WHITE / Color.BLACK sau None daca AI este oprit
        """
        if not self.ai_enabled.get():
            return None
        side = self.ai_side.get().upper()
        return Color.WHITE if side == "WHITE" else Color.BLACK

    def maybe_ai_autoplay(self):
        """
        Daca AI este activ si este randul lui, face o mutare automat.

        Nu muta daca jocul este deja terminat (checkmate/stalemate).
        """
        ai_color = self.current_ai_color()
        if ai_color is None:
            return
        if self.game.get_status_for(self.game.current_player) in ("checkmate", "stalemate"):
            return
        if self.game.current_player == ai_color:
            self.ai_move()

    def ai_move(self):
        """
        Face o mutare pentru AI, daca:
        - AI este activ
        - este randul AI-ului
        - jocul nu este terminat

        Alege mutarea cu minimax (ChessAI) si o aplica in engine.
        """
        ai_color = self.current_ai_color()
        if ai_color is None:
            self.info_var.set("AI disabled")
            return
        if self.game.current_player != ai_color:
            self.info_var.set("Not AI turn")
            return
        if self.game.get_status_for(self.game.current_player) in ("checkmate", "stalemate"):
            return

        ai = ChessAI(depth=self.ai_depth.get())
        best = ai.choose_move(self.game)
        if best is None:
            self.info_var.set("AI has no moves")
            return

        f, t = best
        try:
            in_check, status = self.game.move(f, t)
            msg = ""
            if in_check:
                msg = "Check"
            if status == "checkmate":
                msg = "Checkmate"
            elif status == "stalemate":
                msg = "Stalemate"
            self.info_var.set(msg)
            self.selected = None
            self.refresh()
            if status in ("checkmate", "stalemate"):
                messagebox.showinfo("Game Over", f"{status}")
            else:
                self.root.after(50, self.maybe_ai_autoplay)
        except Exception as e:
            self.info_var.set(str(e))
            self.refresh()

    def save_game(self):
        """
        Deschide un dialog de salvare si scrie jocul curent intr-un fisier PGN-like.
        """
        path = filedialog.asksaveasfilename(defaultextension=".pgn", filetypes=[("PGN-like", "*.pgn"), ("All files", "*.*")])
        if not path:
            return
        try:
            save_pgn_like(self.game, path)
            self.info_var.set("Saved")
        except Exception as e:
            self.info_var.set(str(e))

    def load_game(self):
        """
        Deschide un dialog de incarcare si reface jocul dintr-un fisier PGN-like.
        """
        path = filedialog.askopenfilename(filetypes=[("PGN-like", "*.pgn"), ("All files", "*.*")])
        if not path:
            return
        try:
            self.game = load_pgn_like(path)
            self.reset_selection()
            self.refresh()
            self.info_var.set("Loaded")
            self.root.after(50, self.maybe_ai_autoplay)
        except Exception as e:
            self.info_var.set(str(e))

    def on_square_click(self, r, c):
        """
        Handler pentru click pe un patrat de pe tabla.

        Comportament:
        - daca jocul e terminat, nu face nimic
        - daca e randul AI-ului, nu permite mutarea utilizatorului
        - daca nu exista selectie, selecteaza o piesa a jucatorului curent
        - daca exista selectie:
          - click pe aceeasi piesa: deselect
          - click pe alta piesa proprie: schimba selectia
          - click pe patrat tinta: aplica mutarea (si gestioneaza promovarea)
        """
        if self.game.get_status_for(self.game.current_player) in ("checkmate", "stalemate"):
            return

        ai_color = self.current_ai_color()
        if ai_color is not None and self.game.current_player == ai_color:
            return

        piece = self.game.board.get_piece(r, c)

        if self.selected is None:
            if piece is None:
                return
            if piece.color != self.game.current_player:
                return
            self.selected = (r, c)
            self.rebuild_legal_cache()
            self.refresh()
            return

        sr, sc = self.selected

        if (r, c) == (sr, sc):
            self.reset_selection()
            return

        if piece is not None and piece.color == self.game.current_player:
            self.selected = (r, c)
            self.rebuild_legal_cache()
            self.refresh()
            return

        options = self.legal_map.get((sr, sc), [])
        target = (r, c)
        promos = [p for (t, p) in options if t == target and p is not None]

        from_alg = self.coords_to_alg(sr, sc)
        to_alg = self.coords_to_alg(r, c)

        try:
            if promos:
                choice = self.ask_promotion()
                if choice is None:
                    self.info_var.set("Promotion canceled")
                    return
                in_check, status = self.game.move(from_alg, to_alg + choice)
            else:
                in_check, status = self.game.move(from_alg, to_alg)

            msg = ""
            if in_check:
                msg = "Check"
            if status == "checkmate":
                msg = "Checkmate"
            elif status == "stalemate":
                msg = "Stalemate"

            self.info_var.set(msg)
            self.selected = None
            self.legal_targets = set()
            self.refresh()

            if status in ("checkmate", "stalemate"):
                messagebox.showinfo("Game Over", f"{status}")
            else:
                self.root.after(50, self.maybe_ai_autoplay)
        except Exception as e:
            self.info_var.set(str(e))
            self.refresh()


def run_gui():
    """
    Functie helper care porneste interfata grafica.
    Creeaza fereastra principala si intra in loop-ul Tkinter.
    """
    root = tk.Tk()
    ChessGUI(root)
    root.mainloop()
