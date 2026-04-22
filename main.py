from cmu_graphics import *
import random
import math
import json

#create Piece class
class Piece:
    def __init__(self, x, y, width, height, correctX, correctY, row, col, angle):
        self.x = x
        self.y = y
        self.startX = x
        self.startY = y
        self.width = width
        self.height = height
        self.correctX = correctX
        self.correctY = correctY
        self.row = row
        self.col = col
        self.locked = False
        self.angle = angle
        # self.dragging = False
        self.edges = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}

def onAppStart(app):
    app.stepsPerSecond = 10
    app.height = 900
    app.width = 600
    app.boardLeft = 25
    app.boardTop = 25
    app.boardWidth = min(app.width - (app.boardLeft * 2), app.height - (app.boardTop * 2))
    app.boardHeight = app.boardWidth
    app.draggingPiece = None
    app.bestScores = []
    start_onScreenStart(app)


def start_onScreenStart(app):
    app.timer = 0
    app.pieceList = []
    app.rows, app.cols = 1, 1
    app.offsetX, app.offsetY = 0, 0
    app.numberOfPieces = 1
    app.levelChosen = 'easy'
    app.hints = 0
    app.hintPiece = None
    app.gameWon = False
    app.winDelay = 0

def start_onMouseRelease(app, mouseX, mouseY):
    pass

def start_onMouseDrag(app, mouseX, mouseY):
    pass

#create start screen, easy, medium, hard screens
def start_redrawAll(app):
    # come up with a creative name
    drawRect(0,0,app.width, app.height, fill = 'pink', opacity = 80)
    drawLabel('Welcome to the Jigsaw Jungle', app.width//2, 50, size = app.width//14, font = 'cursive', bold = True)
    drawLabel('Select a Level', app.width // 2, 1.25*app.height/5, size = app.width//11, font = 'cursive')
    drawRect(app.width//2, 2*app.height/5, app.width//2.5, app.height//7, align = 'center', fill = 'forestGreen')
    drawRect(app.width//2, 3*app.height/5, app.width//2.5, app.height//7, align = 'center', fill = 'gold')
    drawRect(app.width//2, 4*app.height/5, app.width//2.5, app.height//7, align = 'center', fill = 'crimson')
    drawLabel('Easy', app.width//2, 2*app.height/5, size = app.width / 10, font = 'cursive')
    drawLabel('Medium', app.width//2, 3*app.height/5, size = app.width / 10, font = 'cursive')
    drawLabel('Hard', app.width//2, 4*app.height/5, size = app.width / 10, font = 'cursive')
    drawRect(app.width//2, app.height - 50, app.width//5, app.height//14, align = 'center', fill = 'cyan')
    drawLabel('Instructions', app.width//2, app.height - 50, size = 20, font = 'cursive')
    
def start_onMousePress(app, mouseX, mouseY):
    levelChosen = levelSelected(app, mouseX, mouseY)
    if (app.width//2 - app.width//10 <= mouseX <= app.width//2 + app.width//10) and (app.height - 50 - app.height//28 <= mouseY <= app.height - 50 + app.height//28): 
       setActiveScreen('instructions') 
    if levelChosen == None:
        return
    if levelChosen == 'Easy': 
        app.levelChosen = random.choice(['easy', 'easy2'])
        app.numberOfPieces = 25
    if levelChosen == 'Medium':
        app.levelChosen = random.choice(['medium', 'medium2'])
        app.numberOfPieces = 64
    if levelChosen == 'Hard':
        app.levelChosen = 'hard'
        app.numberOfPieces = 100
    if levelChosen != None:
        app.rows = app.cols = int(math.sqrt(app.numberOfPieces))
        createPieces(app)
        setActiveScreen('game')
    #used AI to help come up with this idea rather than 
    #having an Easy, Medium, and Hard screen which would be so much code

def levelSelected(app, mouseX, mouseY):
    x0, x1 = app.width//2 - app.width//2.5, app.width//2 + app.width//2.5
    if (x0 <= mouseX <= x1):
        if (2*app.height/5 - app.height//7 <= mouseY <= 2*app.height/5 + app.height//7):
            return 'Easy'
        if (3*app.height/5 - app.height//7 <= mouseY <= 3*app.height/5 + app.height//7):
            return 'Medium'
        if (4*app.height/5 - app.height//7 <= mouseY <= 4*app.height/5 + app.height//7):
            return 'Hard'
    else:
        return None

# def isInsideBoard(app, x, y, width, height):
#     return (app.boardLeft <= x <= app.boardLeft + app.boardWidth - width) or (app.boardTop <= y <= app.boardTop + app.boardHeight - height)
 
 
def game_onStep(app):
    if not app.gameWon:
        app.timer += 1
    else:
        handleWinDelay(app)

def handleWinDelay(app):
    app.winDelay -= 1
    if app.winDelay <= 0:
        setActiveScreen('win')

def game_onScreenEnd(app):
    app.draggingPiece = None

def game_onScreenStart(app):
    pass

# ai helped explain the jso to me, nothing else    
def createPieces(app):
    with open(f'{app.levelChosen}_edges.json', 'r') as f:
        app.edges = json.load(f)
    width, height = getCellSize(app)
    app.pieceList = []
    # need to create a grid at the bottom to place pieces, 
    # for 
    #     app.potentialStartPlaces = 
    for row in range(app.rows):
        for col in range(app.cols):
            correctX, correctY = getCellLeftTop(app, row, col)
            x = random.randint(0, int(app.width - width))
            y = random.randint(int(app.boardTop + app.boardHeight), int(app.height - height))
            print(correctX, correctY)
            angle = random.choice([0, 90, 180, 270])
            piece = Piece(x, y, width, height, correctX, correctY, row, col, angle)
            piece.edges = app.edges[f'{row},{col}']
            app.pieceList.append(piece)
    
    # #creating the knobs
    # for row in range(app.rows):
    #     for col in range(app.cols):
    #         piece = app.pieceList[row * app.cols + col]
    #         if col < app.cols - 1:
    #             value = random.choice([-1,1])
    #             piece.edges['right'] = value
    #             app.pieceList[row * app.cols + (col+1)].edges['left'] = -value
    
    #         if row < app.rows - 1:
    #             value = random.choice([-1,1])
    #             piece.edges['bottom'] = value
    #             app.pieceList[(row + 1) * app.cols + col].edges['top'] = -value

def instructions_redrawAll(app):
    drawLabel('Press s to shuffle nonplaced pieces', app.width / 2, app.height / 5, size = app.width/24)
    drawLabel('Press h for a hint regarding currently selected piece', app.width / 2, 2 * app.height / 5, size = app.width/24)
    drawLabel('Press c to automatically complete puzzle', app.width / 2, 3 * app.height / 5, size = app.width/24)
    drawLabel('Press r to rotate selected piece', app.width / 2, 4 * app.height / 5, size = app.width/24)

def instructions_onScreenStart(app):
    pass
def instructions_onMousePress(app, mouseX, mouseY):
    pass
def instructions_onMouseRelease(app, mouseX, mouseY):
    pass
def instructions_onMouseDrag(app, mouseX, mouseY):
    pass
    

def game_redrawAll(app):
    for piece in app.pieceList:
        drawPiece(app, piece)
    minutes, seconds = (app.timer//app.stepsPerSecond) // 60, (app.timer//app.stepsPerSecond) % 60
    drawLabel(f'{minutes}m, {seconds}s', app.width//2, app.height//2, size = 20)
    if app.hintPiece != None:
        drawRect(app.hintPiece.correctX, app.hintPiece.correctY, app.hintPiece.width, app.hintPiece.height, fill = None, border = 'red')
    drawBoard(app)
    drawBoardBorder(app)

def game_onKeyPress(app, key):
    if key == 'c':
        for piece in app.pieceList:
            piece.x, piece.y = piece.correctX, piece.correctY
            piece.angle = 0
            piece.locked = True
    if key == 'h':
        if app.draggingPiece != None:
            app.hintPiece = app.pieceList[app.draggingPiece]
            app.hints += 1
    if key == 's':
        for piece in app.pieceList:
            if not piece.locked:
                piece.x = random.randint(int(piece.width/2), int(app.width - piece.width))
                piece.y = random.randint(int(app.boardTop + app.boardHeight + piece.height / 2), int(app.height - piece.height/2))
    if key == 'r':
        if app.draggingPiece != None:
            currPiece = app.pieceList[app.draggingPiece]
            currPiece.angle += 90
    if gameWon(app) and not app.gameWon:
        minutes, seconds = (app.timer//app.stepsPerSecond) // 60, (app.timer//app.stepsPerSecond) % 60
        app.bestScores.append(f'{minutes}m, {seconds}s, Hints = {app.hints}')
        app.gameWon = True
        app.winDelay = app.stepsPerSecond * 2
    
def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col)
        
def drawCell(app, row, col):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)
    drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = None)#, border = 'black')
    
def drawBoardBorder(app):
    drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight, fill = None, border = 'black', borderWidth = 3)

def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)
    
def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = app.boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)
    
def drawPiece(app, piece):
    pieceImage = f'{app.levelChosen}/{app.levelChosen}_{piece.row}_{piece.col}.png'
    r = piece.width // 6
    drawImage(pieceImage, piece.x-r, piece.y-r, width = piece.width + r*2, height = piece.height + r*2, rotateAngle = piece.angle)


def getPiece(app, row, col):
    for piece in app.pieceList:
        if piece.row == row and piece.col == col:
            return piece
    return None

#ai written
def bringKnobsToFront(app, piece):
    neighbors = [
        (piece.row - 1, piece.col, 'bottom'),
        (piece.row + 1, piece.col, 'top'),
        (piece.row, piece.col - 1, 'right'),
        (piece.row, piece.col + 1, 'left'),
    ]
    for row, col, side in neighbors:
        if 0 <= row < app.rows and 0 <= col < app.cols:
            neighbor = getPiece(app, row, col)
            if neighbor and neighbor.locked and neighbor.edges[side] == 1:
                app.pieceList.remove(neighbor)
                app.pieceList.append(neighbor)

    
def game_onMousePress(app, mouseX, mouseY):
    app.draggingPiece = inPiece(app, mouseX, mouseY)
    if app.draggingPiece != None:
        # so that the piece will be on top/ layering isn't weird during movement
        piece = app.pieceList.pop(app.draggingPiece)
        app.pieceList.append(piece)
        app.draggingPiece = len(app.pieceList) - 1
        app.offsetX, app.offsetY = mouseX - piece.x, mouseY - piece.y
    
def game_onMouseRelease(app, mouseX, mouseY):
    if app.draggingPiece != None:
        currPiece = app.pieceList[app.draggingPiece]
        placePiece(app, currPiece)
        if currPiece.locked:
            app.hintPiece = None
    if gameWon(app) and not app.gameWon:
        app.gameWon = True
        app.winDelay = app.stepsPerSecond * 2
        app.bestScores.append(app.timer)
        
    
def game_onMouseDrag(app, mouseX, mouseY):
    if app.draggingPiece != None:
            currPiece = app.pieceList[app.draggingPiece]
            if not currPiece.locked:
                currPiece.x, currPiece.y = mouseX, mouseY
                currPiece.x = mouseX - app.offsetX
                currPiece.y = mouseY - app.offsetY

def inPiece(app, mouseX, mouseY):
    for i in range(len(app.pieceList)-1,-1,-1):
        piece = app.pieceList[i]
        if (piece.x <= mouseX <= piece.x + piece.width) and (piece.y <= mouseY <= piece.y + piece.height):
            return i
    return None
        
def placePiece(app, piece):
    cellWidth, cellHeight = getCellSize(app)
    tolerance = cellWidth // 4
    print(f'distance x: {abs(piece.x - piece.correctX)}, distance y: {abs(piece.y - piece.correctY)}, tolerance: {tolerance}')
    if abs(piece.x- piece.correctX) <= tolerance and abs(piece.y - piece.correctY) <= tolerance and piece.angle % 360 == 0:
        piece.x = piece.correctX
        piece.y = piece.correctY
        piece.locked = True
    else:
        piece.x, piece.y = piece.startX, piece.startY

def gameWon(app):
    for piece in app.pieceList:
        if not piece.locked:
             return False
    return True

def win_onScreenStart(app):
    pass

def win_onMousePress(app, mouseX, mouseY):
    buttonX = app.width//2
    buttonY = app.height//2 + 130
    button2Y = buttonY + 70
    buttonW = 200
    buttonH = 50
    if (buttonX - buttonW/2 <= mouseX <= buttonX + buttonW/2) and (buttonY - buttonH/2 <= mouseY <= buttonY + buttonH/2):
        setActiveScreen('start')
    if (buttonX - buttonW/2 <= mouseX <= buttonX + buttonW/2) and (button2Y - buttonH/2 <= mouseY <= button2Y + buttonH/2):
        setActiveScreen('bestScores')
    
def win_onStep(app):
    pass

def win_redrawAll(app):
    drawLabel('You Win!!', app.width // 2, app.height // 2, size = 50, bold = True, font = 'cursive')
    drawLabel('Congratulations', app.width // 2, app.height // 2 - 60, size = 30, font = 'cursive')
    drawLabel(f'{(app.timer//app.stepsPerSecond)}s', app.width//2, app.height//2 + 60, size = 20, font = 'cursive')
    drawLabel(f'Hints used: {app.hints}', app.width // 2, app.height // 2 - 33, font = 'cursive')
    buttonX = app.width//2
    buttonY = app.height//2 + 130
    buttonW = 200
    buttonH = 50
    button2Y = buttonY + 70
    drawRect(buttonX, buttonY, buttonW, buttonH, align='center', fill='forestGreen')
    drawLabel('Play Again', buttonX, buttonY, size=25, font = 'cursive')
    drawRect(buttonX, button2Y, buttonW, buttonH, align='center', fill='gold')
    drawLabel('See Best Scores', buttonX, button2Y, size=25, font = 'cursive')

def bestScores_onScreenStart(app):
    pass

def bestScores_redrawAll(app):
    app.bestScores.sort
    for i in range(len(app.bestScores)):
        bestScore = app.bestScores[i]
        drawLabel(bestScore, app.width/2, 20+20*i)

def bestScores_onMousePress(app, mouseX, mouseY):
    pass

def bestScores_onMouseRelease(app, mouseX, mouseY):
    pass

def main():
    runAppWithScreens(initialScreen='start')

main()