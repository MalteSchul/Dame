import board as b
import monTree as mt
import os
import pygame
import time
from math import inf
from statistics import median
import random
import itertools
import matplotlib.pyplot as plt

display = True
width = 600
fieldSize = width / 8
test = False


if display:
    pygame.init()
    screen = pygame.display.set_mode((width, width))
    mb = b.Board(test=test)
else:
    mb = b.Board()
plt.ion()
plt.show()


def monTreSearch(board, master, limit, runs, displayHistoryBool=False):
    timeout = time.time() + limit[0]
    headNode = mt.Node(board, master)
    # Initialise history
    if displayHistoryBool:
        displayHistory = {}
        for move in headNode.availableMoves:
            displayHistory.update({move: []})
    # Only one possible move
    if len(headNode.availableMoves) == 1:
        return headNode.availableMoves[0][0], headNode.availableMoves[0][1]
    totalVisits = 0
    while time.time() < timeout and totalVisits < limit[1]:
        currNode = headNode
        if totalVisits % 100 == 0 and totalVisits > 0:
            sortedByVisits = sorted(headNode.subNodes, key=lambda a: a.visits, reverse=True)
            if sortedByVisits[0].visits * 0.5 > sortedByVisits[1].visits:
                print("Search canceled prematurely")
                break
        visitedNodes = [headNode]
        # Going down the tree
        while currNode.hasSubNodes():
            currNode = currNode.chooseMostInterestingSubNode(totalVisits)
            visitedNodes.append(currNode)
        score, gameLength = currNode.evaluateNode(runs)
        for visitedNode in visitedNodes:
            visitedNode.visits += 1
            visitedNode.gameLength += gameLength
            if visitedNode.playedBy == master:
                visitedNode.value += score
            else:
                visitedNode.value -= score
        totalVisits += 1
        if displayHistoryBool:
            for subNode in headNode.subNodes:
                displayHistory[subNode.board.playedMove].append(subNode.visits)

    for subNode in headNode.subNodes:
        print(subNode.visits, subNode.board.playedMove, subNode.avgScore(), subNode.avgGameLength())
    if displayHistoryBool:
        plt.clf()
        linestyle_tuple = [(0, (1, 1)), (0, (3, 3)), (0, (5, 5))]
        for posKey, key in enumerate(displayHistory):
            plt.plot(range(1, totalVisits + 1), displayHistory[key], label=str(key), linestyle=linestyle_tuple[posKey%len(linestyle_tuple)])
        plt.legend()
        plt.draw()
        plt.pause(0.1)
    winnerFromField, WinnerToField = mt.chooseBestSubNode(headNode).board.playedMove
    return winnerFromField, WinnerToField


def monTreSearchDepth(board, master, depth, runs):
    headNode = mt.Node(board, master)
    if len(headNode.availableMoves) == 1:
        return headNode.availableMoves[0][0], headNode.availableMoves[0][1]
    totalVisits = 0
    while totalVisits < depth:
        currNode = headNode
        visitedNodes = [headNode]
        # Going down the tree
        while currNode.hasSubNodes():
            currNode = currNode.chooseMostInterestingSubNode(totalVisits)
            visitedNodes.append(currNode)
        score = currNode.evaluateNode(runs)
        for visitedNode in visitedNodes:
            visitedNode.visits += 1
            if visitedNode.playedBy == master:
                visitedNode.value += score
            else:
                visitedNode.value -= score
        totalVisits += 1

    winnerFromField, WinnerToField = mt.chooseBestSubNode(headNode).playedMove
    return winnerFromField, WinnerToField


def getRandomMove(movableFields):
    keys = list(movableFields.keys())
    fromField = keys[random.randrange(len(keys))]
    toField = movableFields[fromField][random.randrange(len(movableFields[fromField]))]
    return fromField, toField


def mousePosToField(pos):
    return (int(pos[0] // (width / 8)), int(pos[1] // (width / 8)))


def getPlayerMove():
    moveDone = False
    while not moveDone:
        display()
        fromFieldSelected = mb.forcedToken
        while not fromFieldSelected:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    fromFieldSelected = mousePosToField(pygame.mouse.get_pos())
                    if fromFieldSelected not in mb.movableFields.keys():
                        fromFieldSelected = False
        display(fromFieldSelected=fromFieldSelected)
        # Select toField
        toFieldSelected = False
        while not toFieldSelected:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    toFieldSelected = mousePosToField(pygame.mouse.get_pos())
                    if toFieldSelected in mb.movableFields[fromFieldSelected]:
                        return mb.move(fromFieldSelected, toFieldSelected), fromFieldSelected, toFieldSelected
                    else:
                        fromFieldSelected = False


def display(fromFieldSelected=None):
    screen.fill((200, 200, 200))
    for row, column in itertools.product(range(8), range(8)):
        if row % 2 != column % 2:
            pygame.draw.rect(screen, (100, 42, 42), ((int(fieldSize) * column, int(fieldSize) * row), (fieldSize, fieldSize)))
    #draw played move
    if mb.playedMove:
        pygame.draw.rect(screen, (100, 80, 42), ((int(fieldSize) * mb.playedMove[0][0], int(fieldSize) * mb.playedMove[0][1]), (fieldSize, fieldSize)))
        pygame.draw.rect(screen, (100,100 , 42), ((int(fieldSize) * mb.playedMove[1][0], int(fieldSize) * mb.playedMove[1][1]), (fieldSize, fieldSize)))

    for column in range(1, 8):
        pygame.draw.line(screen, (0, 0, 0), (int(fieldSize) * column, 0),
                         (int(fieldSize) * column, width))
    for row in range(1, 8):
        pygame.draw.line(screen, (0, 0, 0), (0, int(fieldSize) * row),
                         (width, int(fieldSize) * row))

    pygame.event.get()
    for posRow, posColumn in itertools.product(range(8), range(8)):
        if mb.fields[posRow][posColumn] == 1:
            pygame.draw.circle(screen, (255, 255, 255),
                               (posColumn * fieldSize + fieldSize / 2, posRow * fieldSize + fieldSize / 2),
                               fieldSize / 3)
            if (posColumn, posRow) in mb.movableFields.keys():
                pygame.draw.circle(screen, (0, 0, 0),
                                   (posColumn * fieldSize + fieldSize / 2, posRow * fieldSize + fieldSize / 2),
                                   fieldSize / 6,
                                   width=2)
        elif mb.fields[posRow][posColumn] == 2:
            pygame.draw.circle(screen, (0, 0, 0),
                               (posColumn * fieldSize + fieldSize / 2, posRow * fieldSize + fieldSize / 2),
                               fieldSize / 3)
            if (posColumn, posRow) in mb.movableFields.keys():
                pygame.draw.circle(screen, (255, 255, 255),
                                   (posColumn * fieldSize + fieldSize / 2, posRow * fieldSize + fieldSize / 2),
                                   fieldSize / 6,
                                   width=2)
    for posColumn, posRow in mb.queenPoss:
        pygame.draw.circle(screen, (0, 200, 0),
                           (posColumn * fieldSize + fieldSize / 2, posRow * fieldSize + fieldSize / 2),
                           fieldSize / 3, width=4)
    if fromFieldSelected:
        if mb.currPlayer == 1:
            pygame.draw.circle(screen, (0, 0, 0), (
                fromFieldSelected[0] * fieldSize + fieldSize / 2, fromFieldSelected[1] * fieldSize + fieldSize / 2),
                               fieldSize / 6)
        else:
            pygame.draw.circle(screen, (255, 255, 255), (
                fromFieldSelected[0] * fieldSize + fieldSize / 2, fromFieldSelected[1] * fieldSize + fieldSize / 2),
                               fieldSize / 6)
        for field in mb.movableFields[fromFieldSelected]:
            pygame.draw.circle(screen, (200, 0, 0),
                               (field[0] * fieldSize + fieldSize / 2, field[1] * fieldSize + fieldSize / 2),
                               fieldSize / 6)
    pygame.display.update()

def fight(type, level=0.1, displayGraph=False):
    display()
    while True:
        print("\n", mb.currPlayer)
        if type == "mvm":
            if mb.currPlayer == 1:
                fromField, toField = monTreSearch(mb, mb.currPlayer, (level, inf), 5, displayHistoryBool=displayGraph)
                winner = mb.move(fromField, toField)
            else:
                fromField, toField = monTreSearch(mb, mb.currPlayer, (level, inf), 5, displayHistoryBool=displayGraph)
                winner = mb.move(fromField, toField)
        elif type == "mvp":
            if mb.currPlayer == 1:
                fromField, toField = monTreSearch(mb, mb.currPlayer, (level, inf), 5, displayHistoryBool=displayGraph)
                winner = mb.move(fromField, toField)
            else:
                winner, fromField, toField = getPlayerMove()
        elif type == "pvp":
            if mb.currPlayer == 1:
                winner, fromField, toField = getPlayerMove()
            else:
                winner, fromField, toField = getPlayerMove()
        else:
            raise Exception(type + " not available")
        print(fromField, toField, mb.turns, mb.turnsWithoutIncident)
        display()
        if winner >= 0:
            if winner == 0:
                pygame.draw.circle(screen, (120, 120, 120), (width / 2, width / 2), width / 3, width=10)
            elif winner == 1:
                pygame.draw.circle(screen, (255, 255, 255), (width / 2, width / 2), width / 3, width=10)
            elif winner == 2:
                pygame.draw.circle(screen, (0, 0, 0), (width / 2, width / 2), width / 3, width=10)
            pygame.display.update()
            winnerScreenSeen = False
            while not winnerScreenSeen:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        winnerScreenSeen = True
            mb.reset()
        # mb.getPlayerMove()
        display()
        time.sleep(0.5)

fight("mvm", level=6, displayGraph=True)
