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


def simulate_multiple_games(player1, player2, board, n_games):

    winners = []
    for g in range(1, 1+n_games):
        # Assign random color to each player
        player1.newGame(random.choice([board._WHITE, board._BLACK]))
        player2.newGame(board._flip(player1.color))

        sys.stdout = open(os.devnull, 'w')
        b = deepcopy(board)
        winner = play(player1, player2, b)
        sys.stdout = sys.__stdout__
        if winner == player1.color:
            winner_str = player1.getPlayerName()
        elif winner == player2.color:
            winner_str = player2.getPlayerName()
        else:
            winner_str = "tie"

        winners.append(winner_str)

        if g % 1 == 0:
            print("End of game", g, "winner:", winner_str)

    print("End of", n_games, "simulations\n", "-"*50)
    print("Player1:", player1.getPlayerName(), "wins:", winners.count(player1.getPlayerName()), ", Player2", player2.getPlayerName(), "wins:",
          winners.count(player2.getPlayerName()), ", Ties:", winners.count("tie"))


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


if __name__ == "__main__":
    # #Train mcts for n iterations
    # n = 10
    # train(10, b_size=8) #uncomment to retrain the mcts

    # #Test mcts vs alphabeta for 120 games
    board = Reversi.Board(8)
    mcts = load_mcts("mcts_save/mcts_10000_iter_size_8.pickle")
    p1, p2 = MCTSPlayer(
        0, mcts, board._boardsize, max_time=120), AlphaBetaPlayer(1, board._boardsize, max_time=120)

    simulate_multiple_games(p1, p2, board, n_games=30)

    # # Show graph for 5 iterations
    # mcts = load_mcts("mcts_save/mcts_5_iter_size_8.pickle")
    # mcts.show()
