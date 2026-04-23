from PIL import Image
import os

# ai wrote
def sliceImage(filename, difficulty, rows, cols):
    img = Image.open(filename)
    imgWidth, imgHeight = img.size
    if imgWidth < imgHeight:
        img = img.rotate(90, expand=True)
    pieceWidth = imgWidth // cols
    pieceHeight = imgHeight // rows
    
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
    sliceImage('cmu letters logo.png', 'medium', 8, 8)
    sliceImage('CMU.jpg', 'medium2', 8, 8)
    sliceImage('venice bridge.jpg', 'hard', 10, 10)
