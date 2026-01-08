from game import ChessGame


def export_pgn_like(game: ChessGame) -> str:
    """
    Exporta istoricul mutarilor unui joc intr-un format text asemanator PGN.

    Formatul rezultat este de tip:
    1. e2e4 e7e5
    2. g1f3 b8c6

    Fiecare linie contine mutarea albului si a negrului.
    """
    lines = []
    for i, mv in enumerate(game.history):
        if i % 2 == 0:   # daca e mutarea albului
            lines.append(f"{(i // 2) + 1}. {mv.from_pos}{mv.to_pos}")
        else:           # daca e mutarea negrului
            lines[-1] = lines[-1] + f" {mv.from_pos}{mv.to_pos}"
    return "\n".join(lines) + ("\n" if lines else "")


def export_moves_list(game: ChessGame):
    """
    Returneaza lista simpla de mutari din joc.

    Fiecare mutare este un string de forma:
    e2e4, e7e5, g1f3 etc.

    :param game: instanta ChessGame
    :return: lista de string-uri cu mutari
    """
    return [mv.from_pos + mv.to_pos for mv in game.history]


def save_pgn_like(game: ChessGame, path: str):
    """
    Salveaza partida curenta intr-un fisier text in format PGN-like.

    :param game: instanta ChessGame care contine istoricul mutarilor
    :param path: calea catre fisierul unde se salveaza datele
    """
    data = export_pgn_like(game)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)


def load_pgn_like(path: str) -> ChessGame:
    """
    Incarca o partida dintr-un fisier PGN-like.

    Creeaza un joc nou si aplica mutarile una cate una,
    in ordinea in care apar in fisier.

    :param path: calea catre fisierul PGN-like
    :return: instanta ChessGame refacuta din fisier
    """
    g = ChessGame()
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        return g

    tokens = []
    for line in text.splitlines():
        parts = line.strip().split()
        for p in parts:
            if p.endswith("."):
                continue
            tokens.append(p)

    for tok in tokens:
        if len(tok) < 4:
            continue
        from_sq = tok[:2]
        to_sq = tok[2:]
        g.move(from_sq, to_sq)

    return g
