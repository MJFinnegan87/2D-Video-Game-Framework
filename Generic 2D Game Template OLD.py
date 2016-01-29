import pygame
import time
import random
import sys,os
import math

#Python 2.7

class SpriteSheet(object):
    def __init__(self, file_name):
        self.sprite_sheet = pygame.image.load(file_name).convert()

    def get_image(self, Coords, tileWidth, tileHeight):
        image = pygame.Surface([tileWidth, tileHeight]).convert()
        image.blit(self.sprite_sheet, (0,0), Coords)
        image.set_colorkey((255,0,0))
        return image

    def send_coords(self, tileRequested, tileWidth, tileHeight):
        myTileDictionary = {0 : (0, 64, tileWidth, tileHeight),
                            1 : (0, 0, tileWidth, tileHeight),
                            2 : (0, 128, tileWidth, tileHeight)
                            }
        return myTileDictionary[tileRequested]


def textObjects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def largeMessageDisplay(text, myGameDisplay, myColor):
    largeText = pygame.font.Font("freesansbold.ttf", 135)
    textSurf, textRect = textObjects(text, largeText, myColor)
    textRect.center = ((displayWidth/2), (displayHeight/2))
    myGameDisplay.blit(textSurf, textRect)
    pygame.display.update()
    time.sleep(2)

def smallMessageDisplay(text, lineNumber, myGameDisplay, myColor, displayWidth):
    smallText = pygame.font.Font("freesansbold.ttf", 16)
    textSurf, textRect = textObjects(text, smallText, myColor)
    textRect.center = ((displayWidth-60), 15 + (15*lineNumber))
    myGameDisplay.blit(textSurf, textRect)

def drawWorld(myImage, myCoords, myGameDisplay):
    #pygame.draw.rect(myImage, grayConst, myCoords)
     myGameDisplay.blit(myImage, (myCoords[0], myCoords[1]))
    
def drawObject(myFile, x, y, myGameDisplay):
    myCharacter = pygame.image.load(myFile)
    myGameDisplay.blit(myCharacter,(x,y))


def drawTiles(tileToScreenXOffset, tileToScreenYOffset, tileLevelYLoc, tileLevelXLoc, tileWidth, tileHeight, displayWidth, displayHeight, thisLevelMap, mySpriteSheet, gameDisplay):
    for i in range((displayWidth/tileWidth)+2):
        for j in range((displayHeight/tileHeight)+2):
            drawWorld(mySpriteSheet.get_image(mySpriteSheet.send_coords(thisLevelMap[j+tileLevelYLoc][i+tileLevelXLoc], tileWidth, tileHeight), tileWidth, tileHeight),
                      (((i-1)*tileWidth)+tileToScreenXOffset,
                      ((j-1)*tileHeight)+tileToScreenYOffset,
                      (((i-1)*tileWidth)+tileToScreenXOffset)+ tileWidth,
                      (((j-1)*tileHeight)+tileToScreenYOffset) + tileHeight), gameDisplay)

def keyPressAndGameEventHandler(exiting, lost, ammo, personXDelta, personYDelta, personAccel, shotsFired):
    #HANDLE KEY PRESS/RELEASE/USER ACTIONS
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():                #ASK WHAT EVENTS OCCURRED
        if event.type == pygame.QUIT:
            exiting = True
            lost = False
        #IF PLAYER MUST PRESS TRIGGER REPEATEDLY, FIRE ON KEY UP:
        #if event.type == pygame.KEYUP and keys[pygame.K_SPACE] and ammo >0:
        #   shotsFired = True
        #   ammo = ammo - 1

        #IF PLAYER MUST PRESS TRIGGER REPEATEDLY, FIRE ON KEY DOWN:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and ammo >0:
            shotsFired = True
            ammo = ammo - 1
    i = 0
    personXDelta = 0
    personYDelta = 0                                #VS. ASK WHAT KEYS ARE DOWN AT THIS MOMENT.
    if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
        personXDelta = personAccel
    if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
        personXDelta = -personAccel
    if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
        personYDelta = -personAccel
    if keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
        personYDelta = personAccel
    #IF PLAYER SHOULD BE ABLE TO HOLD DOWN TRIGGER:
    #if keys[pygame.K_SPACE] and ammo >0:
    #   shotsFired = True
    #    ammo = ammo - 1

    return exiting, lost, ammo, personXDelta, personYDelta, personAccel, shotsFired

def characterWallCollisionTest(thisLevelMap, tileLevelYLoc, tileLevelXLoc, tileToScreenYOffset, tileToScreenXOffset, personYDelta, personXDelta, personYDeltaButScreenOffset, personXDeltaButScreenOffset, tileHeight, tileWidth, personHeight, personWidth, personAccel, y, x):
    
#CHARACTER<->WALL COLLISION DETECTION:
#COLLISION DETECTION ACTUALLY HAS TO CHECK 2 DIRECTIONS FOR EACH OF THE 4 CORNERS FOR 2D MOVEMENT:
#EACH OF THESE 2x4 CHECKS ARE LABLED BELOW AND CODE IS MARKED INDICATING WHICH
#CORNER CHECK IS OCCURRING. THIS WOULD BE GOOD ENOUGH IF WE JUST STOPPED THE CHARACTER
#ON COLLISION. FOR A BETTER USER EXPERIENCE, IF USER IS MOVING IN 2 DIRECTIONS (FOR EX LEFT + DOWN),
#BUT ONLY ONE DIRECTION (FOR EX: LEFT) COLLIDES, THEN WE WANT TO KEEP THE USER MOVING
#IN THE 1 GOOD DIRECTION ONLY. THIS REQUIRES 2 COLLISION CHECKS @ EACH OF THE 8 POINTS BECAUSE
#THE OUTCOME AND REMEDIATION OF A COLLISION CHECK ON ONE SIDE AFFECTS BY THE OUTCOME AND REMEDIATION
#OF THE NEXT COLLISION CHECK @ 90deg/270deg DIFFERENT DIRECTION.

#        A     B
#        ^     ^
#        |     |
#    H <-+-----+-> C
#        | _O_ |
#        |  |  |
#        | / \ |
#    G <-+-----+-> D
#        |     |
#        V     V
#        F     E

    yok = 1
    xok = 1
    needToRevert = 0
    #COLLISION CHECK @ C or @ D or @ H or @ G
    if ((personXDelta)> 0 and (thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))])) or ((personXDelta)< 0 and (thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))])):
        tempxok = xok #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
        temppersonXDeltaButScreenOffset = personXDeltaButScreenOffset #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
        temppersonXDelta = personXDelta #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
        xok = 0
        personXDeltaButScreenOffset = 0
        personXDelta = 0
        needToRevert = 1

    #COLLISION CHECK @ A or @ B or @ F or @ E 
    #IF WE HANDLED A COLLISION @ C, D, H, OR G OR NO COLLISION @ C, D, H, OR G OCCURED,
    #WOULD A COLLISION OCCUR @ A, B, F, OR E ??? (NOTE HOW THIS FORMULA IS DEPENDENT ON VARS ABOVE THAT WERE CHANGED!)
    if (personYDelta < 0 and (thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y - (personYDeltaButScreenOffset + personAccel) + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y - (personYDeltaButScreenOffset + personAccel) + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))])) or (personYDelta > 0 and (thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + (-personYDeltaButScreenOffset + personAccel) + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + (-personYDeltaButScreenOffset + personAccel) + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))])):
        yok = 0
        personYDeltaButScreenOffset = 0
        personYDelta = 0

    #RESET 1ST COLLISION CHECK PARAMATERS B/C NOW,
    #WE DON'T KNOW IF A COLLISION @ C or @ D or @ H or @ G WILL OCCUR
    #BECAUSE WE MAY HAVE HANDLED A COLLISION @ A, B, F, OR E.
    #KNOWING THIS BEFOREHAND AFFECTS THE OUTCOME OF COLLISION TEST.
    if needToRevert == 1:
        xok = tempxok
        personXDeltaButScreenOffset = temppersonXDeltaButScreenOffset
        personXDelta = temppersonXDelta

    #COLLISION CHECK @ C or @ D or @ H or @ G
    #NOW TEST FOR COLLISION @ C, D, H, OR G NOW KNOWING THAT WE HANDLED MAY HAVE HANDLED A COLLISION @ C, D, H, OR G
    #LIKEWISE, THIS FORMULA IS DEPENDENT ON VARS IN 2ND SECTION THAT CHANGED
    if ((personXDelta)> 0 and (thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))])) or ((personXDelta)< 0 and (thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))])):
        xok = 0
        personXDeltaButScreenOffset = 0
        personXDelta = 0
    return yok, xok, thisLevelMap, tileLevelYLoc, tileLevelXLoc, tileToScreenYOffset, tileToScreenXOffset, personYDelta, personXDelta, personYDeltaButScreenOffset, personXDeltaButScreenOffset, personHeight, personWidth, personAccel, y, x

def screenSynchWithCharacterMovement(yok, xok, personYDelta, personXDelta, displayHeight, displayWidth, tileToScreenYOffset, tileToScreenXOffset, personYDeltaButScreenOffset, personXDeltaButScreenOffset, tileHeight, tileWidth, tileLevelYLoc, tileLevelXLoc, playerYBlock, playerXBlock, y, x):


#        -COMPUTER SCREEN-
#          |          |
#          |          |
#          |          |
#          |          |
#          |          |
#          |          |
#          |          |
#          |          |
#          |          |
#----------+----------+--------------
#          |    IF    |
#          | PLAYER   |
#          | TRIES TO |
#          |   LEAVE  |
#          | THIS AREA|
#          |   THEN   |
#          | PREVENT  |
#          | AND START|
#          |  SCREEN  |
#          |SCROLLING |
#------------------------------------
#          |          |
#          |          |
#          |          |
#          |          |
#          |          |
#          |          |
#          |          |
#          |          |
#          |          |

    #TEST FOR PLAYER ATTEMPTING TO TRAVEL BEYOND MIDDLE 9TH OF SCREEN
    #TODO: IF WE'RE NOT CLOSE TO THE EDGE OF THE WORLD:
    if xok == 1 and ((x + personXDelta > (2*displayWidth)/3) or (x + personXDelta < (1*displayWidth)/3)):
        tileToScreenXOffset = tileToScreenXOffset - personXDelta
        personXDeltaButScreenOffset = -personXDelta
    else:
        personXDeltaButScreenOffset = 0
    if yok == 1 and ((y + personYDelta > (2*displayHeight)/3) or (y + personYDelta < (1*displayHeight)/3)):
        tileToScreenYOffset = tileToScreenYOffset - personYDelta
        personYDeltaButScreenOffset = -personYDelta
    else:
        personYDeltaButScreenOffset = 0

    #SCREEN MOVES IN PIXELS, BUT THE WORLD IS BUILT IN BLOCKS.
    #WHEN SCREEN MOVES IN PIXELS WITH USER'S MOVEMENT, THIS
    #IS STORED IN tileToScreen(X or Y)Offset. BUT IF USER'S
    #MOVEMENT (AND THEREFORE, tileToScreenX/YOffset) GOES BEYOND
    #THE SIZE OF A BLOCK, THEN TAKE AWAY THE BLOCK SIZE FROM THE 
    #tileToScreenX/YOffset, AND CONSIDER THAT THE USER HAS MOVED
    #1 BLOCK IN DISTANCE IN THE WORLD. THIS IS IMPORTANT IN
    #ACCURATELY TRACKING THE USER'S LOCATION COORDINATES HELD
    #IN playerX/YBlock
    if tileToScreenXOffset >= tileWidth:
        tileToScreenXOffset = tileToScreenXOffset - tileWidth
        tileLevelXLoc = tileLevelXLoc - 1
        
    elif tileToScreenXOffset <0:
        tileToScreenXOffset = tileToScreenXOffset + tileWidth
        tileLevelXLoc = tileLevelXLoc + 1

    if tileToScreenYOffset >= tileHeight:
        tileToScreenYOffset = tileToScreenYOffset - tileHeight
        tileLevelYLoc = tileLevelYLoc - 1

    elif tileToScreenYOffset <0:
        tileToScreenYOffset = tileToScreenYOffset + tileHeight
        tileLevelYLoc = tileLevelYLoc + 1
        
    if xok == 1:
        x = x + personXDelta + personXDeltaButScreenOffset #MOVE USER'S CHARACTER, BUT DON'T MOVE HIM IN ONE DIRECTION IF THE SCREEN SCROLL IS ALSO MOVING IN THAT DIRECTION
        playerXBlock = 1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + (x/float(tileWidth)) #0 BASED, JUST LIKE THE ARRAY, THIS IS LEFT MOST POINT OF USER'S CHAR
    if yok == 1:
        y = y + personYDelta + personYDeltaButScreenOffset #MOVE USER'S CHARACTER, BUT DON'T MOVE HIM IN ONE DIRECTION IF THE SCREEN SCROLL IS ALSO MOVING IN THAT DIRECTION
        playerYBlock = 1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + (y/float(tileHeight)) #0 BASED, JUST LIKE THE ARRAY, THIS IS TOP MOST POINT OF USER'S CHAR
    return yok, xok, personYDelta, personXDelta, displayHeight, displayWidth, tileToScreenYOffset, tileToScreenXOffset, personYDeltaButScreenOffset, personXDeltaButScreenOffset, tileHeight, tileWidth, tileLevelYLoc, tileLevelXLoc, playerYBlock, playerXBlock, y, x

def gameLoop():
    # INITIALIZATION
    tileWidth = 64
    tileHeight = 64
    grayConst = (128,128,128)
    black = (0,0,0)
    white = (255,255,255)
    red = (255,0,0)
    clock = pygame.time.Clock()
    displayWidth = 800 #960
    displayHeight = 600 #540
    myCharacter = ""
    gameDisplay = pygame.display.set_mode((displayWidth, displayHeight))
    pygame.display.set_caption("Generic 2D Game Template")
    exiting = False
    lost = False
    personWidth = 32
    personHeight = 32
    ammo = 50000
    enemiesAlive = 0
    currentLevel = 0
    currentGun = "Long Gun"
    myHealth = 100
    myparticles = [] #[NAME, X1, Y1, WIDTH, HEIGHT, R, G, B, SPEED, 0]
    myEnemies = [] #[species, weapon, health, aggression, speed, img, x, y, dx, dy, width, height]
    personAccel = 4 #FOR BEST PERFORMANCE, MAKE THIS A FACTOR OF SPRITE WIDTH & HEIGHT
    personXDelta = 0
    personXDeltaButScreenOffset = 0
    personYDelta = 0
    personYDeltaButScreenOffset = 0
    score = 0
    shotsFired = False
    x = (((displayWidth/float(tileWidth))/2)*tileWidth)
    y = (((displayHeight/float(tileHeight))/2)*tileHeight)
    playerXBlock = 0
    playerYBlock = 0
    tileToScreenXOffset = 0
    tileToScreenYOffset = 0
    tileLevelYLoc = 5
    tileLevelXLoc = 31
    mySpriteSheet = SpriteSheet("spritesheet.png")
    #myMainChar = SpriteSheet("person.png")
    thisLevelMap = [
        [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
        [2,1,0,2,1,0,2,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
        [2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
        [2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
        [2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]

    # GAME LOOP
    while not exiting:
        #HANDLE KEY PRESSES AND PYGAME EVENTS
        exiting, lost, ammo, personXDelta, personYDelta, personAccel, shotsFired = keyPressAndGameEventHandler(exiting, lost, ammo, personXDelta, personYDelta, personAccel, shotsFired)
        #CHECK FOR CHARACTER-WALL COLLISIONS
        yok, xok, thisLevelMap, tileLevelYLoc, tileLevelXLoc, tileToScreenYOffset, tileToScreenXOffset, personYDelta, personXDelta, personYDeltaButScreenOffset, personXDeltaButScreenOffset, personHeight, personWidth, personAccel, y, x = characterWallCollisionTest(thisLevelMap, tileLevelYLoc, tileLevelXLoc, tileToScreenYOffset, tileToScreenXOffset, personYDelta, personXDelta, personYDeltaButScreenOffset, personXDeltaButScreenOffset, tileHeight, tileWidth, personHeight, personWidth, personAccel, y, x)

        #TODO: generateBadGuys()
        #TODO: badGuysMoveOrAttack()
        #TODO: generateparticles() (bullets, rain drops, snowflakes, etc...)
        #TODO: moveparticlesAndHandleparticleCollision()
        
        #SYNCH SCREEN WITH CHARACTER MOVEMENT
        yok, xok, personYDelta, personXDelta, displayHeight, displayWidth, tileToScreenYOffset, tileToScreenXOffset, personYDeltaButScreenOffset, personXDeltaButScreenOffset, tileHeight, tileWidth, tileLevelYLoc, tileLevelXLoc, playerYBlock, playerXBlock, y, x = screenSynchWithCharacterMovement(yok, xok, personYDelta, personXDelta, displayHeight, displayWidth, tileToScreenYOffset, tileToScreenXOffset, personYDeltaButScreenOffset, personXDeltaButScreenOffset, tileHeight, tileWidth, tileLevelYLoc, tileLevelXLoc, playerYBlock, playerXBlock, y, x)
        #DRAW THE WORLD IN TILES BASED ON THE THE NUMBERS IN THE thisLevelMap ARRAY
        drawTiles(tileToScreenXOffset, tileToScreenYOffset, tileLevelYLoc, tileLevelXLoc, tileWidth, tileHeight, displayWidth, displayHeight, thisLevelMap, mySpriteSheet, gameDisplay)
        drawObject("person.png", x, y, gameDisplay)
        #drawWorld(myMainChar.get_image((0, 0, personWidth, personHeight)), (x, y, personWidth, personHeight))
        smallMessageDisplay("Health: " + str(myHealth), 0, gameDisplay, white, displayWidth)
        smallMessageDisplay("Ammo: " + str(ammo), 1, gameDisplay, white, displayWidth)
        smallMessageDisplay("Level: " + str(currentLevel), 2, gameDisplay, white, displayWidth)
        smallMessageDisplay("Score: " + str(score), 3, gameDisplay, white, displayWidth)
        #smallMessageDisplay("Player X: " + str(playerXBlock), 4, gameDisplay, white, displayWidth)
        #smallMessageDisplay("Player Y: " + str(playerYBlock), 5, gameDisplay, white, displayWidth)
        #smallMessageDisplay("  " + str(thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))]),7, gameDisplay, white, displayWidth)
        #smallMessageDisplay("  " + str(thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))]) , 8, gameDisplay, white, displayWidth)
        #smallMessageDisplay("View X: " + str(tileLevelXLoc), 7, gameDisplay, white, displayWidth)
        #smallMessageDisplay("View Y: " + str(tileLevelYLoc), 8, gameDisplay, white, displayWidth)
        pygame.display.update()
        clock.tick(60)
        if myHealth <= 0:
            lost = True
            exiting = True
            largeMessageDisplay("YOU LOSE", gameDisplay, white)
            gameDisplay.fill(black)
            largeMessageDisplay(str(score) + " pts", gameDisplay, white)

        
    #OUT OF THE GAME LOOP
    if lost == True:
        gameLoop()
    pygame.quit()
    quit()

pygame.init()
gameLoop()
