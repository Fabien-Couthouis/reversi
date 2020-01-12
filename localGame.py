import sys
import time
import Reversi
from io import StringIO
from DefaultPlayer import DefaultPlayer
from AdvancedPlayer import AdvancedPlayer
from MCTSPlayer import MCTSPlayer, MCTS


def main():
    b = Reversi.Board(10)

    next_player, other_player = DefaultPlayer(
        b._BLACK), AdvancedPlayer(b._WHITE)
    players = [next_player, other_player]
    nbmoves = 1

    # total real time for each player
    totalTime = {p.getPlayerName(): 20 for p in players}
    outputs = {p.getPlayerName(): "" for p in players}
    sysstdout = sys.stdout
    stringio = StringIO()

    print(b.legal_moves())
    while not b.is_game_over():
        print("Referee Board:")
        print(b)
        print("Before move", nbmoves)
        print("Legal Moves: ", b.legal_moves())
        print(0)

        nbmoves += 1

        currentTime = time.time()

        # sys.stdout = stringio
        move = next_player.getPlayerMove()

        # sys.stdout = sysstdout
        # playeroutput = "\r" + stringio.getvalue()
        # stringio.truncate(0)
        # print((str(next_player) + "] ").join(playeroutput.splitlines(True)))
        # outputs[next_player.getPlayerName()] += playeroutput
        totalTime[next_player.getPlayerName()] += time.time() - currentTime
        print(next_player.color,
              next_player.getPlayerName(), "plays" + str(move))
        (x, y) = move
        if not b.is_valid_move(next_player.color, x, y):
            print(other_player, next_player, next_player.color)
            print("Problem: illegal move")
            break
        b.push([next_player.color, x, y])
        other_player.playOpponentMove(x, y)

        # Invert players
        next_player, other_player = other_player, next_player

    print(b)

    print("The game is over")
    print(b)
    (nbwhites, nbblacks) = b.get_nb_coins()
    print("Time:", totalTime)
    print("Winner: ", end="")
    if nbwhites > nbblacks:
        print("WHITE")
    elif nbblacks > nbwhites:
        print("BLACK")
    else:
        print("DEUCE")
    print("Final is: ", nbwhites, "whites and ", nbblacks, "blacks")


if __name__ == "__main__":
    # main()
    b = Reversi.Board(10)
    # player = MCTSPlayer(b._BLACK)
    # print(player.start_self_play())
    mcts = MCTS()
    mcts.start_self_play(b, n_games=100)
    mcts.show(save_image=True)
