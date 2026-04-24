from cmu_graphics import *
from PIL import Image, ImageDraw
import os
import random
import math
import json
from sliceImage import sliceImage
from generateKnobs import generateKnobPieces, bakeKnobs, getImageAverage, bakeSilhouettes 
FONT = 'Chalkduster'

'''
Own image upload (place image in same folder as code), 
pieces with actual knobs, piece rotation, 
drag and drop with tolerance, 
highlight/ shadow selected piece (shadow is opposite of average pixel color), 
hints, shuffle, auto-place piece, 
auto-complete puzzle, 
win screen with animated confetti, timer,
best scores tracker for all difficulties
'''

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
        self.edges = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}

class Button:
    def __init__(self, cx, cy, width, height, text, color, textSize):
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.textSize = textSize

    def contains(self, mouseX, mouseY):
        return (self.cx - (self.width / 2) <= mouseX <= self.cx + (self.width/2) 
                and self.cy - (self.height/2) <= mouseY <= self.cy + (self.height/2))

    def draw(self):
        #shadow
        drawRect(self.cx + 6, self.cy + 6, self.width, self.height,
             align='center', fill='black', opacity=50)
        #drawRect
        drawRect(self.cx, self.cy, self.width, self.height,
                 align = 'center', fill = self.color, border = 'black', borderWidth = 2)
        drawLabel(self.text, self.cx, self.cy, size = self.textSize,
                  font = FONT, bold = True)
                
class Confetti:
    def __init__(self, app):
        self.colors = ['red', 'gold', 'forestGreen', 'dodgerBlue', 'hotPink', 'orange', 'cyan']
        self.reset(app)
    
    def reset(self, app):
        self.x = random.randint(0, app.width)
        self.y = random.randint(-app.height + (app.height // 2), 0)  # start above screen
        self.width = random.randint(6, 14)
        self.height = random.randint(4, 10)
        self.speed = random.uniform(1.5, 4.5)
        self.drift = random.uniform(-1.2, 1.2)
        self.angle = random.randint(0, 360)
        self.spin = random.uniform(-6, 6)
        self.color = random.choice(self.colors)

def onAppStart(app):
    app.title = 'SCRAMBLED!'
    app.backgroundColor = 'darkSlateGray'
    app.accentColor = 'gold'
    app.stepsPerSecond = 10
    app.height = 900
    app.width = 600
    app.boardLeft = 25
    app.boardTop = 25
    app.boardWidth = min(app.width - (app.boardLeft * 2), app.height - (app.boardTop * 2))
    app.boardHeight = app.boardWidth
    app.draggingPiece = None
    app.bestScores = {'Easy': [], 'Medium': [], 'Hard': [], 'Own Image': []}
    app.confetti = [Confetti(app) for _ in range(60)]
    createStartButtons(app)
    createPlayAgain(app)
    createWinButtons(app)
    createBackButton(app)
    createOwnImageButtons(app)
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
    app.ownImage = False

def createOwnImageButtons(app):
    app.ownImageName = ''
    app.ownImageStatus = ''
    app.ownImageDifficulty = 'own'
    app.ownImageRows = 5
    cx, cy = app.width//2, app.height // 2
    w, h = app.width//4, app.height//14
    app.ownImageButtons = [
        Button(app.width//4, cy, w, h, 'Easy', 'forestGreen', 18),
        Button(app.width//2, cy, w, h, 'Medium', 'gold', 18),
        Button(3*app.width//4, cy, w, h, 'Hard', 'crimson', 18),
    ]
    app.goButton = Button(app.width//2, cy + h*2, app.width//3, h, 'Go!', 'hotPink', 22)


def createStartButtons(app):
    cx, cy = app.width//2, app.height/6
    width, height = app.width // 2.5, app.height // 7
    textSize = app.width / 12
    app.startButtons = [Button(cx, 2*cy, width, height, 'Easy', 'forestGreen', textSize), 
                        Button(cx, 3*cy, width, height, 'Medium', 'gold', textSize),
                        Button(cx, 4*cy, width, height, 'Hard', 'crimson', textSize),
                        Button(cx, 5*cy, width, height, 'Own Image', 'hotPink', app.width // 18),
                        Button(cx, app.height - (app.height//28) - 10, app.width//5, app.height//14, 'Instructions', 'cyan', 15)]

def drawBackground(app):
    drawRect(0, 0, app.width, app.height, fill= app.backgroundColor)

def createBackButton(app):
    app.backButton = Button(app.width//2, app.height - app.height//10, app.width//3, app.height//14,'Back', 'crimson', app.width//22)

def createPlayAgain(app):
    app.playAgainButton = Button(app.width//2, app.height//2 + 160, (app.width//2), (app.height / 9), 'Play Again', 'forestGreen', 35)

def createWinButtons(app):
    cx, cy = app.width//2, app.height// 2 + 160
    width, height = (app.width/2), app.height / 9
    # textSize = 25
    app.winButtons = [Button(cx, cy + 130, width, height, 'See Best Scores', 'gold', 32)] + [app.playAgainButton]

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
    app.ownImage = False

def start_onMousePress(app, mouseX, mouseY):
    levelMap = {'Easy' : ((['easy', 'easy2']), 25), 
                'Medium' : ((['medium2']), 64),
                'Hard' : ((['hard']), 100)}
    for button in app.startButtons:
        if button.contains(mouseX, mouseY):
            if button.text == 'Instructions':
                setActiveScreen('instructions')
                return
            elif button.text == 'Own Image':
                ownImage_onScreenStart(app)
                setActiveScreen('ownImage')
                return
            else:
                levels, app.numberOfPieces = levelMap[button.text]
                app.levelChosen = random.choice(levels)
                app.rows = app.cols = int(math.sqrt(app.numberOfPieces))
                createPieces(app)
                setActiveScreen('game')
                return
    #used AI to help come up with this idea rather than 
    #having an Easy, Medium, and Hard screen which would be so much code

def start_onMouseRelease(app, mouseX, mouseY):
    pass

def start_onMouseDrag(app, mouseX, mouseY):
    pass

#create start screen, easy, medium, hard screens
def start_redrawAll(app):
    drawBackground(app)
    drawLabel(app.title, app.width//2, app.height/10, size = app.width//7, font = FONT, bold = True, fill = app.accentColor)
    drawLabel('Choose your difficulty!', app.width // 2, app.height/10 + app.height//9, size = app.width//20, font = FONT, fill = 'white')
    for button in app.startButtons:
        button.draw()

def ownImage_onScreenStart(app):
    pass

def ownImage_onMousePress(app, mouseX, mouseY):
    if app.backButton.contains(mouseX, mouseY):
        setActiveScreen('start')
    for button in app.ownImageButtons:
        if button.contains(mouseX, mouseY):
            if button.text == 'Easy': app.ownImageRows = 5
            elif button.text == 'Medium': app.ownImageRows = 8
            elif button.text == 'Hard': app.ownImageRows = 10
    if app.goButton.contains(mouseX, mouseY):
        if app.ownImageName != '':
            if not os.path.exists(app.ownImageName):
                app.ownImageStatus = 'File not found! Check the filename and try again.'
            else:
                processOwnImage(app, app.ownImageName, app.ownImageRows)
                app.ownImage = True
                app.ownImageStatus = 'Done! Starting game...'
                app.levelChosen = app.ownImageDifficulty
                app.numberOfPieces = app.ownImageRows ** 2
                app.rows = app.cols = app.ownImageRows
                createPieces(app)
                setActiveScreen('game')

#just had ai tell me what function to write
def processOwnImage(app, filename, rows):
    cols = rows
    difficultyLabel = {5: 'easy', 8: 'medium', 10:'hard'}[rows]
    folderName = f"{difficultyLabel}_{filename.split('.')[0]}"
    app.ownImageDifficulty = folderName
    sliceImage(app.ownImageName, folderName, rows, cols)
    edges = generateKnobPieces(folderName, rows, cols)
    bakeKnobs(folderName, rows, cols, edges)
    bakeSilhouettes(folderName, rows, cols)

def ownImage_onMouseDrag(app, mouseX, mouseY):
    pass

def ownImage_onKeyHold(app, mouseX, mouseY):
    pass

def ownImage_onKeyPress(app, key):
    if key == 'backspace':
        app.ownImageName = app.ownImageName[:-1]
    elif key == 'space':
        app.ownImageName += ' '
    elif len(key) == 1:
        app.ownImageName += key

def ownImage_redrawAll(app):
    drawBackground(app)
    drawLabel('Own Image', app.width//2, app.height//10, size=app.width//9, font=FONT, bold=True, fill=app.accentColor)
    drawRect(app.width//2, app.height//3, app.width*0.7, 50, align='center', fill='white', border='gold', borderWidth=2)
    displayText = app.ownImageName if app.ownImageName != '' else 'Step 2: Type image filename...'
    displayColor = 'black' if app.ownImageName else 'gray'
    drawLabel('Step 1 : Place image in same folder as this code', app.width//2, app.height//4 + 30, size=15, font=FONT, fill='white')
    drawLabel(displayText, app.width//2, app.height//3, size=18, font=FONT, fill=displayColor)
    drawLabel('Step 3 : Select your difficulty', app.width//2, app.height// 2 - 50, size=15, font=FONT, fill='white')
    # difficulty buttons
    for button in app.ownImageButtons:
        button.draw()
    app.goButton.draw()
    drawLabel(app.ownImageStatus, app.width//2, app.height*0.85, size=15, font=FONT, fill='gold')
    app.backButton.draw()

def instructions_onScreenStart(app):
    pass
def instructions_onMousePress(app, mouseX, mouseY):
    if app.backButton.contains(mouseX, mouseY):
        setActiveScreen('start')

def instructions_onMouseRelease(app, mouseX, mouseY):
    pass
def instructions_onMouseDrag(app, mouseX, mouseY):
    pass

def instructions_redrawAll(app):
    drawBackground(app)
    drawLabel('How to Play', app.width / 2, app.height/ 10 - 25, size = app.width //9, font = FONT, bold = True, fill = app.accentColor)
    drawLabel('Drag and Drop Pieces or Press Keys:', app.width / 2, app.height/ 10 + 42, size = app.width //27, font = FONT, bold = True, fill = app.accentColor)
    guidance = [('S', 'Shuffle unplaced pieces'),
                ('H', 'Hint for selected piece'),
                ('R', 'Rotate selected piece'),
                ('P', 'Place selected piece'),
                ('C', 'Auto-complete puzzle')]
    for i in range(len(guidance)):
        key, description = guidance[i]
        y = app.height // 4.5 + i * (app.height // 7)
        keyButton = Button(app.width // 6, y, app.width // 8, app.height // 12, key, app.accentColor, app.width//10)
        keyButton.draw()
        drawLabel(description, app.width//2.2 + app.width//8, y,
              size=app.width//22, font=FONT, fill='white')
    app.backButton.draw()
        
def game_onScreenStart(app):
    app.gameWon = False
    pass

def game_onScreenEnd(app):
    app.draggingPiece = None
 
def game_onStep(app):
    if not app.gameWon:
        app.timer += 1
    else:
        handleWinDelay(app)

def game_onMousePress(app, mouseX, mouseY):
    app.draggingPiece = inPiece(app, mouseX, mouseY)
    if app.draggingPiece != None:
        # so that the piece will be on top/ layering isn't weird during movement
        piece = app.pieceList.pop(app.draggingPiece)
        app.pieceList.append(piece)
        app.draggingPiece = len(app.pieceList) - 1
        app.offsetX, app.offsetY = mouseX - piece.x, mouseY - piece.y

def game_onMouseDrag(app, mouseX, mouseY):
    if app.draggingPiece != None:
            currPiece = app.pieceList[app.draggingPiece]
            if not currPiece.locked:
                currPiece.x, currPiece.y = mouseX, mouseY
                currPiece.x = mouseX - app.offsetX
                currPiece.y = mouseY - app.offsetY
    
def game_onMouseRelease(app, mouseX, mouseY):
    if app.draggingPiece != None:
        currPiece = app.pieceList[app.draggingPiece]
        placePiece(app, currPiece)
        if currPiece.locked:
            app.hintPiece = None
        completeGameWin(app)

def completeGameWin(app):
    if gameWon(app) and not app.gameWon:
        app.gameWon = True
        app.winDelay = app.stepsPerSecond * 2
        if app.numberOfPieces == 25: level = 'Easy'
        elif app.numberOfPieces == 64: level = 'Medium'
        else: level = 'Hard'
        app.bestScores[level].append((app.timer, app.ownImage))

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
    if key == 'p':
        if app.draggingPiece != None:
            piece = app.pieceList[app.draggingPiece]
            piece.x, piece.y = piece.correctX, piece.correctY
            piece.angle = 0
            app.hintPiece = None
            piece.locked = True
    if key == 's':
        for piece in app.pieceList:
            if not piece.locked:
                piece.x = random.randint(int(piece.width/2), int(app.width - piece.width))
                piece.y = random.randint(int(app.boardTop + app.boardHeight + piece.height / 2), int(app.height - piece.height/2))
    if key == 'r':
        if app.draggingPiece != None:
            currPiece = app.pieceList[app.draggingPiece]
            currPiece.angle += 90
    completeGameWin(app)

def game_redrawAll(app):
    drawBackground(app)
    for piece in app.pieceList:
        drawPiece(app, piece)
    minutes, seconds = (app.timer//app.stepsPerSecond) // 60, (app.timer//app.stepsPerSecond) % 60
    drawLabel(f'{minutes:02d}m, {seconds:02d}s', app.width//2, app.height//2 + app.boardHeight / (app.rows + 2), size = 20, font = FONT)
    # if app.hintPiece != None:
    #     r = app.hintPiece.width // 6
    #     pieceImage = f'{app.levelChosen}/{app.levelChosen}_{app.hintPiece.row}_{app.hintPiece.col}.png'
    #     drawImage(pieceImage, app.hintPiece.correctX - r, app.hintPiece.correctY - r,
    #             width=app.hintPiece.width + r*2, height=app.hintPiece.height + r*2,
    #             opacity=18)
    # if i just want a gold dashed border... which one do we prefer?
    if app.hintPiece != None:
        drawRect(app.hintPiece.correctX, app.hintPiece.correctY, app.hintPiece.width, app.hintPiece.height, fill = None, border = app.accentColor, borderWidth = 3, dashes = True, opacity = 30)
    drawBoard(app)
    drawBoardBorder(app)

def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col)
        
def drawCell(app, row, col):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)
    drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = None)
    
def drawBoardBorder(app):
    drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight, fill = None, border = app.accentColor, borderWidth = 3)
    
def drawPiece(app, piece):
    pieceImage = f'{app.levelChosen}/{app.levelChosen}_{piece.row}_{piece.col}.png'
    highlight = f'{app.levelChosen}/{app.levelChosen}_{piece.row}_{piece.col}_highlighted.png'
    r = max(4, int(piece.width // 8))
    if app.draggingPiece!= None and app.pieceList[app.draggingPiece] == piece:
        drawImage(highlight, piece.x-r+5, piece.y-r+5, width = piece.width + r*2, height = piece.height + r*2, rotateAngle = piece.angle) #, opacity = 100)
    drawImage(pieceImage, piece.x-r, piece.y-r, width = piece.width + r*2, height = piece.height + r*2, rotateAngle = piece.angle)

def win_onScreenStart(app):
    pass

def win_onStep(app):
    for confettiPiece in app.confetti:
        confettiPiece.y += confettiPiece.speed
        confettiPiece.x += confettiPiece.drift
        confettiPiece.angle += confettiPiece.spin
        if confettiPiece.y > app.height + 10:
            confettiPiece.reset(app)
            confettiPiece.y = random.randint(-25, 0)

def win_onMousePress(app, mouseX, mouseY):
    for button in app.winButtons:
        if button.contains(mouseX, mouseY):
            if button.text == 'Play Again':
                start_onScreenStart(app)
                setActiveScreen('start')
            elif button.text == 'See Best Scores':
                setActiveScreen('bestScores')
            return

def win_redrawAll(app):
    drawBackground(app)
    drawLabel(app.title, app.width//2, app.height/10, size=app.width//7, font=FONT, bold=True, fill=app.accentColor)
    drawLabel('You Win!!', app.width // 2, app.height // 4, size = app.width / 8, bold = True, font = FONT, fill = app.accentColor)
    minutes, seconds = (app.timer//app.stepsPerSecond) // 60, (app.timer//app.stepsPerSecond) % 60
    drawLabel(f'{minutes:02d}m, {seconds:02d}s', app.width//2, app.height//2 - 32, size = 30, font = FONT)
    drawLabel(f'Hints used: {app.hints}', app.width // 2, app.height // 2, font = FONT, size = 30)
    for button in app.winButtons:
        button.draw()
    for confettiPiece in app.confetti:
        drawRect(confettiPiece.x, confettiPiece.y, confettiPiece.width, confettiPiece.height, fill=confettiPiece.color, rotateAngle=confettiPiece.angle)

def bestScores_onScreenStart(app):
    pass

def bestScores_onMousePress(app, mouseX, mouseY):
    if app.playAgainButton.contains(mouseX, mouseY):
        start_onScreenStart(app)
        setActiveScreen('start')

def bestScores_onMouseRelease(app, mouseX, mouseY):
    pass

def bestScores_redrawAll(app):
    drawBackground(app)
    drawLabel(app.title, app.width // 2, app.height / 10, size = app.width // 7, font = FONT, fill = app.accentColor)
    drawColumns = [('Easy', 'forestGreen'),
                   ('Medium', 'gold'),
                   ('Hard', 'crimson')]
    colX = [app.width // 4, app.width // 2, 3*app.width//4]
    headerY = app.height // 5
    for i in range(len(drawColumns)):
        text, color = drawColumns[i]
        key = text
        x = colX[i]
        drawLabel(text, x, headerY, size = app.width // 25, font=FONT, bold=True, fill=color)
        scores = sorted(app.bestScores[key])
        if scores == []:
            drawLabel('No Scores Yet', x, headerY + app.height // 12, size=app.width // 40, font=FONT, fill='white')
        else:
            for j in range(len(scores[:5])):
                score = scores[j]
                y = headerY + app.height // 12 + j * (app.height // 11)
                if j == 0 and not scores[j][1]:
                    drawRect(x, y, app.width // 5, app.height // 12, align='center', fill='white', opacity=10)
                if scores[j][1]:
                    drawRect(x, y, app.width // 5, app.height // 12, align='center', fill='hotPink', opacity=29)
                    drawLabel('★ Pink = Own Image', app.width // 2, app.height - app.height // 10, size=14, font=FONT, fill='hotPink')
                minutes, seconds = (score[0] // app.stepsPerSecond) // 60, (score[0] // app.stepsPerSecond) % 60    
                drawLabel(f'#{j+1}  {minutes:02d}m {seconds:02d}s', x, y, size=app.width // 40, font=FONT, fill='white')
        app.playAgainButton.draw()

# ai helped explain the json to me, nothing else    
def createPieces(app):
    with open(f'{app.levelChosen}_edges.json', 'r') as f:
        app.edges = json.load(f)
    width, height = getCellSize(app)
    app.pieceList = []
    for row in range(app.rows):
        for col in range(app.cols):
            correctX, correctY = getCellLeftTop(app, row, col)
            x = random.randint(0, int(app.width - width))
            y = random.randint(int(app.boardTop + app.boardHeight), int(app.height - height))
            angle = random.choice([0, 90, 180, 270])
            piece = Piece(x, y, width, height, correctX, correctY, row, col, angle)
            piece.edges = app.edges[f'{row},{col}']
            app.pieceList.append(piece)

def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)
    
def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = app.boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)

def getPiece(app, row, col):
    for piece in app.pieceList:
        if piece.row == row and piece.col == col:
            return piece
    return None

def placePiece(app, piece):
    cellWidth, cellHeight = getCellSize(app)
    tolerance = cellWidth // 4
    if abs(piece.x- piece.correctX) <= tolerance and abs(piece.y - piece.correctY) <= tolerance and piece.angle % 360 == 0:
        piece.x = piece.correctX
        piece.y = piece.correctY
        # app.draggingPiece = None
        piece.locked = True
    # else:
    #     piece.x, piece.y = piece.startX, piece.startY
        
def inPiece(app, mouseX, mouseY):
    for i in range(len(app.pieceList)-1,-1,-1):
        piece = app.pieceList[i]
        if (piece.x <= mouseX <= piece.x + piece.width) and (piece.y <= mouseY <= piece.y + piece.height):
            return i
    return None

def gameWon(app):
    if app.pieceList == []: return False
    for piece in app.pieceList:
        if not piece.locked:
             return False
        else:
            app.draggingPiece = None
            return True

def handleWinDelay(app):
    app.winDelay -= 1
    if app.winDelay <= 0:
        setActiveScreen('win')

def main():
    runAppWithScreens(initialScreen='start')

main()