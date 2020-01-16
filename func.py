import math


def func(total_time, n_turns):
    left_time = total_time
    results = []
    for turn in range(1, 1+n_turns):
        # res = left_time*math.exp(lamb*(n_turns-turn+1))/sum([math.exp(lamb*i)
        #                                                    for i in range(1, n_turns-turn+2)])
        # res = round(res, 4)
        res = get_time_for_turn(left_time, n_turns, turn)
        left_time -= res
        results.append(res)

        print(res)

    print(sum(results))


def get_time_for_turn(left_time, n_turns, turn):
    lamb = 0.05
    res = left_time*math.exp(lamb*(n_turns-turn+1))/sum([math.exp(lamb*i)
                                                         for i in range(1, n_turns-turn+2)])
    return round(res, 3)


func(150, 40)
