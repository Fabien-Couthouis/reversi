# -*- coding: utf-8 -*-

import time
import Reversi
from random import randint, choice

def RandomMove(b):
    return choice(list(b.legal_moves()))

def deroulementRandom(b):
    print("----------")
    print(b)
    if b.is_game_over():
        return
    move = RandomMove(b) 
    b.push(move)
    deroulementRandom(b)
    b.pop()


def heuristique(b, blanc):
    return b.heuristique()

def estimeFin(b, blanc):
    val = None
    if b.is_game_over():
        (nbwhite, nbblack) = b.get_nb_pieces()
        if nbwhite == nbblack:
            val = 0
        elif nbwhite > nbblack:
            val = 1000 if blanc else -1000
        else:
            val = -1000 if blanc else 1000
    else:
         val = heuristique(b, blanc)
    return (val, None)

def negaMax(b, blanc=True, horizon=10):

    if horizon == 0 or b.is_game_over():
        return estimeFin(b, blanc)

    meilleur = None
    meilleurCoup = None
    for m in b.legal_moves():
        b.push(m)
        (nm, _) = negaMax(b, not blanc, horizon - 1)
        nm = -nm
        if meilleur is None or nm > meilleur:
            meilleur = nm
            meilleurCoup = m
        b.pop()

    return (meilleur, meilleurCoup)

# Neg Alpha Beta avec version d'echec
def negAlphaBeta(b, alpha, beta, blanc=True, horizon=10):

    if horizon == 0 or b.is_game_over():
        return estimeFin(b, blanc)

    meilleur = None
    meilleurCoup = None
    for m in b.legal_moves():
        b.push(m)
        (nm, _) = negAlphaBeta(b, -beta, -alpha,
                            not blanc, horizon - 1)
        nm = -nm
        if meilleur is None or nm > meilleur:
            meilleur = nm
            meilleurCoup = m
            if meilleur > alpha:
                alpha = meilleur
                if alpha > beta: # Coupure
                    b.pop()
                    return (meilleur, meilleurCoup)
        b.pop()

    return (meilleur, meilleurCoup)

board = Reversi.Board(10)

# Problème : quand on est en fin de partie, le ID est relancé des millieurs de fois avec une profondeur max très grande
while not board.is_game_over():
    tt = time.perf_counter()
    #coup = IAMinimax(board, 1)  # Profondeur donnée en nombre de coups
    (_,coup) = negaMax(board, True, 5) # Profondeur donnée en "secondes" pour ID
    print("negaMax joue " + str(coup) + " en " + str(time.perf_counter()-tt))
    #assert(board.is_valid_move(coup))
    board.push(coup)

    tt = time.perf_counter()
    (_, coup) = negAlphaBeta(board, -1000, 1000, False, 5)  # Profondeur donnée en nombre de coups
    print("negAlphaBeta joue " + str(coup) + " en " + str(time.perf_counter()-tt))
    board.push(coup)

    print(board)

