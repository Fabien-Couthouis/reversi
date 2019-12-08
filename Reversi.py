# -*- coding: utf-8 -*-

''' Fichier de règles du Reversi pour le tournoi Masters Info 2019 en IA.
    Certaines parties de ce code sont fortement inspirée de 
    https://inventwithpython.com/chapter15.html

    '''


class Board:
    _BLACK = 1
    _WHITE = 2
    _EMPTY = 0

    # Attention, la taille du plateau est donnée en paramètre
    def __init__(self, boardsize=8):
        self._nbWHITE = 2
        self._nbBLACK = 2
        self._nextPlayer = self._BLACK
        self._boardsize = boardsize
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

    # Donne la taille du plateau
    def get_board_size(self):
        return self._boardsize

    # Donne le nombre de pieces de blanc et noir sur le plateau
    # sous forme de tuple (blancs, noirs)
    # Peut être utilisé si le jeu est terminé pour déterminer le vainqueur
    def get_nb_pieces(self, player=None):
        if player == self._BLACK:
            return self._nbBLACK
        elif player == self._WHITE:
            return self._nbWHITE
        else:
            return self._nbBLACK, self._nbWHITE

    # Vérifie si player a le droit de jouer en (x,y)
    def is_valid_move(self, player, x, y):
        if x == -1 and y == -1:
            return not self.at_least_one_legal_move(player)
        return self.lazyTest_ValidMove(player, x, y)

    def _isOnBoard(self, x, y):
        return x >= 0 and x < self._boardsize and y >= 0 and y < self._boardsize

    # Renvoie la liste des pieces a retourner si le coup est valide
    # Sinon renvoie False
    # Ce code est très fortement inspiré de https://inventwithpython.com/chapter15.html
    # y faire référence dans tous les cas
    def testAndBuild_ValidMove(self, player, xstart, ystart):
        if self._board[xstart][ystart] != self._EMPTY or not self._isOnBoard(xstart, ystart):
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
        if player == self._BLACK:
            return self._WHITE
        return self._BLACK

    def is_game_over(self):
        if self.at_least_one_legal_move(self._nextPlayer):
            return False
        if self.at_least_one_legal_move(self._flip(self._nextPlayer)):
            return False
        return True

    def push(self, move):
        [player, x, y] = move
        assert player == self._nextPlayer
        if x == -1 and y == -1:  # pass
            self._nextPlayer = self._flip(player)
            self._stack.append([move, self._successivePass, []])
            self._successivePass += 1
            return
        toflip = self.testAndBuild_ValidMove(player, x, y)
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

    # Est-ce que on peut au moins jouer un coup ?
    # Note: cette info pourrait être codée plus efficacement
    def at_least_one_legal_move(self, player):
        for x in range(0, self._boardsize):
            for y in range(0, self._boardsize):
                if self.lazyTest_ValidMove(player, x, y):
                    return True
        return False

    # ---------------------------------------------
    # Heuristic functions
    # ---------------------------------------------
    def get_nb_legal_moves(self):
        return len(self.legal_moves("default")), len(self.legal_moves("other"))

    def get_corners(self):
        player = self._nextPlayer
        other = self._flip(player)
        end = self._boardsize-1
        corners_list = [(0, 0), (0, end), (end, 0), (end, end)]
        player_corners, other_corners = [],[]
        for (x, y) in corners_list:
            if self._board[x][y] == player:
                player_corners.append((x,y))
            elif self._board[x][y] == other:
                other_corners.append((x,y))
        return player_corners, other_corners

    def get_stability(self, player_corners, other_corners, nb_coins_p, nb_coins_o):
        #inspired from http://pressibus.org/ataxx/autre/minimax/node3.html
        player = self._nextPlayer
        other = self._flip(player)
        player_stables, other_stables = [], []

        #which rows are filled?
        for x in range(self._boardsize):
            add = True
            temp_player, temp_other = [], []
            for y in range(self._boardsize):
                square_value = self._board[x][y]
                if square_value == player:
                    temp_player.append((x, y))
                elif square_value == other:
                    temp_other.append((x, y))
                else:
                    add = False
                    break
            if add:
                player_stables.extend(temp_player)
                other_stables.extend(temp_other)
        
        # then append the corners
        player_stables.extend(player_corners)
        other_stables.extend(other_corners)

        #looks for squares adjacent to these stable square
        player_stables_nb= len(self.add_adjacents_to_stable(player_stables, player))
        other_stables_nb = len(self.add_adjacents_to_stable(other_stables, other))

        player_semi_stables_nb = len(self.get_semi_stables(player))
        other_semi_stables_nb = len(self.get_semi_stables(other))
        player_unstable_nb = nb_coins_p - player_stables_nb - player_semi_stables_nb
        other_unstable_nb = nb_coins_o - other_semi_stables_nb - other_stables_nb

        player_stability = player_stables_nb - player_unstable_nb
        other_stability = other_stables_nb - other_unstable_nb


        return player_stability, other_stability



    def add_adjacents_to_stable(self, stable_squares, player):
        candidates_lists = []

        for x,y in stable_squares:
            candidates = [(x,y-1),(x-1,y),(x,y+1),(x+1,y),(x+1,y+1),(x-1,y-1),(x-1,y+1),(x+1,y-1)]
            candidates_lists.append(candidates)

        for candidates in candidates_lists:
            for candidate in candidates:
                #check square validity and player
                if not any([pos < 0 or pos >= self._boardsize for pos in candidate]) and self._board[x][y] == player:
                    stable_squares.append(candidate)
        return stable_squares

    def get_semi_stables(self,player):
        semi_stables = []
        for move in self.legal_moves(player):
            x,y = move[1], move[2]
            toflip_list = self.testAndBuild_ValidMove(player, x, y)
            if toflip_list != False:
                for toflip in toflip_list:
                    semi_stables.append(toflip)
        return semi_stables #list(set(semi_stables))

 



    # ---------------------------------------------

    # Renvoi la liste des coups possibles
    # Note: cette méthode pourrait être codée plus efficacement

    def legal_moves(self, player="default"):
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
