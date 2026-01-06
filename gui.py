import tkinter as tk
from tkinter import messagebox

from game import ChessGame
from pieces import Color, PieceType, Piece


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


class ChessGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chess")

        self.game = ChessGame()

        self.selected = None
        self.legal_map = {}
        self.legal_targets = set()

        self.status_var = tk.StringVar()
        self.turn_var = tk.StringVar()
        self.info_var = tk.StringVar()

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
        control.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        tk.Button(control, text="New Game", command=self.new_game).pack(side=tk.LEFT)
        tk.Button(control, text="Reset Selection", command=self.reset_selection).pack(side=tk.LEFT, padx=8)

        self.refresh()

    def new_game(self):
        self.game = ChessGame()
        self.reset_selection()
        self.refresh()

    def reset_selection(self):
        self.selected = None
        self.legal_map = {}
        self.legal_targets = set()
        self.info_var.set("")
        self.refresh()

    def piece_to_text(self, piece):
        if piece is None:
            return ""
        return UNICODE_MAP.get(piece.symbol, piece.symbol)

    def square_colors(self, r, c):
        light = (r + c) % 2 == 0
        return "#EEEED2" if light else "#769656"

    def refresh(self):
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
        self.legal_map = {}
        all_moves = self.game.get_all_legal_moves(self.game.current_player)
        for (from_pos, to_pos, promo) in all_moves:
            self.legal_map.setdefault(from_pos, []).append((to_pos, promo))

        if self.selected is None:
            self.legal_targets = set()
        else:
            self.legal_targets = set(tp for (tp, _promo) in self.legal_map.get(self.selected, []))

    def coords_to_alg(self, r, c):
        file = chr(ord("a") + c)
        rank = str(r + 1)
        return file + rank

    def ask_promotion(self):
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

    def on_square_click(self, r, c):
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
        except Exception as e:
            self.info_var.set(str(e))
            self.refresh()


def run_gui():
    root = tk.Tk()
    ChessGUI(root)
    root.mainloop()
