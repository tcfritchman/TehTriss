'''
TehTriss - A Tetris clone.
Created on Aug 20, 2013
@author: Thomas Fritchman
'''

import pygame, sys, random, os, copy, math
from pygame.locals import *

# Game constants
FIELDWIDTH = 10
FIELDHEIGHT = 24
LEFTEDGE = 0
RIGHTEDGE = FIELDWIDTH - 1
BOTTOMEDGE = FIELDHEIGHT - 1
BLOCKSIZE = 16
WINDOWWIDTH = 160
WINDOWHEIGHT = 384
SHAPES = 7
FPS = 30
BLANK = None

# Color constants
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
CYAN = Color(0, 255, 255)
YELLOW = Color(255, 255, 0)
VIOLET = Color(192, 0, 255)
ORANGE = Color(255, 128, 0)

X = 0
Y = 1

LEFT = 'left'
RIGHT = 'right'
DOWN = 'down'
UP = 'up'
CLOCKWISE = 'clockwise'
COUNTERCLOCKWISE = 'counterclockwise'

BGCOLOR = BLACK


def main():
    global FPSCLOCK, DELAYCLOCK, DISPLAYSURF
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DELAYCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('TehTriss v0.1')
    
    while True:
        runGame()

def runGame():
    oldField = createNewField()
    direction = None # L, R keyboard movement
    rotate_direction = None # Tetromino rotation direction
    currentTetromino = generateTetromino() # Tetromino in play
    fallDelay = 3

    DISPLAYSURF.fill(BGCOLOR)

    while True: # main game loop -----------------------------------------------
        for iteration in xrange(FPS // fallDelay): # inner, full speed main loop
            for event in pygame.event.get(): # Event loop
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        direction = LEFT
                    elif event.key == K_RIGHT:
                        direction = RIGHT
                    elif event.key == K_DOWN:
                        direction = DOWN
                    elif event.key == K_UP:
                        rotate_direction = CLOCKWISE
                elif event.type == KEYUP:
                    if event.key == K_LEFT or event.key == K_RIGHT:
                        direction = None
    

            # copy old field into a new field var
            newField = copy.deepcopy(oldField)
            eraseTetrominoFromField(newField, currentTetromino)
    
            # real-time movement and control
            if direction == LEFT:
                if not leftWallCollision(newField, currentTetromino) and not leftBlockCollision(newField, currentTetromino):
                    currentTetromino.moveLeft()
                direction = None
            elif direction == RIGHT:
                if not rightWallCollision(newField, currentTetromino) and not rightBlockCollision(newField, currentTetromino):
                    currentTetromino.moveRight()
                direction = None
            elif direction == DOWN:
                # FOR TESTING ONLY
                currentTetromino.moveDown()
                direction = None
            
            # rotation logic including wall-kick
            if rotate_direction == CLOCKWISE:
                '''
                # first check for block collision
                if not rightBlockCollision(newField, currentTetromino) and not leftBlockCollision(newField, currentTetromino):
                    # check for wall collision
                    if leftWallCollision(newField, currentTetromino):
                        # attempt wall-kick
                        currentTetromino.moveRight()
                        currentTetromino.rotateCW()
                        # check for any collision after wall kick
                        if blockCollision(newField, currentTetromino):
                            currentTetromino.rotateCCW()
                            currentTetromino.moveLeft()
                    elif rightWallCollision(newField, currentTetromino):
                        # attemt wall-kick
                        currentTetromino.moveLeft()
                        currentTetromino.rotateCW()
                        # check for any collision after wall kick
                        if blockCollision(newField, currentTetromino):
                            currentTetromino.rotateCCW()
                            currentTetromino.moveRight()
                    else:
                        currentTetromino.rotateCW()
                rotate_direction = None
                '''                        
                currentTetromino.rotateCW()
                rotate_direction = None

                        

            
            # update current tetromino to gameField 
            drawTetrominoToField(newField, currentTetromino)

            # update gameField to screen
            drawField(newField, oldField)
            pygame.display.flip()
            oldField = copy.deepcopy(newField)
            FPSCLOCK.tick(FPS)

        # if tetromino collides with floor, time to make a new one
        # follows same screen update format as real-time loop
        newField = copy.deepcopy(oldField)
        eraseTetrominoFromField(newField, currentTetromino)
        if floorCollision(newField, currentTetromino) or verticalBlockCollision(newField, currentTetromino):
            #currentTetromino.moveUp()
            drawTetrominoToField(newField, currentTetromino)
            oldField = copy.deepcopy(newField)
            currentTetromino = generateTetromino()
        else:
            # block falls incrementally
            currentTetromino.moveDown()
            drawTetrominoToField(newField, currentTetromino)
            drawField(newField, oldField)
            pygame.display.flip()
            oldField = copy.deepcopy(newField)

        DELAYCLOCK.tick(fallDelay)

    # --------------------------------------------------------------------------

    
# Return empty field data structure
def createNewField():
    field = []
    for x in range(FIELDWIDTH):
        field.append([])
        for y in range(FIELDHEIGHT):
            field[x].append(BLANK)
    return field

# redraw the tetris field
def drawField(newField, oldField):
    for x in range(FIELDWIDTH):
        for y in range(FIELDHEIGHT):
            # TEST - COMMENTED OUT FOR TESTING PURPOSES ONLY TO PROVIDE ACCURATE PORTRAYAL OF PLAYING FIELD
            #if newField[x][y] != oldField[x][y]:
            # display only different blocks
            blockX = x * BLOCKSIZE
            blockY = y * BLOCKSIZE
            blockRect = pygame.Rect(blockX, blockY, BLOCKSIZE, BLOCKSIZE)
            drawBlock(newField[x][y], blockRect)

# check each block for collisions
# Types of collision:    Triggered by:
# 1. Wall                Left, Right, Rotate
# 2. Floor               Down, Rotate
# 3. Horizontal block    Left, Right, Rotate
# 4. Vertical block      Down, Rotate

# return True if block collides with either side of field
def leftWallCollision(field, tetromino):
    for coord in range(len(tetromino.coords)):
        # Check to see if block is out of vertical bounds
        block = tetromino.coords[coord][X]
        if block <= LEFTEDGE:
            return True
    return False

def rightWallCollision(field, tetromino):
    for coord in range(len(tetromino.coords)):
        # Check to see if block is out of vertical bounds
        block = tetromino.coords[coord][X]
        if block >= RIGHTEDGE:
            return True
    return False

def floorCollision(field, tetromino):
    for coord in range(len(tetromino.coords)):
        # Check to see of block has hit the floor
        block = tetromino.coords[coord][Y]
        if block >= BOTTOMEDGE:
            return True
    return False

def verticalBlockCollision(field, tetromino):
    for coord in range(len(tetromino.coords)):
        # Check to see if block is already occupied 
        blockX = tetromino.coords[coord][X]
        blockY = tetromino.coords[coord][Y]
        if field[blockX][blockY + 1] != BLANK:
            print blockX, ',', blockY
            return True
    return False

def leftBlockCollision(field, tetromino):
    for coord in range(len(tetromino.coords)):
        # Check to see if block is already occupied 
        blockX = tetromino.coords[coord][X]
        blockY = tetromino.coords[coord][Y]
        if field[blockX - 1][blockY] != BLANK:
            print blockX, ',', blockY
            return True
    return False

def rightBlockCollision(field, tetromino):
    for coord in range(len(tetromino.coords)):
        # Check to see if block is already occupied 
        blockX = tetromino.coords[coord][X]
        blockY = tetromino.coords[coord][Y]
        if field[blockX + 1][blockY] != BLANK:
            print blockX, ',', blockY
            return True
    return False

def blockCollision(field, tetromino):
    for coord in range(len(tetromino.coords)):
        # Check to see if block is already occupied 
        blockX = tetromino.coords[coord][X]
        blockY = tetromino.coords[coord][Y]
        if field[blockX][blockY] != BLANK:
            print blockX, ',', blockY
            return True
    return False


# draw a block to the field
def drawBlock(color, rect):
    if color == BLANK:
        pygame.draw.rect(DISPLAYSURF, BLACK, rect)
    else:
        pygame.draw.rect(DISPLAYSURF, color, rect)

# replaces all coordinates in a tetromino with BLANK
def eraseTetrominoFromField(field, tetromino):
    for i in range(len(tetromino.coords)):
        field[tetromino.coords[i][0]][tetromino.coords[i][1]] = BLANK

# writes all coordinates of a tetromino with that tetromino's color
def drawTetrominoToField(field, tetromino):
    # change color for each coordinate in tetromino
    for i in range(len(tetromino.coords)):
        field[tetromino.coords[i][0]][tetromino.coords[i][1]] = tetromino.color
        
# returns a random tetromino object
def generateTetromino():
    n = random.randint(1, SHAPES)
    if n == 1:
        return I()
    elif n == 2:
        return J()
    elif n == 3:
        return L()
    elif n == 4:
        return O()
    elif n == 5:
        return S()
    elif n == 6:
        return T()
    elif n == 7:
        return Z()
    

# the size, color, position, and coordinates which describe a Tetromino
class Tetromino(object):
    def __init__(self,
                 size,
                 color,
                 pos,
                 coords):
        self.size = size # size of encompassing square
        self.color = color # shape's display color
        self.pos = pos # location of square's top left corner
        self.coords = coords    # coordinates of each Block
                                # originally relative, then
                                # actual calculated using pos`
                               
    def moveUp(self): 
        offsetShape(self.coords, [0, -1])
        self.pos[Y] = self.pos[Y] - 1

    def moveDown(self): 
        offsetShape(self.coords, [0, 1])
        self.pos[Y] = self.pos[Y] + 1
    
    def moveLeft(self):
        offsetShape(self.coords, [-1, 0])
        self.pos[X] = self.pos[X] - 1
        
    def moveRight(self):
        offsetShape(self.coords, [1, 0])
        self.pos[X] = self.pos[X] + 1

    def rotateCW(self):
        # Rotate CCW 3 times
        for i in range(3):
            rotateShape(self.coords, self.size, self.pos)

        
    def rotateCCW(self):
        rotateShape(self.coords, self.size, self.pos)

#         #  
#       # # #
#
class T(Tetromino):
    # coordinates relative to pos

    def __init__(self):
        _shapeCoords = [[0, 1], [1, 0], [1, 1], [2, 1]]
        _startPos = [4, 0]
        offsetShape(_shapeCoords, _startPos) 
        super(T, self).__init__(3, VIOLET, _startPos, _shapeCoords)

#      #
#      # # #
#
class J(Tetromino):
    def __init__(self):
        _shapeCoords = [[0, 0], [0, 1], [1, 1], [2, 1]]
        _startPos = [4, 0]
        offsetShape(_shapeCoords, _startPos) 
        super(J, self).__init__(3, BLUE, _startPos, _shapeCoords)

#          #
#      # # #
#
class L(Tetromino):
    def __init__(self):
        _shapeCoords = [[0, 1], [1, 1], [2, 0], [2, 1]]
        _startPos = [4, 0]
        offsetShape(_shapeCoords, _startPos) 
        super(L, self).__init__(3, ORANGE, _startPos, _shapeCoords)

#        # #
#      # #  
#
class S(Tetromino):
    def __init__(self):
        _shapeCoords = [[0, 1], [1, 0], [1, 1], [2, 0]]
        _startPos = [4, 0]
        offsetShape(_shapeCoords, _startPos) 
        super(S, self).__init__(3, GREEN, _startPos, _shapeCoords)

#      # #  
#        # #
#
class Z(Tetromino):
    def __init__(self):
        _shapeCoords = [[0, 0], [1, 0], [1, 1], [2, 1]]
        _startPos = [4, 0]
        offsetShape(_shapeCoords, _startPos) 
        super(Z, self).__init__(3, RED, _startPos, _shapeCoords)

#       # #  
#       # #  
class O(Tetromino):
    def __init__(self):
        _shapeCoords = [[0, 0], [1, 0], [0, 1], [1, 1]]
        _startPos = [5, 0]
        offsetShape(_shapeCoords, _startPos) 
        super(O, self).__init__(2, YELLOW, _startPos, _shapeCoords)

#
#     # # # #
#            
#            
class I(Tetromino):
    def __init__(self):
        _shapeCoords = [[0, 1], [1, 1], [2, 1], [3, 1]]
        _startPos = [3, 0]
        offsetShape(_shapeCoords, _startPos) 
        super(I, self).__init__(4, CYAN, _startPos, _shapeCoords)
        




def offsetShape(shapeCoords, offset):        
    for i in range(len(shapeCoords)): # add start pos to shape's coordinates
        shapeCoords[i][0] = shapeCoords[i][0] + offset[0]
        shapeCoords[i][1] = shapeCoords[i][1] + offset[1]

def rotateShape(shapeCoords, size, pos):
    # return to relative coordinates
    negativePos = copy.deepcopy(pos)
    negativePos[0] *= -1
    negativePos[1] *= -1
    offsetShape(shapeCoords, negativePos)
    for i in range(len(shapeCoords)):
        x = shapeCoords[i][X]
        shapeCoords[i][X] = shapeCoords[i][Y]
        shapeCoords[i][Y] = size - x - 1
    offsetShape(shapeCoords, pos)
    
def load_bmp(name):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
            print 'Cannot load image:', fullname
            raise SystemExit, message
    return image, image.get_rect()

def isOdd(x):
    if x % 2 == 0:
        return False
    else:
        return True
    
def terminate():
    pygame.quit()
    sys.exit()
            
if __name__ == '__main__':
    main()