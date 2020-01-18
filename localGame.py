import sys
import time
import Reversi
import joblib
import os
import random
from copy import deepcopy
from io import StringIO
from players.RandomPlayer import RandomPlayer
from players.AlphaBetaPlayer import AlphaBetaPlayer
from players.MCTSPlayer import MCTSPlayer, MCTS


def simulate_multiple_games(mcts, board, n_games):

    winners = []
    for g in range(1, 1+n_games):
        # Assign random color to each player
        color_mcts = random.choice([board._WHITE, board._BLACK])
        color_ab = board._flip(color_mcts)

        mcts_player, ab_player = MCTSPlayer(
            color_mcts, mcts, board_size=board._boardsize), AlphaBetaPlayer(color_ab, board_size=board._boardsize)

        sys.stdout = open(os.devnull, 'w')
        b = deepcopy(board)
        winner = play(mcts_player, ab_player, b)
        sys.stdout = sys.__stdout__
        if winner == mcts_player.color:
            winner_str = "mcts"
        elif winner == ab_player.color:
            winner_str = "ab"
        else:
            winner_str = "tie"

        winners.append(winner_str)

        if g % 1 == 0:
            print("End of game", g, winner_str, "won.")

    print("End of", n_games, "simulations\n", "-"*50)
    print("MCTS wins:", winners.count("mcts"), ", AlphaBeta wins:",
          winners.count("ab"), ", Ties:", winners.count("tie"))


def play(player1, player2, b):
    # Black begins
    next_player, other_player = (
        player1, player2) if player1.color == b._BLACK else (player2, player1)
    nbmoves = 1

    # total real time for each player
    totalTime = {p.getPlayerName(): 0 for p in [next_player, other_player]}

    print(b.legal_moves())
    while not b.is_game_over():
        print("Referee Board:")
        print(b)
        print("Before move", nbmoves)
        print("Legal Moves: ", b.legal_moves())

        nbmoves += 1

        currentTime = time.time()
        move = next_player.getPlayerMove()
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
    (nbwhites, nbblacks) = b.get_nb_coins()
    winner = b.get_winner()
    print("Time:", totalTime)
    print("Winner: ", end="")
    if winner == b._WHITE:
        print("WHITE")
    elif winner == b._BLACK:
        print("BLACK")
    else:
        print("DEUCE")
    print("Final is: ", nbwhites, "whites and ", nbblacks, "blacks")
    return winner


def load_mcts(path):
    return joblib.load(path)


def train(n_iter=100, b_size=8):
    b = Reversi.Board(board_size=b_size)
    mcts = MCTS()
    mcts.train(b, n_iter)
    mcts.save(f"mcts_save/mcts_{n_iter}_iter_size_{b_size}.pickle")


def test(mcts_name, n_games=4, b_size=8):
    b = Reversi.Board(board_size=b_size)
    mcts = load_mcts(mcts_name)
    simulate_multiple_games(mcts, b, n_games=n_games)


if __name__ == "__main__":
    # train(10000, b_size=8)

    test("mcts_save/mcts_10000_iter_size_8.pickle", b_size=8, n_games=60)
    # mcts = load_mcts("mcts_save/mcts_10000_iter_size_8.pickle")

    # b_size = 8
    # b = Reversi.Board(board_size=b_size)
    # player1, player2 = AlphaBetaPlayer(
    #     b ._BLACK, board_size=b_size, max_time=10), RandomPlayer(
    #     b ._WHITE, board_size=b_size)
    # play(player1, player2, b)

    # b = Reversi.Board(board_size=4)
    # mcts = MCTS()
    # mcts.train(b, 15, verbose=False)
    # mcts.show()
    # print(mcts._root)
    # for _, child in mcts._root.children.items():
    #     print(child)
