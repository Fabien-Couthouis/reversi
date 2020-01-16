# -*- coding: utf-8 -*-

import time
import Reversi
from random import randint
from playerInterface import *


class RandomPlayer(PlayerInterface):

    def __init__(self, color, board_size=8):
        self._board = Reversi.Board(board_size)
        self.color = None
        self.newGame(color)

    def getPlayerName(self):
        return "Franky Vincent"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return (-1, -1)
        moves = [m for m in self._board.legal_moves()]
        move = moves[randint(0, len(moves)-1)]
        self._board.push(move)
        print("I am playing ", move)
        (c, x, y) = move
        print("color:", self.color, " c:", c)

        assert(c == self.color)
        print("My current board :")
        print(self._board)
        return (x, y)

    def playOpponentMove(self, x, y):
        assert(self._board.is_valid_move(self._opponent, x, y))
        print("Opponent played ", (x, y))
        self._board.push([self._opponent, x, y])

    def newGame(self, color):
        self.color = color
        self._opponent = 1 if color == 2 else 2

    def endGame(self, winner):
        if self.color == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")
