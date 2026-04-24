# excluded code, ai generated
from PIL import Image, ImageDraw
import random
import json

def generateKnobPieces(difficulty, rows, cols):
    edges = {}
    for row in range(rows):
        for col in range(cols):
            edges[f'{row},{col}'] = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
    for row in range(rows):
        for col in range(cols):
            if col < cols - 1:
                value = random.choice([-1, 1])
                edges[f'{row},{col}']['right'] = value
                edges[f'{row},{col+1}']['left'] = -value
            if row < rows - 1:
                value = random.choice([-1, 1])
                edges[f'{row},{col}']['bottom'] = value
                edges[f'{row+1},{col}']['top'] = -value
    with open(f'{difficulty}_edges.json', 'w') as f:
        json.dump(edges, f)
    print(f'Saved {difficulty}_edges.json')
    return edges

def bakeKnobs(difficulty, rows, cols, edges):
    pieces = {}
    pieceW = pieceH = None
    for row in range(rows):
        for col in range(cols):
            path = f'{difficulty}/{difficulty}_{row}_{col}.png'
            img = Image.open(path).convert('RGBA')
            pieces[f'{row},{col}'] = img
            pieceW, pieceH = img.size
    
    r = max(4, pieceW // 8)
    
    for row in range(rows):
        for col in range(cols):
            piece = pieces[f'{row},{col}'].copy()
            edge = edges[f'{row},{col}']
            canvas = Image.new('RGBA', (pieceW + r*2, pieceH + r*2), (0,0,0,0))
            canvas.paste(piece, (r, r))

            if edge['top'] == 1 and row > 0:
                above = pieces[f'{row-1},{col}']
                knobImg = above.crop((pieceW//2 - r, pieceH - r, pieceW//2 + r, pieceH))
                mask = Image.new('L', (r*2, r), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, r*2, r*2), fill=255)
                canvas.paste(knobImg, (r + pieceW//2 - r, 0), mask)  # y=0, x accounts for r offset

            if edge['bottom'] == 1 and row < rows - 1:
                below = pieces[f'{row+1},{col}']
                knobImg = below.crop((pieceW//2 - r, 0, pieceW//2 + r, r))
                mask = Image.new('L', (r*2, r), 0)
                ImageDraw.Draw(mask).ellipse((0, -r, r*2, r), fill=255)
                canvas.paste(knobImg, (r + pieceW//2 - r, pieceH + r), mask)  # y = pieceH + r

            if edge['left'] == 1 and col > 0:
                left_piece = pieces[f'{row},{col-1}']
                knobImg = left_piece.crop((pieceW - r, pieceH//2 - r, pieceW, pieceH//2 + r))
                mask = Image.new('L', (r, r*2), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, r*2, r*2), fill=255)
                canvas.paste(knobImg, (0, r + pieceH//2 - r), mask)  # x=0, y accounts for r offset

            if edge['right'] == 1 and col < cols - 1:
                right_piece = pieces[f'{row},{col+1}']
                knobImg = right_piece.crop((0, pieceH//2 - r, r, pieceH//2 + r))
                mask = Image.new('L', (r, r*2), 0)
                ImageDraw.Draw(mask).ellipse((-r, 0, r, r*2), fill=255)
                canvas.paste(knobImg, (pieceW + r, r + pieceH//2 - r), mask)  # x = pieceW + r

            # cut out holes for inward knobs (-1)
            draw = ImageDraw.Draw(canvas)
            if edge['top'] == -1:
                draw.ellipse((r + pieceW//2 - r, 0, r + pieceW//2 + r, r*2), fill=(0,0,0,0))
            if edge['bottom'] == -1:
                draw.ellipse((r + pieceW//2 - r, pieceH, r + pieceW//2 + r, pieceH + r*2), fill=(0,0,0,0))
            if edge['left'] == -1:
                draw.ellipse((0, r + pieceH//2 - r, r*2, r + pieceH//2 + r), fill=(0,0,0,0))
            if edge['right'] == -1:
                draw.ellipse((pieceW, r + pieceH//2 - r, pieceW + r*2, r + pieceH//2 + r), fill=(0,0,0,0))
            
            canvas.save(f'{difficulty}/{difficulty}_{row}_{col}.png')
    print(f'Done baking knobs for {difficulty}!')

if __name__ == '__main__':
    bakeKnobs('easy', 5, 5, generateKnobPieces('easy', 5, 5))
    bakeKnobs('easy2', 5, 5, generateKnobPieces('easy2', 5, 5))
    bakeKnobs('medium2', 8, 8, generateKnobPieces('medium2', 8, 8))
    bakeKnobs('hard', 10, 10, generateKnobPieces('hard', 10, 10))

def getImageAverage(difficulty, rows, cols):
    all_pixels = []
    for row in range(rows):
        for col in range(cols):
            piece = Image.open(f'{difficulty}/{difficulty}_{row}_{col}.png').convert('RGBA')
            pixels = list(piece.getdata())
            all_pixels += [(r, g, b) for r, g, b, a in pixels if a > 0]
    avgR = sum(p[0] for p in all_pixels) // len(all_pixels)
    avgG = sum(p[1] for p in all_pixels) // len(all_pixels)
    avgB = sum(p[2] for p in all_pixels) // len(all_pixels)
    return 255 - avgR, 255 - avgG, 255 - avgB

def bakeSilhouettes(difficulty, rows, cols):
    oppR, oppG, oppB = getImageAverage(difficulty, rows, cols)
    for row in range(rows):
        for col in range(cols):
            piece = Image.open(f'{difficulty}/{difficulty}_{row}_{col}.png').convert('RGBA')
            _, _, _, alpha = piece.split()
            silhouette = Image.new('RGBA', piece.size, (0, 0, 0, 0))
            fill = Image.new('RGBA', piece.size, (oppR, oppG, oppB, 255))
            silhouette.paste(fill, mask=alpha)
            silhouette.save(f'{difficulty}/{difficulty}_{row}_{col}_highlighted.png')
    print(f'Done baking silhouettes for {difficulty}!')

# run after bakeKnobs so the PNGs already exist
if __name__ == '__main__':
    bakeSilhouettes('easy', 5, 5)
    bakeSilhouettes('easy2', 5, 5)
    bakeSilhouettes('medium2', 8, 8)
    bakeSilhouettes('hard', 10, 10)