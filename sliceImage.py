from PIL import Image
import os

# ai wrote
def sliceImage(filename, difficulty, rows, cols):
    img = Image.open(filename).convert('RGBA')
    imgWidth, imgHeight = img.size

    size = min(imgWidth, imgHeight)
    left = (imgWidth - size) // 2
    top = (imgHeight - size) // 2
    img = img.crop((left, top, left + size, top + size))
    
    pieceWidth = size // cols
    pieceHeight = size // rows
    img = img.crop((0, 0, pieceWidth * cols, pieceHeight * rows))
    
    if not os.path.exists(difficulty):
        os.makedirs(difficulty)
    
    for row in range(rows):
        for col in range(cols):
            left = col * pieceWidth
            top = row * pieceHeight
            right = left + pieceWidth
            bottom = top + pieceHeight
            piece = img.crop((left, top, right, bottom))
            piece.save(f'{difficulty}/{difficulty}_{row}_{col}.png')


if __name__ == '__main__':
    sliceImage('jungle easy photo.jpg', 'easy', 5, 5)
    sliceImage('CMU.jpg', 'easy2', 5, 5)
    sliceImage('CMU.jpg', 'medium2', 8, 8)
    sliceImage('venice bridge.jpg', 'hard', 10, 10)
