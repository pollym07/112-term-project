from PIL import Image
import os

#had ai write at first. then totally erased, had AI give me a brief,
#broad overview of what it wrote and went back in and rewrote myself

def sliceImage(filename, difficulty, rows, cols):
    image = Image.open(filename)
    imageWidth, imageHeight = image.size
    smallerSize = min(imageWidth, imageHeight)
    left = (imageWidth - smallerSize) // 2
    top = (imageHeight - smallerSize) // 2
    image = image.crop((left, top, left + smallerSize, top + smallerSize))

    pieceWidth, pieceHeight = smallerSize // cols, smallerSize // rows
    image = image.crop((0, 0, pieceWidth * cols, pieceHeight * cols))

    if not os.path.exists(difficulty):
        os.makedirs(difficulty)

    for row in range(rows):
        for col in range(cols):
            left, top = pieceWidth * col, pieceHeight * row
            piece = image.crop((left, top, left + pieceWidth, top + pieceHeight))
            piece.save(f'{difficulty}/{difficulty}_{row}_{col}.png')

if __name__ == '__main__':
    sliceImage('jungle easy photo.jpg', 'easy', 5, 5)
    sliceImage('CMU.jpg', 'easy2', 5, 5)
    sliceImage('CMU.jpg', 'medium2', 8, 8)
    sliceImage('venice bridge.jpg', 'hard', 10, 10)