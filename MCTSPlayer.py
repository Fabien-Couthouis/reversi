from operator import itemgetter
import random
import copy
import numpy as np
import Reversi
import matplotlib.pyplot as plt
import math
import time
from playerInterface import PlayerInterface
from TimeOut import TimeOut


def rollout_policy(board):
    'Rollout randomly'
    legal_moves = board.legal_moves()
    action_probs = np.random.rand(len(legal_moves))
    return zip(legal_moves, action_probs)


def policy_value_fn(board):
    """a function that takes in a state and outputs a list of (action, probability)
    tuples and a score for the state"""
    legal_moves = board.legal_moves()

    # return uniform probabilities for pure MCTS
    action_probs = np.ones(len(legal_moves))/len(legal_moves)
    return zip(legal_moves, action_probs)


class Node:

    def __init__(self, parent, mcts):
        self.n_visits = 0
        self.value = 0
        self.children = {}
        self.parent = parent
        self.mcts = mcts

        if parent == None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1

    def add_child(self, action):
        self.children[str(action)] = Node(parent=self, mcts=self.mcts)

    def is_root(self):
        return True if self.parent is None else False

    def is_leaf(self):
        return self.children == {}

    def expand(self, actions):
        for action in actions:
            if str(action) not in self.children:
                self.add_child(action)
        # Return random child
        action, random_child = random.choice(list(self.children.items()))
        return eval(action), random_child

    def select(self):
        action, node = max(self.children.items(),
                           key=lambda node: node[1].ucb1())
        # action is stored as str in dict, we need to convert it in list before passing it to the game
        action = eval(action)
        return action, node

    def update(self, value):
        self.n_visits += 1
        self.value += value

    def back_propagate(self, value):
        self.update(value)
        if not self.is_root():
            # parent's node refers to opponent's action
            self.parent.back_propagate(1-value)

    def ucb1(self):
        return self.value / (self.n_visits+1) + math.sqrt(2 * math.log(self.mcts.get_n_simulations()) / (self.n_visits+1))

    def get_best_action(self):
        'Get next action based on children values. Return action,node'
        if self.is_leaf():
            raise Exception(f"Node {str(self)} do not have any child")
        # Best action is action with minimal opponnent node value
        action, node = min(self.children.items(),
                           key=lambda act_node: act_node[1].value)
        return eval(action), node

    def find_child_with_action(self, action):
        action = str(action)
        for child in self.children.items():
            child_action, child_node = child
            if child_action == action:
                return child_node
        return None

    def __str__(self):
        return f"Node n°{id(self)} with depth {self.depth} and value {self.value}/{self.n_visits}"


class MCTS:
    def __init__(self):
        self._root = Node(parent=None, mcts=self)
        self._n_simulations = 0

    def get_n_simulations(self):
        return self._n_simulations

    def train(self, starting_board, n_episodes=1000, starting_node=None, verbose=True):
        for episode in range(1, n_episodes+1):
            self.mcts_one_iteraction(starting_board, starting_node)
            if verbose and episode % (n_episodes * 0.05) == 0:
                print("Finished episode", episode, "/", n_episodes)

    def mcts_one_iteraction(self, board, starting_node=None):
        """
        Performs a round of Monte Carlo: https://en.wikipedia.org/wiki/Monte_Carlo_tree_search
        """
        board_copy = copy.deepcopy(board)
        # board_copy = board

        # Selection
        # Start from root R and select successive child nodes until a leaf node L is reached.
        node = self._root if starting_node is None else starting_node
        while not node.is_leaf():
            # Take ucb-directed action
            action, node = node.select()
            board_copy.push(action)

        # Expansion :
        # Unless L ends the game decisively (e.g. win/loss/draw) for either player
        # create one (or more) child nodes and choose node C from one of them.
        if not board_copy.is_game_over():
            action, node = node.expand(board_copy.legal_moves())
            board_copy.push(action)

        # Simulation
        # Complete one random rollout from node C
        value = self.simulate(board_copy)

        # Backpropagation
        # Use the result of the playout to update information in the nodes above
        node.back_propagate(value)

    def set_root(self, node):
        self._root = node

    def simulate(self, board, limit=1000):
        """
        Use the rollout policy to play until the end of the game,
        returning +1 if the current player wins, 0 if the opponent wins,
        and 0.5 if it is a tie.
        """
        current_player = board.get_next_player()
        while not board.is_game_over():
            action_probs = rollout_policy(board)
            next_action = max(action_probs, key=itemgetter(1))[0]
            board.push(next_action)

        winner = board.get_winner()
        self._n_simulations += 1
        # tie
        if winner == 0:
            return 0.5
        # current player wins
        elif winner == current_player:
            return 1
        # current player loses
        else:
            return 0

    def show(self, save_image=False):
        "Plot mcts using networkx and matplotlib"
        import networkx as nx
        from networkx.drawing.nx_agraph import write_dot, graphviz_layout

        def build_graph():
            def add_childs(graph, label_dict, node):
                if node.is_leaf():
                    return
                if node.is_root:
                    graph.add_node(id(node))
                    label_dict[id(node)] = f"{node.value}/{node.n_visits}"
                for child in node.children.items():
                    child_node = child[1]
                    graph.add_node(id(child_node))
                    graph.add_edge(id(node), id(child_node))
                    add_childs(graph, label_dict, child_node)
                    label_dict[id(child_node)
                               ] = f"{child_node.value}/{child_node.n_visits}"

            graph = nx.DiGraph()
            label_dict = {}
            add_childs(graph, label_dict, self._root)
            return graph, label_dict

        graph, label_dict = build_graph()
        write_dot(graph, 'mcts.dot')
        pos = graphviz_layout(graph, prog='dot')
        _fig, ax = plt.subplots()
        nx.draw(graph, pos, labels=label_dict,
                with_labels=True, arrows=False, node_size=1)
        if save_image:
            plt.savefig('mcts.png')
        plt.show()

    def save(self, path="mcts.pickle"):
        "Save mcts object using joblib"
        import joblib
        joblib.dump(self, path, compress=4)


class MCTSPlayer(PlayerInterface):
    """Reversi player based on MCTS"""

    def __init__(self, color, mcts, board_size=8):
        self._board = Reversi.Board(board_size)
        self.color = None
        self.newGame(color)
        self.mcts = mcts
        self.current_node = mcts._root

    def getPlayerName(self):
        return "Jean-Claude Van Dam"

    def update_current_node_with_action(self, action):
        new_current_node = self.current_node.find_child_with_action(action)
        self.update_current_node(new_current_node)

    def update_current_node(self, node):
        self.current_node = node

    def play_mcts(self, max_time=2):
        timeout = TimeOut(max_time)
        start = time.time()
        while not timeout.out_of_time():
            self.mcts.mcts_one_iteraction(
                self._board, starting_node=self.current_node)
        print("MCTS took", time.time()-start)

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return (-1, -1)

        self.play_mcts()
        action, node = self.current_node.get_best_action()
        self._board.push(action)
        self.update_current_node(node)
        print("I am playing ", action)
        (c, x, y) = action
        print("color:", self.color, " c:", c)

        assert(c == self.color)
        print("My current board :")
        print(self._board)
        return (x, y)

    def playOpponentMove(self, x, y):
        assert(self._board.is_valid_move(self._opponent, x, y))
        print("Opponent played ", (x, y))
        action = [self._opponent, x, y]
        self._board.push(action)
        self.update_current_node_with_action(action)

    def newGame(self, color):
        self.color = color
        self._opponent = 1 if color == 2 else 2

    def endGame(self, winner):
        if self.color == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")
