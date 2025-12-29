from game import ChessGame
from pieces import Color, PieceType, Piece


print("Test castling:")
g1 = ChessGame()
g1.move("g1", "f3")
g1.move("g8", "f6")
g1.move("e2", "e4")
g1.move("e7", "e5")
g1.move("f1", "e2")
g1.move("b8", "c6")
in_check, status = g1.move("e1", "g1")
print(g1.board)
print("Castling ok, status:", status)

print("\nTest en passant:")
g2 = ChessGame()
g2.move("e2", "e4")
g2.move("a7", "a6")
g2.move("e4", "e5")
g2.move("d7", "d5")
in_check, status = g2.move("e5", "d6")
print(g2.board)
print("En passant ok, status:", status)

print("\nTest promotion:")
g3 = ChessGame()
for r in range(8):
    for c in range(8):
        g3.board.set_piece(r, c, None)
g3.board.set_piece(0, 4, Piece(PieceType.KING, Color.WHITE))
g3.board.set_piece(7, 4, Piece(PieceType.KING, Color.BLACK))
g3.board.set_piece(6, 0, Piece(PieceType.PAWN, Color.WHITE))
g3.current_player = Color.WHITE
in_check, status = g3.move("a7", "a8Q")
print(g3.board)
print("Promotion ok, status:", status)
print("Istoric:", g3.history)
