import random
import copy


class Node:
    def __init__(self, parent):
        self.n_visits = 0
        self.n_wins = 0
        self.children = {}
        self.parent = parent

    def add_child(self, action):
        self.children[action] = Node(parent=self)

    def is_leaf(self):
        return self.children == {}

    def is_root(self):
        return self.parent is None

    def expand(self, actions):
        for action in actions:
            if action not in self.children:
                self.add_child(action)

    def get_value(self):
        return self.n_wins/self.n_visits

    def select(self, random=False):
        if random:
            return random.choice(list(self.children.items()))
        else:
            return max(self.children.items(), key=lambda node: node.get_value())

    def update(self, win):
        self.n_visits += 1
        if win:
            self.n_wins += 1

    def update_parents(self, win):
        if not self.is_root:
            self.update_parents(not win)
        self.update(win)


class MCTS:
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

            # epsilon-greedy strategy
            if random.random() < self.epsilon:
                # Greedily select next move.
                action, node = node.select(random=False)
            else:
                # Randomly select next move.
                action, node = node.select(random=True)

            board_copy.push(action)

        action_probs, win = self._policy(board_copy)
        # Check for end of game.
        end, winner = board_copy.end_game()
        if not end:
            node.expand(action_probs)
        else:
            if winner == board_copy.player:
                win = True
            else:
                win = False

        node.update_recursive(not win)

    def update(self, move):
        if move in self._root._children:
            self._root = self._root.children[move]
            self._root.parent = None
        else:
            self._root = Node(parent=None)

    def get_move_values(self, board):
        for n in range(self._n_games):
            self.walk(board)

        # calc the move probabilities based on visit counts at the root node
        act_visits = [(act, node.n_visits)
                      for act, node in self._root.children.items()]
        acts, visits = zip(*act_visits)

        return acts, act_visits
