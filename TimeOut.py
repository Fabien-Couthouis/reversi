import time
import math


class TimeOut():
    """
    Timeout Class

    Arguments:
        max_time: Max time (in seconds) before getting out of time 
    """

    def __init__(self, max_time, n_turns=None):
        self.start_time = time.time()
        self.max_time = max_time
        self.end_time = time.time() + max_time
        self.n_turns = n_turns
        self.turn = 1

    def get_time_left(self):
        return self.end_time - time.time()

    def out_of_time(self):
        return self.get_time_left() < 0.01  # little margin

    # def out_of_time_for_turn(self,turn):
    #     if

    def get_time_for_turn(self, turn):
        lamb = 0.05
        res = self.get_time_left()*math.exp(lamb*(self.n_turns-turn+1))/sum([math.exp(lamb*i)
                                                                             for i in range(1, self.n_turns-turn+2)])
        return round(res, 3)
