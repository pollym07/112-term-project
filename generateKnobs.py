#ai generated, but I edited a good amount
from PIL import Image, ImageDraw
import random
import json

def generateKnobPieces(difficulty, rows, cols):
    edges = dict()
    for row in range(rows):
        for col in range(cols):
            edges[f'{row},{col}'] = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
    for row in range(rows):
        for col in range(cols):
            if col < cols - 1:
                knob = random.choice([-1, 1])
                edges[f'{row},{col}']['right'] = knob
                edges[f'{row},{col+1}']['left'] = -knob
            if row < rows - 1:
                knob = random.choice([-1, 1])
                edges[f'{row},{col}']['bottom'] = knob
                edges[f'{row+1},{col}']['top'] = -knob 
    with open(f'{difficulty}_edges.json', 'w') as f:
        json.dump(edges, f)
    return edges

def bakeKnobs(difficulty, rows, cols, edges):
    pieces = {}
    pieceW = pieceH = None
    for row in range(rows):
        for col in range(cols):
            path = f'{difficulty}/{difficulty}_{row}_{col}.png'
            image = Image.open(path).convert('RGBA')
            pieces[f'{row},{col}'] = image
            pieceW, pieceH = image.size
    
    knobRadius = max(4, pieceW // 8)
    
    for row in range(rows):
        for col in range(cols):
            piece = pieces[f'{row},{col}'].copy()
            edge = edges[f'{row},{col}']
            canvas = Image.new('RGBA', (pieceW + knobRadius*2, pieceH + knobRadius*2), (0,0,0,0))
            canvas.paste(piece, (knobRadius, knobRadius))

            if edge['top'] == 1 and row > 0:
                above = pieces[f'{row-1},{col}']
                knobImg = above.crop((pieceW//2 - knobRadius, pieceH - knobRadius, pieceW//2 + knobRadius, pieceH))
                mask = Image.new('L', (knobRadius*2, knobRadius), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, knobRadius*2, knobRadius*2), fill=255)
                canvas.paste(knobImg, (pieceW//2, 0), mask)

            if edge['bottom'] == 1 and row < rows - 1:
                below = pieces[f'{row+1},{col}']
                knobImg = below.crop((pieceW//2 - knobRadius, 0, pieceW//2 + knobRadius, knobRadius))
                mask = Image.new('L', (knobRadius*2, knobRadius), 0)
                ImageDraw.Draw(mask).ellipse((0, -knobRadius, knobRadius*2, knobRadius), fill=255)
                canvas.paste(knobImg, (pieceW//2, pieceH + knobRadius), mask)  # y = pieceH + r

            if edge['left'] == 1 and col > 0:
                left_piece = pieces[f'{row},{col-1}']
                knobImg = left_piece.crop((pieceW - knobRadius, pieceH//2 - knobRadius, pieceW, pieceH//2 + knobRadius))
                mask = Image.new('L', (knobRadius, knobRadius*2), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, knobRadius*2, knobRadius*2), fill=255)
                canvas.paste(knobImg, (0, pieceH//2), mask)  # x=0, y accounts for r offset

            if edge['right'] == 1 and col < cols - 1:
                right_piece = pieces[f'{row},{col+1}']
                knobImg = right_piece.crop((0, pieceH//2 - knobRadius, knobRadius, pieceH//2 + knobRadius))
                mask = Image.new('L', (knobRadius, knobRadius*2), 0)
                ImageDraw.Draw(mask).ellipse((-knobRadius, 0, knobRadius, knobRadius*2), fill=255)
                canvas.paste(knobImg, (pieceW + knobRadius, pieceH//2), mask)  # x = pieceW + r

            # cut out holes for inward knobs (-1)
            draw = ImageDraw.Draw(canvas)
            if edge['top'] == -1:
                draw.ellipse((pieceW//2, 0, 2*knobRadius + pieceW//2, knobRadius*2), fill=(0,0,0,0))
            if edge['bottom'] == -1:
                draw.ellipse((pieceW//2, pieceH, 2*knobRadius + pieceW//2, pieceH + knobRadius*2), fill=(0,0,0,0))
            if edge['left'] == -1:
                draw.ellipse((0, pieceH//2, knobRadius*2, 2*knobRadius + pieceH//2), fill=(0,0,0,0))
            if edge['right'] == -1:
                draw.ellipse((pieceW, pieceH//2, pieceW + knobRadius*2, 2*knobRadius + pieceH//2), fill=(0,0,0,0))
            
            canvas.save(f'{difficulty}/{difficulty}_{row}_{col}.png')
    print(f'Done baking knobs for {difficulty}!')

if __name__ == '__main__':
    bakeKnobs('easy', 5, 5, generateKnobPieces('easy', 5, 5))
    bakeKnobs('easy2', 5, 5, generateKnobPieces('easy2', 5, 5))
    bakeKnobs('medium2', 8, 8, generateKnobPieces('medium2', 8, 8))
    bakeKnobs('hard', 10, 10, generateKnobPieces('hard', 10, 10))

def getImageAverage(difficulty, rows, cols):
    allPixels = []
    for row in range(rows):
        for col in range(cols):
            piece = Image.open(f'{difficulty}/{difficulty}_{row}_{col}.png').convert('RGBA')
            pixels = list(piece.getdata())
            allPixels += [(r, g, b) for r, g, b, a in pixels if a > 0]
    avgR = sum(p[0] for p in allPixels) // len(allPixels)
    avgG = sum(p[1] for p in allPixels) // len(allPixels)
    avgB = sum(p[2] for p in allPixels) // len(allPixels)
    maxColor = 255
    return maxColor - avgR, maxColor - avgG, maxColor - avgB

def bakeSilhouettes(difficulty, rows, cols):
    oppR, oppG, oppB = getImageAverage(difficulty, rows, cols)
    for row in range(rows):
        for col in range(cols):
            piece = Image.open(f'{difficulty}/{difficulty}_{row}_{col}.png').convert('RGBA')
            alpha = piece.split()[3]
            silhouette = Image.new('RGBA', piece.size, (0, 0, 0, 0))
            fill = Image.new('RGBA', piece.size, (oppR, oppG, oppB, 255))
            silhouette.paste(fill, mask=alpha)
            silhouette.save(f'{difficulty}/{difficulty}_{row}_{col}_highlighted.png')

if __name__ == '__main__':
    bakeSilhouettes('easy', 5, 5)
    bakeSilhouettes('easy2', 5, 5)
    bakeSilhouettes('medium2', 8, 8)
    bakeSilhouettes('hard', 10, 10)