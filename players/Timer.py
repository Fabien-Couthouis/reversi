import time
import math


class Timer():
    """
    Timer Class to help players managing their time.

    Arguments:
        max_time: Max time (in s) before getting out of time
        max_n_turns: Max number of turns for the game
    """

    def __init__(self, max_time, max_n_turns):
        self.total_time_left = max_time
        self.max_n_turns = int(max_n_turns)
        self.current_turn = 0

    def start_turn(self):
        "Launch this function while starting a new turn"
        self.start_time_turn = time.time()
        self.current_turn += 1

    def stop_turn(self):
        "Launch this function while ending turn"
        self.total_time_left -= time.time()-self.start_time_turn

    def get_time_left_for_turn(self):
        return self.start_time_turn + self.get_time_for_turn() - time.time()

    def out_of_time_for_turn(self):
        "True if time is out for current turn, False otherwise"
        if self.get_time_left_for_turn() < 0.01:  # little margin
            return True
        else:
            return False

    def get_time_for_turn(self):
        "Calculate time for turn, by giving more time to early turns"
        assert self.total_time_left > 0
        lamb = 0.1
        res = self.total_time_left*math.exp(lamb*(self.max_n_turns-self.current_turn+1))/sum([math.exp(lamb*i)
                                                                                              for i in range(1, self.max_n_turns-self.current_turn+2)])
        return round(res, 3)
