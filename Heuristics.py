from Reversi import Board


class Heuristics:

    def __init__(self, board, player, opponent):
        self._board = board
        self.player = player
        self.opponent = opponent
        self.corners_p = None
        self.corners_o = None
        self.nb_coins_p = None
        self.nb_coins_o = None

    def _get_nb_legal_moves(self):
        return len(self._board.legal_moves("default")), len(self._board.legal_moves("other"))

    def _set_nb_coins(self):
        self.nb_coins_p = self._board.get_nb_coins(self.player)
        self.nb_coins_o = self._board.get_nb_coins(self.opponent)

    def _set_corners(self):
        end = self._board._boardsize-1
        corners_list = [(0, 0), (0, end), (end, 0), (end, end)]
        self.corners_p, self.corners_o = [], []
        for (x, y) in corners_list:
            if self._board._board[x][y] == self.player:
                self.corners_p.append((x, y))
            elif self._board._board[x][y] == self.opponent:
                self.corners_o.append((x, y))

    def _get_stability(self):
        player_stables, other_stables = 0, 0
        for i in range(0, self._board._boardsize):
            for j in range(0, self._board._boardsize):
                if self._board._board[i][j] != self._board._EMPTY:
                    neighbors = [[i-1, j-1], [i-1, j], [i-1, j+1],
                                 [i, j-1], [i, j+1], [i+1, j-1], [i+1, j], [i+1, j+1]]
                    for x, y in neighbors:
                        if self._board._isOnBoard(x, y) and self._board._board[x][y] == self._board._EMPTY:
                            if self._board._board[i][j] == self.player:
                                player_stables += 1
                            else:
                                other_stables += 1

        return player_stables, other_stables

    def _get_heuristic_value(self, value_p, value_o):
        "Heuristic value calculation formula, based on value for player and opponent"
        if value_p + value_o == 0:
            return 0
        else:
            return 100 * (value_p - value_o) / (value_p + value_o)

    def coin_parity_heuristic(self):
        "Number of coins for each player"
        coins_h = self._get_heuristic_value(self.nb_coins_p, self.nb_coins_o)
        return coins_h

    def mobility_heuristic(self):
        "Possible moves for player"
        nb_moves_p, nb_moves_o = self._get_nb_legal_moves()
        mobility_h = self._get_heuristic_value(nb_moves_p, nb_moves_o)
        return mobility_h

    def corners_heuristic(self):
        "Corners captured"
        nb_corners_p = len(self.corners_p)
        nb_corners_o = len(self.corners_o)
        corners_h = self._get_heuristic_value(nb_corners_p, nb_corners_o)
        return corners_h

    def stability_heuristic(self):
        # Stability
        stability_p, stability_o = self._get_stability()
        stability_h = self._get_heuristic_value(stability_p, stability_o)
        return stability_h

    def disc_difference_heuristic(self):
        value = self._board._nbBLACK - self._board._nbWHITE
        return value if self.player == Board._BLACK else -value

    def total_heuristic(self):
        "Dynamic heuristic based on mobility, corners, coin parity and stability weighted according to the stage of the game"
        # inspired from https://github.com/Jules-Lion/kurwa/blob/master/Dokumentation/An Analysis of Heuristics in Othello.pdf
        # and https://github.com/arminkz/Reversi/blob/master/src/player/ai/DynamicEvaluator.java
        self._set_nb_coins()
        self._set_corners()

        # Dynamic heuristic based on the number of coins on the board
        stone_count = self._board.get_total_coins()

        # Early game
        if stone_count < 20:
            return 1000*self.corners_heuristic() + 50*self.mobility_heuristic()
        # Mid game
        elif stone_count <= 58:
            return 1000*self.corners_heuristic() + 20*self.mobility_heuristic() + 10*self.disc_difference_heuristic() + 100*self.coin_parity_heuristic() + 500*self.stability_heuristic()
        # End game
        else:
            return 1000*self.corners_heuristic() + 100*self.mobility_heuristic() + 500*self.disc_difference_heuristic() + 500*self.coin_parity_heuristic()
