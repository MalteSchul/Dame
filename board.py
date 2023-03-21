import random
import numpy as np
import itertools


def theOtherPlayer(player):
    return player % 2 + 1


def resultHeight(currentHeight, movingDirection, stepSize):
    if movingDirection == "plus":
        return currentHeight + stepSize
    else:
        return currentHeight - stepSize


class Board:
    def __init__(self, test=False):
        self.playedMove = False
        if test:
            self.turns = 0
            self.turnsWithoutIncident = 10
            self.fields = np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                                    [1, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 1, 0, 1, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 2, 0]], dtype=int)
            self.currPlayer = 1
            self.jump = False
            self.forcedToken = False
            self.queenPoss = [(3,2), (5,6), (1,2), (5,2)]
            self.updateMovableFields()
        else:
            self.reset()

    def reset(self):
        self.turns = 0
        self.turnsWithoutIncident = 0
        self.fields = np.array([[0, 1, 0, 1, 0, 1, 0, 1],
                                [1, 0, 1, 0, 1, 0, 1, 0],
                                [0, 1, 0, 1, 0, 1, 0, 1],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [2, 0, 2, 0, 2, 0, 2, 0],
                                [0, 2, 0, 2, 0, 2, 0, 2],
                                [2, 0, 2, 0, 2, 0, 2, 0]], dtype=int)
        self.currPlayer = random.randrange(2) + 1
        self.jump = False
        self.forcedToken = False
        self.queenPoss = []
        self.updateMovableFields()

    def updateMovableFields(self):
        self.movableFields = {}
        self.jump = False
        if self.forcedToken:
            self.checkDelta2(self.forcedToken[0], self.forcedToken[1])
            return
        for Row, Column in itertools.product(range(8), range(8)):
            if self.fields[Row][Column] == self.currPlayer:
                self.checkDelta1(Column, Row)
        for Row, Column in itertools.product(range(8), range(8)):
            if self.fields[Row][Column] == self.currPlayer:
                self.checkDelta2(Column, Row)

    def checkDelta1(self, Column, Row):
        added = False
        deltaXs = [-1, 1]
        if (Column, Row) in self.queenPoss:
            deltaYs = [-1, 1]
        elif self.currPlayer == 1:
            deltaYs = [1]
        else:
            deltaYs = [-1]
        for deltaY in deltaYs:
            if 0 <= Row + deltaY <= 7:
                for deltaX in deltaXs:
                    if 0 <= Column + deltaX <= 7:
                        if self.fields[Row + deltaY][Column + deltaX] == 0:
                            if not added:
                                self.movableFields.update({(Column, Row): []})
                                added = True
                            self.movableFields[(Column, Row)].append((Column + deltaX, Row + deltaY))

    def checkDelta2(self, Column, Row):
        added = False
        deltaXs = [-2, 2]
        if (Column, Row) in self.queenPoss:
            deltaYs = [-2, 2]
        elif self.currPlayer == 1:
            deltaYs = [2]
        else:
            deltaYs = [-2]
        for deltaY in deltaYs:
            if 0 <= Row + deltaY <= 7:
                for deltaX in deltaXs:
                    if 0 <= Column + deltaX <= 7:
                        if self.fields[Row + deltaY][Column + deltaX] == 0 and self.fields[Row + int(deltaY/2)][Column + int(deltaX/2)] == theOtherPlayer(self.currPlayer):
                            if not self.jump:
                                self.jump = True
                                self.movableFields.clear()
                            if not added:
                                self.movableFields.update({(Column, Row): []})
                                added = True
                            self.movableFields[(Column, Row)].append((Column + deltaX, Row + deltaY))

    def move(self, fromField, toField):
        self.turns += 1
        self.playedMove = (fromField, toField)
        if fromField in self.queenPoss:
            self.queenPoss[self.queenPoss.index(fromField)] = toField
            self.turnsWithoutIncident += 1
        else:
            self.turnsWithoutIncident = 0
        self.fields[fromField[1]][fromField[0]] = 0
        self.fields[toField[1]][toField[0]] = self.currPlayer
        if (toField[1] == 0 or toField[1] == 7) and (toField[0], toField[1]) not in self.queenPoss:
            self.queenPoss.append((toField[0], toField[1]))

        if self.jump:
            self.turnsWithoutIncident = 0
            jumpedField = (int(fromField[0] + (toField[0] - fromField[0]) / 2),int(fromField[1] + (toField[1] - fromField[1]) / 2))
            if jumpedField in self.queenPoss:
                self.queenPoss.pop(self.queenPoss.index(jumpedField))
            self.fields[jumpedField[1]][jumpedField[0]] = 0
            self.forcedToken = toField
            self.updateMovableFields()
            if not self.movableFields.keys():
                self.currPlayer = theOtherPlayer(self.currPlayer)
                self.forcedToken = False
                self.updateMovableFields()
        else:
            self.currPlayer = theOtherPlayer(self.currPlayer)
            self.updateMovableFields()
        return self.checkWinner()

    def checkWinner(self):
        if self.movableFields.keys():
            if self.turnsWithoutIncident > 20:
                return 0
            return -1
        else:
            return theOtherPlayer(self.currPlayer)

    def __str__(self):
        return str(self.fields)
        # return reduce(lambda strA, strB: strA + "\n" + strB, map(lambda row: " ".join(map(lambda field: str(field), row)), self.fields))
