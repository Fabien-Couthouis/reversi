# Computer othello / reversi
Computer reversi program developped for AI [ENSEIRB-MATMECA](https://enseirb-matmeca.bordeaux-inp.fr/fr) course. It implements: a Random player, an AlphaBeta player with heuristics and a Monte Carlo Tree Search player.

## Implementation details
### AlphaBeta player
[AlphaBeta Player](./players/AlphaBetaPlayer.py) is based on negAlphaBeta algorithm with iterative deepening and dynamic heuristic. This [dynamic heuristic](./players/Heuristics.py) is inspired by [SannidHanam et al.](https://courses.cs.washington.edu/courses/cse573/04au/Project/mini1/RUSSIA/Final_Paper.pdf) and [this dynamic evaluator](https://github.com/arminkz/Reversi/blob/master/src/player/ai/DynamicEvaluator.java), and evolves during stages of the game (early game, mid game, end game).
1. Early game heuristic (less than 20 stones placed on the board): 
    ```python
    H_early =   1000*corners_heuristic + 50*mobility_heuristic
    ```
   
2. Mid game heuristic (between 20 and 58 stones placed on the board): 



    ```python
    H_mid = 1000*corners_heuristic + 20*mobility_heuristic + 10*disc_difference_heuristic + 100*coin_parity_heuristic + 500*stability_heuristic
    ```

3. End game heuristic (more than 58 stones placed on the board): 

    ```python
    H_end = 1000*corners_heuristic+ mobility_heuristic + 500*disc_difference_heuristic + 500*coin_parity_heuristic
    ```
All sub-heuristics are described in the table below:

| Sub-heuristic             |                                                                                                                              Value for each player                                                                                                                               | Coefficients (early/mid/end) |
| ------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :--------------------------: |
| disc difference heuristic |                                                                                                             Number of coins of player - number of coins of opponent                                                                                                              |           0/10/500           |
| corners heuristic         |                                                                                                                            Number of captured corners                                                                                                                            |        1000/1000/1000        |
| mobility heuristic        |                                                                                                                             Number of legal actions                                                                                                                              |           50/20/1            |
| coin parity heuristic     |                                                                                                                          Number of coins on the board.                                                                                                                           |          0/100/500           |
| stability heuristic       | Each coin of the player can be either stable (cannot be flipped, value=1), semi-stable (can be flipped but not in the next move, value=0) or unstable (can by flipped by the opponent next move, value=-1). The value for each player is the sum of the values of all its coins. |           0/500/0            |

All sub-heuristics (except disc difference) are computed thanks to this formula:
```python
100 * (value_for_player - value_for_opponent) / (value_for_player + value_for_opponent)
```

### MCTS player
[Vanilla Monte Carlo Tree Search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search) with ucb node selection in simulations, to balance between exploitation and exploration.
It is possible to train the mcts by making games simulations between itself, in order to estimate node values. THere is also a function to show the mcts graph built. 

### Time limitation
Each game has a time limit.
For both of MCTS and AlphaBeta players, time limit for each turn is computed thanks to the formula below, in order to give more time to the player for early turns:

```python
    time_for_turn = total_time_left*math.exp(0.1(max_n_turns-current_turn+1))/sum([math.exp(lamb*i)
```

Where the maximum number of turns is given by 4+(board_size**2)/2).


## Usage
[Main.py file](./main.py) contains all functions to test the players. You just need to modify the __main__ function:

```python
    #Train mcts for 10 iterations on a 8x8 board
    n = 10
    train(10, b_size=8) 
```

```python
    # Test mcts vs alphabeta for 60 games with a time limit of 120s maximum for each game
    board = Reversi.Board(8)
    mcts = load_mcts("mcts_save/mcts_10000_iter_size_8.pickle")
    p1, p2 = MCTSPlayer(
        0, mcts, board._boardsize, max_time=120), AlphaBetaPlayer(1, board._boardsize, max_time=120)
    simulate_multiple_games(p1, p2, board, n_games=30)
```

```python
    #Show mcts graph for 5 iterations
    mcts = load_mcts("mcts_save/mcts_5_iter_size_8.pickle")
    mcts.show()
```

![Image](/images/mcts_5_iter.png "MCTS generated on 5 iterations")



## Results


Comparison: MCTS vs AlphaBeta vs Random player (random color assignation at each game). MCTS vs AlphaBeta was tested with 120s maximum per game. AlphaBeta vs Random and MCTS vs Random was tested with only 30s maximum per game. I played 60 games for each experiment. The results are presented in the table below.


Reading direction: left player wins - top player wins - ties



|           | AlphaBeta |   MCTS | Random |
| --------- | :-------: | -----: | -----: |
| AlphaBeta |     -     | 3-57-0 | 52-6-2 |
| MCTS      |  57-3-0  |      - | 58-1-1 |
| Random    |  6-52-2   | 1-58-1 |      - |


## Credits
Based on [Laurent Simon](https://www.labri.fr/perso/lsimon/) courses at [ENSEIRB-MATMECA](https://enseirb-matmeca.bordeaux-inp.fr/fr).
