import random

# Implementation d'une table de transposition améliorée en utilisant le hashage de Zobrist


class ZobTransTable:
    def __init__(self, b):
        self.b = b
        (self._BLACK, self._WHITE, self._EMPTY, self._LIMIT) = (
            self.b._BLACK, self.b._WHITE, self.b._EMPTY, self.b._LIMIT)
        # self.zobTable = [[[random.randint(1, 2**10-1) for i in range(2)] for i in range(
        #     self.b.get_board_size())] for i in range(self.b.get_board_size())]
        self.zobTable = []
        for i in range(self.b.get_board_size()):
            self.zobTable.append([])
            for j in range(self.b.get_board_size()):
                self.zobTable[i].append((i, j))

        self.hash = self.compute_hash()
        self.data = {}

    # Retourne l'index dans la table de Zobrist correspondant à chaque type de pièce
    def indexing(self, piece):
        if piece == self._BLACK:
            return 0
        else:
            return 1

    # Calcul du hachage de l'état initial du plateau de jeu
    def compute_hash(self):
        h = 0
        board = self.b.get_board()
        for i in range(self.b.get_board_size()):
            for j in range(self.b.get_board_size()):
                if board[i][j] != self._EMPTY and board[i][j] != self._LIMIT:
                    piece = board[i][j]
                    h ^= self.zobTable[i-1][j-1][self.indexing(piece)]
        return h

    # Mise à jour du hachage suivant le dernier coup joué à l'aide d'une succession de XOR (plus rapide que de recalculer le hachage du plateau de jeu entier)
    def update_hash(self, move, toflip):
        [player, x, y] = move
        self.hash ^= self.zobTable[x][y][self.indexing(player)]
        for xf, yf in toflip:
            if player == self._BLACK:
                self.hash ^= self.zobTable[xf][yf][self.indexing(self._WHITE)]
            else:
                self.hash ^= self.zobTable[xf][yf][self.indexing(self._BLACK)]
            self.hash ^= self.zobTable[xf][yf][self.indexing(player)]

    # On regarde si l'état du plateau correspond à un état déjà enregistré dans la table (à l'aide de son hachage)
    # et on le renvoie le cas échéant
    def lookup(self):
        (move, toflip) = self.b.get_last_move()
        if move is not None:
            self.update_hash(move, toflip)
        return self.data.get(self.hash)

    # Stockage de l'état de jeu passé en paramètre dans la table de transposition via son hachage
    def store(self, entry):
        hash = self.compute_hash()
        self.data[hash] = entry
