from game import ChessGame


class Replay:
    def __init__(self, game: ChessGame):
        self.base = ChessGame()
        self.moves = [(mv.from_pos, mv.to_pos) for mv in game.history]
        self.snaps = [self.base.snapshot()]
        self.index = 0

    def rebuild(self):
        self.base = ChessGame()
        self.snaps = [self.base.snapshot()]
        self.index = 0

    def can_forward(self):
        return self.index < len(self.moves)

    def can_back(self):
        return self.index > 0

    def forward(self):
        if not self.can_forward():
            return False
        f, t = self.moves[self.index]
        self.base.move(f, t)
        self.snaps.append(self.base.snapshot())
        self.index += 1
        return True

    def back(self):
        if not self.can_back():
            return False
        self.index -= 1
        snap = self.snaps[self.index]
        self.base.restore(snap)
        self.snaps = self.snaps[: self.index + 1]
        return True
