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

    def get_nb_legal_moves(self):
        return len(self._board.legal_moves("default")), len(self._board.legal_moves("other"))

    def set_nb_coins(self):
        self.nb_coins_p = self._board.get_nb_coins(self.player)
        self.nb_coins_o = self._board.get_nb_coins(self.opponent)

    def set_corners(self):
        end = self._board._boardsize-1
        corners_list = [(0, 0), (0, end), (end, 0), (end, end)]
        self.corners_p, self.corners_o = [], []
        for (x, y) in corners_list:
            if self._board._board[x][y] == self.player:
                self.corners_p.append((x, y))
            elif self._board._board[x][y] == self.opponent:
                self.corners_o.append((x, y))

    def get_stability(self):
        # inspired from http://pressibus.org/ataxx/autre/minimax/node3.html
        player_stables, other_stables = set(), set()
        b_size = self._board._boardsize

        # append filled rows
        for x in range(b_size):
            temp_p, temp_o = set(), set()
            for y in range(b_size):
                square_value = self._board._board[x][y]
                if square_value == self.player:
                    temp_p.add((x, y))
                elif square_value == self.opponent:
                    temp_o.add((x, y))
                else:
                    # Row is not filled
                    break
            player_stables.update(temp_p)
            other_stables.update(temp_o)

        # then append the corners
        player_stables.update(set(self.corners_p))
        other_stables.update(set(self.corners_o))

        # looks for squares adjacent to these stable square
        player_stables_nb = len(
            self.add_adjacents_to_stable(list(player_stables), self.player))
        other_stables_nb = len(
            self.add_adjacents_to_stable(list(other_stables), self.opponent))

        player_semi_stables_nb = len(self.get_semi_stables(self.player))
        other_semi_stables_nb = len(
            self.get_semi_stables(self.opponent))
        player_unstable_nb = self.nb_coins_p - \
            player_stables_nb - player_semi_stables_nb
        other_unstable_nb = self.nb_coins_o - other_semi_stables_nb - other_stables_nb

        player_stability = player_stables_nb - player_unstable_nb
        other_stability = other_stables_nb - other_unstable_nb

        return player_stability, other_stability

    def add_adjacents_to_stable(self, stable_squares, player):
        candidates_list = []
        # print("oui")

        for x, y in stable_squares:
            candidates = [(x, y-1), (x-1, y), (x, y+1), (x+1, y),
                          (x+1, y+1), (x-1, y-1), (x-1, y+1), (x+1, y-1)]
            # Check if position is legal
            if not any([[pos < 0 or pos >= self._board._boardsize for pos in candidate] for candidate in candidates]):
                candidates_list.append(candidates)

        for candidates in candidates_list:
            for x, y in candidates:
                # check square validity and player
                if self._board._board[x][y] == player:
                    stable_squares.append((x, y))
        return stable_squares

    def get_semi_stables(self, player):
        semi_stables = []
        for move in self._board.legal_moves(player):
            x, y = move[1], move[2]
            toflip_list = self._board.testAndBuild_ValidMove(player, x, y)
            if toflip_list != False:
                for toflip in toflip_list:
                    if toflip not in semi_stables:
                        semi_stables.append(toflip)
        return semi_stables

    def coin_parity(self):
        "Number of coins for each player"
        coins_h = self.get_heuristic_value(self.nb_coins_p, self.nb_coins_o)
        return coins_h

    def mobility(self):
        "Possible moves for player"
        nb_moves_p, nb_moves_o = self.get_nb_legal_moves()
        mobility_h = self.get_heuristic_value(nb_moves_p, nb_moves_o)
        return mobility_h

    def corners(self):
        "Corners captured"
        nb_corners_p = len(self.corners_p)
        nb_corners_o = len(self.corners_o)
        corners_h = self.get_heuristic_value(nb_corners_p, nb_corners_o)
        return corners_h

    def stability(self):
        # Stability
        stability_p, stability_o = self.get_stability()
        stability_h = self.get_heuristic_value(stability_p, stability_o)
        return stability_h

    def disc_difference(self):
        value = self._board._nbBLACK - self._board._nbWHITE
        return value if self.player == Board._BLACK else -value

    def total_heuristic(self):
        # inspired from https://github.com/Jules-Lion/kurwa/blob/master/Dokumentation/An Analysis of Heuristics in Othello.pdf
        # and https://github.com/arminkz/Reversi/blob/master/src/player/ai/DynamicEvaluator.java

        self.set_nb_coins()
        self.set_corners()

        # Dynamic heuristic based on the number of coins on the board
        gamephase = self.get_gamephase()
        if gamephase == "early":
            return 1000*self.corners() + 50*self.mobility()

        elif gamephase == "mid":
            return 1000*self.corners() + 20*self.mobility() + 10*self.disc_difference() + 100*self.coin_parity() + 500*self.stability()

        else:
            return 1000*self.corners() + 100*self.mobility() + 500*self.disc_difference() + 500*self.coin_parity()

    def get_gamephase(self):
        stone_count = self._board.get_total_coins()
        if stone_count < 20:
            return "early"
        elif stone_count <= 58:
            return "end"
        else:
            return "end"

    def get_heuristic_value(self, value_p, value_o):
        "Heuristic value calculation formula, based on value for player and opponent"
        if value_p + value_o == 0:
            return 0
        else:
            return 100 * (value_p - value_o) / (value_p + value_o)
