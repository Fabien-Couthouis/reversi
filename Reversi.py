# -*- coding: utf-8 -*-

''' Fichier de règles du Reversi pour le tournoi Masters Info 2019 en IA.
    Certaines parties de ce code sont fortement inspirée de 
    https://inventwithpython.com/chapter15.html

    '''


class Board:
    _BLACK = 1
    _WHITE = 2
    _EMPTY = 0
    _LIMIT = -1

    # Attention, la taille du plateau est donnée en paramètre
    def __init__(self, board_size=8):
        self._nbWHITE = 2
        self._nbBLACK = 2
        self._nextPlayer = self._BLACK
        self._boardsize = board_size
        self._board = []
        for _ in range(self._boardsize):
            self._board.append([self._EMPTY] * self._boardsize)
        _middle = int(self._boardsize / 2)
        self._board[_middle-1][_middle-1] = self._BLACK
        self._board[_middle-1][_middle] = self._WHITE
        self._board[_middle][_middle-1] = self._WHITE
        self._board[_middle][_middle] = self._BLACK

        self._stack = []
        self._successivePass = 0

    def reset(self):
        self.__init__()

    def get_board_size(self):
        "Return board size"
        return self._boardsize

    def get_board(self):
        return self._board

    def get_next_player(self):
        return self._nextPlayer

    # Donne le nombre de pieces de blanc et noir sur le plateau
    # sous forme de tuple (blancs, noirs)
    # Peut être utilisé si le jeu est terminé pour déterminer le vainqueur
    def get_nb_coins(self, player=None):
        """
        Get nb of coins on the board
        Arguments: player (optionak, default=None): None or Board._BLACK or Board._WHITE
        Return: Number of coins for specified player. If set to none return a tuple (nb_white, nb_black)
        """
        if player == self._BLACK:
            return self._nbBLACK
        elif player == self._WHITE:
            return self._nbWHITE
        else:
            return self._nbWHITE, self._nbBLACK

    def get_total_coins(self):
        return self._nbWHITE + self._nbBLACK

    def is_valid_move(self, player, x, y):
        "Check if player can play move in (x,y)"
        if x == -1 and y == -1:
            return not self.at_least_one_legal_move(player)
        return self.lazyTest_ValidMove(player, x, y)

    def _isOnBoard(self, x, y):
        return x >= 0 and x < self._boardsize and y >= 0 and y < self._boardsize

    def testAndBuild_ValidMove(self, player, xstart, ystart):
        """
        Get list of coins to return if move is valid, else return False
        inspired by https://inventwithpython.com/chapter15.html
        """
        if self._board[xstart][ystart] != self._EMPTY or not self._isOnBoard(xstart, ystart):
            print("ILLEGAL MOVE")
            return False

        # On pourra remettre _EMPTY ensuite
        self._board[xstart][ystart] = player

        otherPlayer = self._flip(player)

        # Si au moins un coup est valide, on collecte ici toutes les pieces a retourner
        tilesToFlip = []
        for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            x, y = xstart, ystart
            x += xdirection
            y += ydirection
            if self._isOnBoard(x, y) and self._board[x][y] == otherPlayer:
                # There is a piece belonging to the other player next to our piece.
                x += xdirection
                y += ydirection
                if not self._isOnBoard(x, y):
                    continue
                while self._board[x][y] == otherPlayer:
                    x += xdirection
                    y += ydirection
                    # break out of while loop, then continue in for loop
                    if not self._isOnBoard(x, y):
                        break
                if not self._isOnBoard(x, y):
                    continue
                # We are sure we can at least build this move. Let's collect
                if self._board[x][y] == player:
                    while True:
                        x -= xdirection
                        y -= ydirection
                        if x == xstart and y == ystart:
                            break
                        tilesToFlip.append([x, y])

        self._board[xstart][ystart] = self._EMPTY  # restore the empty space
        # If no tiles were flipped, this is not a valid move.
        if len(tilesToFlip) == 0:
            return False
        return tilesToFlip

    # Pareil que ci-dessus mais ne revoie que vrai / faux (permet de tester plus rapidement)
    def lazyTest_ValidMove(self, player, xstart, ystart):
        """
        Check if move is valid
        """
        if self._board[xstart][ystart] != self._EMPTY or not self._isOnBoard(xstart, ystart):
            return False

        # On pourra remettre _EMPTY ensuite
        self._board[xstart][ystart] = player

        otherPlayer = self._flip(player)

        for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            x, y = xstart, ystart
            x += xdirection
            y += ydirection
            if self._isOnBoard(x, y) and self._board[x][y] == otherPlayer:
                # There is a piece belonging to the other player next to our piece.
                x += xdirection
                y += ydirection
                if not self._isOnBoard(x, y):
                    continue
                while self._board[x][y] == otherPlayer:
                    x += xdirection
                    y += ydirection
                    # break out of while loop, then continue in for loop
                    if not self._isOnBoard(x, y):
                        break
                if not self._isOnBoard(x, y):  # On a au moins
                    continue
                # We are sure we can at least build this move.
                if self._board[x][y] == player:
                    self._board[xstart][ystart] = self._EMPTY
                    return True

        self._board[xstart][ystart] = self._EMPTY  # restore the empty space
        return False

    def _flip(self, player):
        "Invert player"
        if player == self._BLACK:
            return self._WHITE
        return self._BLACK

    def is_game_over(self):
        if self.at_least_one_legal_move(self._nextPlayer):
            return False
        if self.at_least_one_legal_move(self._flip(self._nextPlayer)):
            return False
        return True

    def get_winner(self):
        "Return winner player if game is overs, else None"
        if not self.is_game_over():
            return None

        nbwhites, nbblacks = self.get_nb_coins()
        if nbwhites < nbblacks:
            winner = self._BLACK
        elif nbwhites > nbblacks:
            winner = self._WHITE
        else:
            winner = 0  # tie
        return winner

    def push(self, move):
        "Play the move on board"
        [player, x, y] = move
        # print("player", player, "next", self._nextPlayer)
        assert player == self._nextPlayer
        if x == -1 and y == -1:  # pass
            self._nextPlayer = self._flip(player)
            self._stack.append([move, self._successivePass, []])
            self._successivePass += 1
            return

        toflip = self.testAndBuild_ValidMove(player, x, y)
        assert toflip != False

        self._stack.append([move, self._successivePass, toflip])
        self._successivePass = 0
        self._board[x][y] = player

        for xf, yf in toflip:
            self._board[xf][yf] = self._flip(self._board[xf][yf])

        if player == self._BLACK:
            self._nbBLACK += 1 + len(toflip)
            self._nbWHITE -= len(toflip)
            self._nextPlayer = self._WHITE
        else:
            self._nbWHITE += 1 + len(toflip)
            self._nbBLACK -= len(toflip)
            self._nextPlayer = self._BLACK

    def pop(self):
        "Cancel last move on board"
        [move, self._successivePass, toflip] = self._stack.pop()
        [player, x, y] = move
        self._nextPlayer = player
        if len(toflip) == 0:  # pass
            assert x == -1 and y == -1
            return
        self._board[x][y] = self._EMPTY
        for xf, yf in toflip:
            self._board[xf][yf] = self._flip(self._board[xf][yf])
        if player == self._BLACK:
            self._nbBLACK -= 1 + len(toflip)
            self._nbWHITE += len(toflip)
        else:
            self._nbWHITE -= 1 + len(toflip)
            self._nbBLACK += len(toflip)

    def at_least_one_legal_move(self, player):
        "Can we play at least on move?"
        for x in range(0, self._boardsize):
            for y in range(0, self._boardsize):
                if self.lazyTest_ValidMove(player, x, y):
                    return True
        return False

    def legal_moves(self, player="default"):
        'Get all possible plays for current player if player="default"'
        if player == "default":
            player = self._nextPlayer
        else:
            player = self._flip(self._nextPlayer)
        moves = []
        for x in range(0, self._boardsize):
            for y in range(0, self._boardsize):
                if self.lazyTest_ValidMove(player, x, y):
                    moves.append([player, x, y])
        if len(moves) is 0:
            moves = [[player, -1, -1]]  # We shall pass
        return moves

    # Exemple d'heuristique tres simple : compte simplement les pieces
    def heuristic(self, player=None):
        if player is None:
            player = self._nextPlayer
        if player is self._WHITE:
            return self._nbWHITE - self._nbBLACK
        return self._nbBLACK - self._nbWHITE

    def _piece2str(self, c):
        if c == self._WHITE:
            return 'O'
        elif c == self._BLACK:
            return 'X'
        else:
            return '.'

    def __str__(self):
        toreturn = ""
        for l in self._board:
            for c in l:
                toreturn += self._piece2str(c)
            toreturn += "\n"
        toreturn += "Next player: " + \
            ("BLACK" if self._nextPlayer == self._BLACK else "WHITE") + "\n"
        toreturn += str(self._nbBLACK) + " blacks and " + \
            str(self._nbWHITE) + " whites on board\n"
        toreturn += "(successive pass: " + str(self._successivePass) + " )"
        return toreturn

    __repr__ = __str__
