from game import ChessGame


class Replay:
    """
    Clasa care permite redarea (replay) unei partide de sah.

    Replay reconstruieste jocul de la inceput si permite:
    - avansarea mutarilor una cate una
    - revenirea inapoi la mutari anterioare

    Se bazeaza pe snapshot-uri ale jocului pentru a putea
    merge inainte si inapoi in siguranta.
    """

    def __init__(self, game: ChessGame):
        """
        Initializeaza un replay pe baza unui joc deja jucat.

        :param game: instanta ChessGame din care se preia istoricul mutarilor
        """
        self.base = ChessGame()
        self.moves = [(mv.from_pos, mv.to_pos) for mv in game.history]
        self.snaps = [self.base.snapshot()]
        self.index = 0

    def rebuild(self):
        """
        Reseteaza complet replay-ul.

        Reface jocul de la pozitia initiala si sterge
        progresul de redare.
        """
        self.base = ChessGame()
        self.snaps = [self.base.snapshot()]
        self.index = 0

    def can_forward(self):
        """
        Verifica daca se poate avansa la urmatoarea mutare.

        :return: True daca mai exista mutari de redat, False altfel
        """
        return self.index < len(self.moves)

    def can_back(self):
        """
        Verifica daca se poate reveni la mutarea anterioara.

        :return: True daca indexul este mai mare decat 0, False altfel
        """
        return self.index > 0

    def forward(self):
        """
        Avanseaza replay-ul cu o mutare.

        Aplica urmatoarea mutare pe tabla si salveaza un snapshot nou.

        :return: True daca mutarea a fost aplicata, False daca nu mai exista mutari
        """
        if not self.can_forward():
            return False

        f, t = self.moves[self.index]
        self.base.move(f, t)
        self.snaps.append(self.base.snapshot())
        self.index += 1
        return True

    def back(self):
        """
        Revine la mutarea anterioara din replay.

        Restaureaza snapshot-ul corespunzator pozitiei precedente.

        :return: True daca revenirea a avut loc, False daca nu se poate merge inapoi
        """
        if not self.can_back():
            return False

        self.index -= 1
        snap = self.snaps[self.index]
        self.base.restore(snap)
        self.snaps = self.snaps[: self.index + 1]
        return True
