from operator import itemgetter
import random
import copy
import numpy as np
import Reversi
import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt
import math


def rollout_policy(board):
    'Rollout randomly'
    legal_moves = board.legal_moves()
    action_probs = np.random.rand(len(legal_moves))
    return zip(legal_moves, action_probs)
    # action = random.choice(legal_moves)

    # return action


def policy_value_fn(board):
    """a function that takes in a state and outputs a list of (action, probability)
    tuples and a score for the state"""
    legal_moves = board.legal_moves()

    # return uniform probabilities and 0 score for pure MCTS
    action_probs = np.ones(len(legal_moves))/len(legal_moves)
    return zip(legal_moves, action_probs)


class Node:
    _ID = 0
    _TOTAL_VISITS = 0

    def __init__(self, parent):
        self.n_visits = 0
        self.n_wins = 0
        self.children = {}
        self.parent = parent

        if parent == None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1
        self.id = Node._ID
        Node._ID += 1

    def add_child(self, action):
        self.children[str(action)] = Node(parent=self)

    def is_root(self):
        return True if self.parent is None else False

    def is_leaf(self):
        return self.children == {}

    def expand(self, actions):
        for action, _ in actions:
            if str(action) not in self.children:
                self.add_child(action)

    def get_value(self):
        return self.n_wins/self.n_visits if self.n_visits != 0 else 0

    def select(self):
        action, node = max(self.children.items(),
                           key=lambda node: node[1].ucb1())
        # action is stored as str in dict, need to convert it in list before passing it in the game
        action = eval(action)
        return action, node

    def update(self, win):
        self.n_visits += 1
        Node._TOTAL_VISITS += 1
        if win:
            self.n_wins += 1

    def back_propagate(self, win):
        if self.parent is not None:
            self.parent.back_propagate(not win)
        self.update(win)

    def ucb1(self):
        return self.get_value() + math.sqrt(2 * math.log(Node._TOTAL_VISITS) / (self.n_visits+1))

    def __str__(self):
        return f"Node n°{self.id} with depth {self.depth} and value {self.n_wins}/{self.n_visits}"


class MCTS:
    def __init__(self, n_games, policy=policy_value_fn):
        self._policy = policy
        self._n_games = n_games
        self._root = Node(parent=None)

    def start_self_play(self, starting_board):
        for _game in range(self._n_games):
            print("game", _game)
            board = copy.deepcopy(starting_board)

            # Selection
            node = self._root
            while not node.is_leaf():
                # Take greedy action
                action, node = node.select()
                # self.show()
                board.push(action)

            # Expansion
            if not board.is_game_over():
                action_probs = self._policy(board)
                node.expand(action_probs)

            # Simulation
            win = self.simulate(board)

            # Backpropagation
            node.back_propagate(not win)

    def simulate(self, board, limit=1000):
        """
        Use the rollout policy to play until the end of the game,
        returning +1 if the current player wins, -1 if the opponent wins,
        and 0 if it is a tie.
        """
        for _ in range(limit):
            end, winner = board.end_game()
            if end:
                break
            action_probs = rollout_policy(board)
            next_action = max(action_probs, key=itemgetter(1))[0]
            # next_action2 = rollout_policy(board)
            # print(board)
            # next_action = rollout_policy(board)
            board.push(next_action)

        if winner == 0:  # tie
            return 0
        elif winner == board.get_player():
            return 1
        else:
            return -1

    def add_childs(self, graph, label_dict, node):
        if node.is_leaf():
            return
        if node.is_root:
            graph.add_node(node.id)
            label_dict[node.id] = f"{node.n_wins}/{node.n_visits}"
        for child in node.children.items():
            child_node = child[1]
            graph.add_node(child_node.id)
            graph.add_edge(node.id, child_node.id)
            self.add_childs(graph, label_dict, child_node)
            label_dict[child_node.id] = f"{child_node.n_wins}/{child_node.n_visits}"

    def build_graph(self):
        graph = nx.DiGraph()
        label_dict = {}
        self.add_childs(graph, label_dict, self._root)
        return graph, label_dict

    def show(self):
        graph, label_dict = self.build_graph()
        write_dot(graph, 'test.dot')
        pos = graphviz_layout(graph, prog='dot')
        nx.draw(graph, pos, labels=label_dict, with_labels=True, arrows=False)
        # nx.draw(graph, labels=label_dict, with_labels=True)
        plt.show()


class MCTS2:
    def __init__(self, n_games, policy, epsilon=0.95):
        self.epsilon = epsilon
        self._policy = policy
        self._n_games = n_games
        self._root = Node(parent=None)

    def walk(self, board):
        board_copy = copy.deepcopy(board)
        node = self._root

        while True:
            if node.is_leaf():
                break
            # Greedily select next move
            action, node = node.select(random=False)
            board_copy.push(action)

        action_probs, _ = self._policy(board)

        # Check for end of game
        if not board.is_game_over():
            node.expand(action_probs)
        # Evaluate the leaf node by random rollout
        win = self.eval_rollout(board_copy)

        # Update value and visit count of nodes in this traversal.
        node.back_propagate(not win)

    def update(self, move):
        if move in self._root._children:
            self._root = self._root.children[move]
            self._root.parent = None
        else:
            self._root = Node(parent=None)

    def get_move(self, board):
        """Runs all playouts sequentially and returns the most visited action.
        state: the current game state
        Return: the selected action
        """
        for _ in range(self._n_games):
            self.walk(board)
        return max(self._root.children.items(),
                   key=lambda act_node: act_node[1].n_visits)[0]

    def eval_rollout(self, board, limit=1000):
        """Use the rollout policy to play until the end of the game,
        returning +1 if the current player wins, -1 if the opponent wins,
        and 0 if it is a tie.
        """

        for _ in range(limit):
            end, winner = board.end_game()
            if end:
                break
            action_probs = rollout_policy(board)
            next_action = max(action_probs, key=itemgetter(1))[0]
            board.push(next_action)

        if winner == 0:  # tie
            return 0
        else:
            return 1 if winner == board.get_player() else -1


class MCTSPlayer(object):
    """Reversi player based on MCTS"""

    def __init__(self, color, n_games=2000):
        self._board = Reversi.Board(10)
        self.color = None
        self.newGame(color)
        self.mcts = MCTS(n_games, policy_value_fn)

    def getPlayerName(self):
        return "MCTS player"

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

    def reset_player(self):
        self.mcts.update(-1)

    def getPlayerMove(self):
        legal_moves = self._board.legal_moves()
        if len(legal_moves) > 0:
            move = self.mcts.get_move(self._board)
            self.mcts.update(-1)
            return move
        else:
            raise EnvironmentError("The board is full!")

    def start_self_play(self):
        """ Start a self-play game using a MCTS player, reuse the search tree,
        and store the self-play data: (state, mcts_probs, z) for training
        """
        states, mcts_probs, current_players = [], [], []
        while True:
            move, move_probs = self.getPlayerMove()
            # store the data
            states.append(self._board.get_state())
            mcts_probs.append(move_probs)
            current_players.append(self._board.get_player())
            # perform a move
            self._board.push(move)
            end, winner = self._board.end_game()
            if end:
                # winner from the perspective of the current player of each state
                winners_z = np.zeros(len(current_players))
                if winner != -1:
                    winners_z[np.array(current_players) == winner] = 1.0
                    winners_z[np.array(current_players) != winner] = -1.0
                # reset MCTS root node
                self.reset_player()
                return winner, zip(states, mcts_probs, winners_z)
