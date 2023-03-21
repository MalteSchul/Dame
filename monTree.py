import math
import copy
import random
import numpy as np

def getRandomMove(movableFields):
    keys = list(movableFields.keys())
    fromField = keys[random.randrange(len(keys))]
    toField = movableFields[fromField][random.randrange(len(movableFields[fromField]))]
    return fromField, toField

def ucb(v, N, n):
    try:
        return v/n + 2 * math.sqrt(math.log(N) / n)
    except ZeroDivisionError:
        pass


def chooseBestSubNode(node):
    if not node.subNodes or node.subNodes[0].visits == 0:
        return False
    bestSubNode = node.subNodes[0]
    for subNode in node.subNodes:
        if subNode.visits >= bestSubNode.visits:
            if subNode.avgScore() >= bestSubNode.avgScore():
                bestSubNode = subNode
    return bestSubNode


class Node:
    def __init__(self, board, master, playedBy=None):
        self.board = board
        self.playedBy = playedBy
        self.master = master
        self.availableMoves = self.searchAvailableMoves()
        # Key values
        self.subNodes = []
        self.visits = 0
        self.value = 0
        self.gameLength = 0

    def avgGameLength(self):
        if self.visits == 0:
            return "-"
        return self.gameLength/self.visits

    def avgScore(self):
        if self.visits == 0:
            return "-"
        return self.value/self.visits

    def hasSubNodes(self):
        return self.subNodes != []

    def searchAvailableMoves(self):
        result = []
        for fromField in self.board.movableFields:
            for toField in self.board.movableFields[fromField]:
                result.append((fromField, toField))
        return result

    def createSubNodes(self):
        for move in self.availableMoves:
            nextBoard = copy.deepcopy(self.board)
            nextBoard.move(move[0], move[1])
            self.subNodes.append(Node(nextBoard, self.master, playedBy=self.board.currPlayer))

    def evaluateNode(self, runs):
        self.createSubNodes()
        score = 0
        gameLength = 0
        for _ in range(runs):
            currBoard = copy.deepcopy(self.board)
            winner = currBoard.checkWinner()
            while True:
                if winner != -1:
                    if winner == self.master:
                        score += 1
                    elif winner > 0:
                        score -= 1
                    gameLength += currBoard.turns
                    break
                move = getRandomMove(currBoard.movableFields)
                winner = currBoard.move(move[0], move[1])
        score /= runs
        return score, gameLength / runs

    # Currents player perspective!
    def chooseMostInterestingSubNode(self, totalVisits):
        currFavoriteSubNode = self.subNodes[0]
        currFavoriteSubNode_UCBScore = ucb(self.subNodes[0].value, totalVisits, self.subNodes[0].visits)
        for subNode in self.subNodes:
            if subNode.visits == 0:
                return subNode
            if ucb(subNode.value, totalVisits, subNode.visits) > currFavoriteSubNode_UCBScore:
                currFavoriteSubNode = subNode
        return currFavoriteSubNode


