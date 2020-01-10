class PlayerInterface():
    def __str__(self):
        return f"Player: {self.getPlayerName()}"

    def getPlayerName(self):
        """
        Returns your player name, as to be displayed during the game.
        """
        return NotImplementedError

    def getPlayerMove(self):
        """
        Returns your move. The move must be a couple of two integers,
        which are the coordinates of where you want to put your piece on the board.
        Coordinates are the coordinates given by the Reversy.py methods (e.g. validMove(board, x, y)
        must be true of you play '(x,y)') You can also answer (-1,-1) as "pass".
        Note: the referee will nevercall your function if the game is over
        """
        return (-1, -1)

    def playOpponentMove(self, x, y):
        'Inform you that the oponent has played this move. You must play it with no search (just update your local variables to take it into account)'
        pass

    def newGame(self, color):
        'Starts a new game, and give you your color. As defined in Reversi.py : color=1 for BLACK, and color=2 for WHITE'
        pass

    #
    def endGame(self, color):
        'You can get a feedback on the winner This function gives you the color of the winner'
        pass
