from game import ChessGame
from pieces import Color

game = ChessGame()

print("Pozitie initiala:")
print(game.board)
print("Randul este:", game.current_player)

print("\n1. e2 -> e4 (alb)")
game.move("e2", "e4")
print(game.board)
print("Randul este:", game.current_player)

print("\n1... e7 -> e5 (negru)")
game.move("e7", "e5")
print(game.board)
print("Randul este:", game.current_player)

print("\n2. Qd1 -> h5 (alb)")
game.move("d1", "h5")
print(game.board)
print("Randul este:", game.current_player)

print("\n2... Nb8 -> c6 (negru, mutare oarecare)")
game.move("b8", "c6")
print(game.board)
print("Randul este:", game.current_player)

print("\n3. Qh5 -> e5 (alb, captura + sah)")
in_check = game.move("h5", "e5")
print(game.board)
print("Negrul este în sah? ->", in_check)
print("Randul este:", game.current_player)

print("\nTest: incercam o mutare ilegala care lasa regele alb în sah:")

try:
    game2 = ChessGame()
    print(game2.board)

    game2.move("e2", "e4")
    game2.move("d8", "h4")
    print(game2.board)

except Exception as e:
    print("A apărut o eroare (cum era de așteptat):", e)


print("\nIstoric mutări:", game.history)

