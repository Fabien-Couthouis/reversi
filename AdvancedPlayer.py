# -*- coding: utf-8 -*-

import time
import Reversi
from Heuristics import Heuristics
from random import randint
from playerInterface import *


class AdvancedPlayer(PlayerInterface):

    def __init__(self, color):
        self._board = Reversi.Board(10)
        self.color = None
        self._opponent = None
        self._is_white = None
        self.heuristics = None
        self.newGame(color)

    def getPlayerName(self):
        return "Jean-Claude"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return (-1, -1)
        move = self.get_move()
        self._board.push(move)
        print("I am playing ", move)
        (c, x, y) = move
        assert(c == self.color)
        print("My current board :")
        print(self._board)
        return (x, y)

    def get_move(self):
        move = self.iterative_deepening(self.negAlphaBeta, 1)
        return move

    def playOpponentMove(self, x, y):
        assert(self._board.is_valid_move(self._opponent, x, y))
        print("Opponent played ", (x, y))
        self._board.push([self._opponent, x, y])

    def newGame(self, color):
        self.color = color
        self._opponent = self._board._BLACK if color == self._board._WHITE else self._board._WHITE
        self._is_white = (self.color == self._board._WHITE)
        self.heuristics = Heuristics(self._board, self.color, self._opponent)

    def endGame(self, winner):
        if self.color == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")

    def naive_heuristic(self):
        return self._board.heuristic()

    def heuristic(self):
        return self.heuristics.total_heuristic()
        # return self.naive_heuristic()

    def estimate_end(self, is_white):
        if self._board.is_game_over():
            (nb_white, nb_black) = self._board.get_nb_coins()
            if nb_white == nb_black:
                val = 0
            elif nb_white > nb_black:
                val = 1000 if is_white else -1000
            else:
                val = -1000 if is_white else 1000
        else:
            val = self.heuristic()
        return (val, None)

    def negaMax(self, is_white=None, horizon=10, timeout=None):
        # Check if timed out
        if timeout is not None and timeout < time.time():
            return None, None
        if is_white is None:
            is_white = self._is_white
        if horizon == 0 or self._board.is_game_over():
            return self.estimate_end(is_white)

        best, best_action = None, None
        for m in self._board.legal_moves():
            self._board.push(m)
            (nm, _) = self.negaMax(not is_white, horizon - 1, timeout)

            # Timed out
            if nm is None:
                self._board.pop()
                return None, None

            nm = -nm
            if best is None or nm > best:
                best = nm
                best_action = m
            self._board.pop()

        return (best, best_action)

    # Neg Alpha Beta avec version d'echec
    def negAlphaBeta(self, alpha=None, beta=None, is_white=None, horizon=10, timeout=None):
        # Check if timed out
        if timeout is not None and timeout < time.time():
            return None, None

        # Initialisation
        is_white = self._is_white if is_white is None else is_white
        alpha = -1e-8 if alpha is None else alpha
        beta = +1e-8 if beta is None else beta

        if horizon == 0 or self._board.is_game_over():
            return self.estimate_end(is_white)

        best, best_action = None, None
        for m in self._board.legal_moves():
            self._board.push(m)
            (nm, _) = self.negAlphaBeta(-beta, -alpha,
                                        not is_white, horizon - 1)
            # Timed out
            if nm is None:
                self._board.pop()
                return None, None

            nm = -nm
            if best is None or nm > best:
                best, best_action = nm, m
                if best > alpha:
                    alpha = best
                    if alpha > beta:  # pruning
                        self._board.pop()
                        return (best, best_action)
            self._board.pop()

        return (best, best_action)

    def iterative_deepening(self, callback, max_time):
        horizon = 1
        timeout = time.time() + max_time
        res = True
        start = time.time()
        while res is not None:
            _, res = callback(horizon=horizon, timeout=timeout)
            horizon += 1
            if res is not None:
                bestmove = res
        print("Took", time.time()-start)

        return bestmove
