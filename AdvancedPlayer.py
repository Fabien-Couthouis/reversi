# -*- coding: utf-8 -*-

import time
import Reversi
from Timeout import TimeOut
from random import randint
from playerInterface import *


class AdvancedPlayer(PlayerInterface):

    def __init__(self, color):
        self._board = Reversi.Board(10)
        self.color = None
        self._opponent = None
        self._is_white = None
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
        # random
        # moves = self._board.legal_moves()
        # move = moves[randint(0, len(moves)-1)]
        # move = self.iterative_deepening(self.negaMax, 3)[1]
        move = self.negaMax(horizon=3)[1]
        return move

    def playOpponentMove(self, x, y):
        assert(self._board.is_valid_move(self._opponent, x, y))
        print("Opponent played ", (x, y))
        self._board.push([self._opponent, x, y])

    def newGame(self, color):
        self.color = color
        self._opponent = self._board._BLACK if color == self._board._WHITE else self._board._WHITE
        self._is_white = (self.color == self._board._WHITE)

    def endGame(self, winner):
        if self.color == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")

    def naive_heuristic(self):
        return self._board.heuristic()

    def heuristic(self):
        # return 0
        # inspired from https://github.com/Jules-Lion/kurwa/blob/master/Dokumentation/An Analysis of Heuristics in Othello.pdf
        # Coin Parity heuristic
        nb_coins_p, nb_coins_o = self._board.get_nb_pieces(
            self.color), self._board.get_nb_pieces(self._opponent)
        coins_h = self.get_heuristic_value(nb_coins_p, nb_coins_o)

        # Mobility heuristic
        nb_moves_p, nb_moves_o = self._board.get_nb_legal_moves()
        mobility_h = self.get_heuristic_value(nb_moves_p, nb_moves_o)

        # Corners Captured heuristic
        corners_p, corners_o = self._board.get_corners()
        nb_corners_p, nb_corners_o = len(corners_p), len(corners_o)

        corners_h = self.get_heuristic_value(nb_corners_p, nb_corners_o)

        # Stability
        # stability_p, stability_o = self._board.get_stability(
        #     corners_p, corners_o, nb_coins_p, nb_coins_o)
        # stability_h = self.get_heuristic_value(stability_p, stability_o)
        stability_h = 0

        score = (10 * coins_h) + (801.724 * corners_h) + (382.026 * -12.5 *
                                                          (nb_coins_p - nb_coins_o)) + (78.922 * mobility_h) + (74.396 * stability_h)
        return score

    def get_heuristic_value(self, value_p, value_o):
        if value_p + value_o == 0:
            return 0
        else:
            return 100 * (value_p - value_o) / (value_p + value_o)

    def estimate_end(self, is_white):
        if self._board.is_game_over():
            (nb_white, nb_black) = self._board.get_nb_pieces()
            if nb_white == nb_black:
                val = 0
            elif nb_white > nb_black:
                val = 1000 if is_white else -1000
            else:
                val = -1000 if is_white else 1000
        else:
            val = self.heuristic()
        return (val, None)

    def negaMax(self, is_white=None, horizon=10):
        if is_white is None:
            is_white = self._is_white
        if horizon == 0 or self._board.is_game_over():
            return self.estimate_end(is_white)

        best = None
        best_action = None
        for m in self._board.legal_moves():
            self._board.push(m)
            (nm, _) = self.negaMax(not is_white, horizon - 1)
            nm = -nm
            if best is None or nm > best:
                best = nm
                best_action = m
            self._board.pop()

        return (best, best_action)

    # Neg Alpha Beta avec version d'echec
    def negAlphaBeta(self, alpha=None, beta=None, is_white=None, horizon=10):
        # Initialisation
        if is_white is None:
            is_white = self._is_white
        if alpha is None:
            alpha = -1e-8
        if beta is None:
            beta = 1e-8

        if horizon == 0 or self._board.is_game_over():
            return self.estimate_end(is_white)

        best = None
        best_action = None
        for m in self._board.legal_moves():
            self._board.push(m)
            (nm, _) = self.negAlphaBeta(-beta, -alpha,
                                        not is_white, horizon - 1)
            nm = -nm
            if best is None or nm > best:
                best = nm
                best_action = m
                if best > alpha:
                    alpha = best
                    if alpha > beta:  # Coupure
                        self._board.pop()
                        return (best, best_action)
            self._board.pop()

        return (best, best_action)

    def iterative_deepening(self, callback, max_time):
        horizon = 1
        try:
            TimeOut(max_time).start()
            while True:
                bestmove = callback(horizon=horizon)
                horizon += 1

        except TimeOut.TimeOutException as e:
            # Timed out
            print(e)
            pass

        return bestmove
