from game import ChessGame


def export_pgn_like(game: ChessGame) -> str:
    lines = []
    for i, mv in enumerate(game.history):
        if i % 2 == 0:
            lines.append(f"{(i // 2) + 1}. {mv.from_pos}{mv.to_pos}")
        else:
            lines[-1] = lines[-1] + f" {mv.from_pos}{mv.to_pos}"
    return "\n".join(lines) + ("\n" if lines else "")


def export_moves_list(game: ChessGame):
    return [mv.from_pos + mv.to_pos for mv in game.history]


def save_pgn_like(game: ChessGame, path: str):
    data = export_pgn_like(game)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)


def load_pgn_like(path: str) -> ChessGame:
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
