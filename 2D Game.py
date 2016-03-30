import pygame
import time
import random
import sys,os
import math

#Python 2.7
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)


class gfxHandler(object):
    def __init__(self):
        pass

    def loadGfxDictionary(self, file_name, imageIndicator, rows, columns, width, height, pictureXPadding, pictureYPadding):
        self.spriteSheet = pygame.image.load(file_name)
        imgTransparency = True
        
        if imageIndicator == "World Tiles":
            self.gfxDictionary = {}
            imgTransparency = False
        self.gfxDictionary.update({imageIndicator:{}}) #NESTED HASHTABLE

        for j in xrange(rows):
            for k in xrange(columns):
                #self.gfxDictionary[(j*k) + j] = self.getImage(self.getCoords((j*k) + j, width, height, pictureXPadding, pictureYPadding, rows, columns))
                self.gfxDictionary[imageIndicator].update({(j*k) + j:self.getImage(self.getCoords((j*k) + j, width, height, pictureXPadding, pictureYPadding, rows, columns), imgTransparency)})

    def getImage(self, Coords, requiresTransparency):
        image = pygame.Surface([Coords[2], Coords[3]])
        image.blit(self.spriteSheet, (0,0), Coords)
        if requiresTransparency == True:
            image.set_colorkey((0,0,0))
        return image

    def getCoords(self, tileRequested, tileWidth, tileHeight, pictureXPadding, pictureYPadding, gfxHandlerRows, gfxHandlerColumns):
        #print int((tileRequested%gfxHandlerColumns)*tileWidth)+(int(tileRequested%gfxHandlerColumns))*pictureXPadding
        #a = raw_input("")
        return (int((tileRequested%gfxHandlerColumns)*tileWidth)+(int(tileRequested%gfxHandlerColumns))*pictureXPadding,
                int((tileRequested/gfxHandlerColumns)*tileHeight)+(int(tileRequested/gfxHandlerColumns))*pictureYPadding,
                tileWidth,
                tileHeight)


    def textObjects(self, text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def largeMessageDisplay(self, text, myGameDisplay, myColor):
        largeText = pygame.font.Font("freesansbold.ttf", 135)
        textSurf, textRect = self.textObjects(text, largeText, myColor)
        textRect.center = ((displayWidth/2), (displayHeight/2))
        myGameDisplay.blit(textSurf, textRect)
        pygame.display.update()
        time.sleep(2)

    def smallMessageDisplay(self, text, lineNumber, myGameDisplay, myColor, displayWidth):
        smallText = pygame.font.Font("freesansbold.ttf", 16)
        textSurf, textRect = self.textObjects(text, smallText, myColor)
        textRect.center = ((displayWidth-60), 15 + (15*lineNumber))
        myGameDisplay.blit(textSurf, textRect)

    def drawWorld(self, myImage, myCoords, myGameDisplay):
        #pygame.draw.rect(myImage, grayConst, myCoords)
         myGameDisplay.blit(myImage, (myCoords[0], myCoords[1]))
        
    def drawObject(self, myFile, x, y, myGameDisplay):
        if myFile == "person.png":
            myGameDisplay.blit(PLAYER,(x,y))
            
    def drawObjectsAndParticles(self, myParticles, gameDisplay, tileLevelYLoc, tileLevelXLoc, tileToScreenYOffset, tileToScreenXOffset, tileHeight, tileWidth, displayWidth, displayHeight, y, x, gfx):
        self.drawWorld(PLAYER, (x, y), gameDisplay)
        for i in xrange(len(myParticles)):
            if myParticles[i][0] == "User Bullet":
                #print "x: " + str((1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) - myParticles[i][2]) * -tileWidth)
                #print "y: " + str((1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) - myParticles[i][3]) * -tileHeight)
                if ((1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) - myParticles[i][2]) * -tileWidth) + myParticles[i][8] > 0 and (1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) - myParticles[i][2]) * -tileWidth < displayWidth:
                    #self.drawObject("bullet" + str(myParticles[i][1]) + ".png", (1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) - myParticles[i][2]) * -tileWidth, (1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) - myParticles[i][3]) * -tileHeight, gameDisplay)
                    #print math.acos(myParticles[i][4]/float((myParticles[i][4]**2 + myParticles[i][5]**2)**.5))
                    #img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][myParticles[i][1]], (180*math.acos(myParticles[i][4]/float((myParticles[i][4]**2 + myParticles[i][5]**2)**.5)))/3.14159265358972)
                    self.drawWorld(myParticles[i][12], ((1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) - myParticles[i][2]) * -tileWidth, (1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) - myParticles[i][3]) * -tileHeight), gameDisplay)
                    
    def drawTiles(self, tileToScreenXOffset, tileToScreenYOffset, tileLevelYLoc, tileLevelXLoc, tileWidth, tileHeight, displayWidth, displayHeight, thisLevelMap, gfx, gameDisplay):
        for i in xrange(int(displayWidth/float(tileWidth))+2):
            for j in xrange(int(displayHeight/float(tileHeight))+2):
              self.drawWorld(gfx.gfxDictionary["World Tiles"][thisLevelMap[j+tileLevelYLoc][i+tileLevelXLoc]],
                          (((i-1)*tileWidth)+tileToScreenXOffset,
                          ((j-1)*tileHeight)+tileToScreenYOffset,
                          (((i-1)*tileWidth)+tileToScreenXOffset)+ tileWidth,
                          (((j-1)*tileHeight)+tileToScreenYOffset) + tileHeight), gameDisplay)

class gameLogicHandler(object):
    def keyPressAndGameEventHandler(self, exiting, lost, ammo, personXDelta, personYDelta, personSpeed, currentGun, shotsFiredFromMe, personXFacing, personYFacing):
        #HANDLE KEY PRESS/RELEASE/USER ACTIONS
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():                #ASK WHAT EVENTS OCCURRED
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                exiting = True
                lost = False
            #IF PLAYER MUST PRESS TRIGGER REPEATEDLY, FIRE ON KEY UP:
            #if event.type == pygame.KEYUP and keys[pygame.K_SPACE] and ammo >0:
            #   shotsFiredFromMe = True
            #   ammo = ammo - 1

            #IF PLAYER MUST PRESS TRIGGER REPEATEDLY, FIRE ON KEY DOWN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and ammo >0:
                    shotsFiredFromMe = True
                    ammo = ammo - 1
                if event.key == pygame.K_KP1 or event.key == pygame.K_1:
                    currentGun = 0
                if event.key == pygame.K_KP2 or event.key == pygame.K_2:
                    currentGun = 1
                if event.key == pygame.K_KP3 or event.key == pygame.K_3:
                    currentGun = 2
            
        i = 0
        personXDelta = 0
        personYDelta = 0                                #VS. ASK WHAT KEYS ARE DOWN AT THIS MOMENT.
        if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            personXDelta = personSpeed
            personXFacing = 1
            personYFacing = 0
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            personXDelta = -personSpeed
            personXFacing = -1
            personYFacing = 0
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            personYDelta = -personSpeed
            personYFacing = -1
            if personXDelta == 0:
                personXFacing = 0
        if keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            personYDelta = personSpeed
            personYFacing = 1
            if personXDelta == 0:
                personXFacing = 0
        #IF PLAYER SHOULD BE ABLE TO HOLD DOWN TRIGGER:
        #if keys[pygame.K_SPACE] and ammo >0:
        #    shotsFiredFromMe = True
        #    ammo = ammo - 1

        return exiting, lost, ammo, personXDelta, personYDelta, personSpeed, currentGun, shotsFiredFromMe, personXFacing, personYFacing

    def characterWallCollisionTest(self, thisLevelMap, tileLevelYLoc, tileLevelXLoc, tileToScreenYOffset, tileToScreenXOffset, personYDelta, personXDelta, personYDeltaButScreenOffset, personXDeltaButScreenOffset, tileHeight, tileWidth, personHeight, personWidth, personSpeed, y, x, timeSpentFalling, gravityYDelta, gravityAppliesToWorld):
        personYDelta = personYDelta + gravityYDelta
    #CHARACTER<->WALL COLLISION DETECTION:
    #COLLISION DETECTION ACTUALLY HAS TO CHECK 2 DIRECTIONS FOR EACH OF THE 4 CORNERS FOR 2D MOVEMENT:
    #EACH OF THESE 2x4 CHECKS ARE LABLED BELOW AND CODE IS MARKED INDICATING WHICH
    #CORNER CHECK IS OCCURRING. THIS WOULD BE GOOD ENOUGH IF WE JUST STOPPED THE CHARACTER
    #ON COLLISION. FOR A BETTER USER EXPERIENCE, IF USER IS MOVING IN 2 DIRECTIONS (FOR EX LEFT + DOWN),
    #BUT ONLY ONE DIRECTION (FOR EX: LEFT) COLLIDES, THEN WE WANT TO KEEP THE USER MOVING
    #IN THE 1 GOOD DIRECTION ONLY. THIS REQUIRES 2 COLLISION CHECKS @ EACH OF THE 8 POINTS BECAUSE
    #THE OUTCOME AND REMEDIATION OF A COLLISION CHECK ON ONE SIDE AFFECTS BY THE OUTCOME AND REMEDIATION
    #OF THE NEXT COLLISION CHECK @ 90deg/270deg DIFFERENT DIRECTION AND BECAUSE PLAYER'S CHARACTER IS SMALLER
    #THAN THE BLOCKS THE WORLD IS MADE OF.

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
        if (personXDelta > 0 and (thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))])) or ((personXDelta)< 0 and (thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + personYDelta + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+(-personXDeltaButScreenOffset + personXDelta)+ personXDeltaButScreenOffset)/float(tileWidth)))])):
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
        if (personYDelta < 0 and (thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y - (personYDeltaButScreenOffset + personSpeed) + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y - (personYDeltaButScreenOffset + personSpeed) + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))])) or (personYDelta > 0 and (thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + (-personYDeltaButScreenOffset + personSpeed + self.getNextGravityApplicationToWorld(gravityYDelta, timeSpentFalling, tileHeight)) + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + (-personYDeltaButScreenOffset + personSpeed + self.getNextGravityApplicationToWorld(gravityYDelta, timeSpentFalling, tileHeight)) + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))])):
            yok = 0
            personYDeltaButScreenOffset = 0
            personYDelta = 0
            if gravityAppliesToWorld == True and gravityYDelta != 0 and personYDelta + self.getNextGravityApplicationToWorld(gravityYDelta, timeSpentFalling, tileHeight) > 0:
                gravityYDelta = 0
                timeSpentFalling = 0
                personYDelta = -1
            
            
        #if (thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + (-personYDeltaButScreenOffset + personSpeed) + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (personHeight/float(tileHeight)) + tileLevelYLoc + (-tileToScreenYOffset/float(tileHeight)) + ((y + (-personYDeltaButScreenOffset + personSpeed) + personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (personWidth/float(tileWidth)) + tileLevelXLoc + (-tileToScreenXOffset/float(tileWidth)) + ((x+personXDelta + personXDeltaButScreenOffset)/float(tileWidth)))]):
        #    fallIfGravityOn = False
        #    timeSpentFalling = 0
        #    gravityYDelta = 0
        #    personYDelta = personYDelta - gravityYDelta - (min(gravityYDelta + (timeSpentFalling + 1) * .05, tileHeight/float(2)))
        #else:
        #    fallIfGravityOn = True
        #    timeSpentFalling = timeSpentFalling + 1
        #    personYDelta = personYDelta - (min(gravityYDelta + (timeSpentFalling + 1) * .05, tileHeight/float(2)))
            
            
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

        return yok, xok, tileLevelYLoc, tileLevelXLoc, personYDelta, personXDelta, personYDeltaButScreenOffset, personXDeltaButScreenOffset, timeSpentFalling, gravityYDelta


    def diagSpeedFix(self, XDelta, YDelta, speed):
        #FIX DIAGONAL SPEED INCREASE
        #  
        #  |\                                                                 |\
        #  | \                                                                | \
        # 5|  \ >5  -> solve for X and Y, while keeping x:y the same ratio:  Y|  \ 5
        #  |_  \                                                              |_  \
        #  |_|__\                                                             |_|__\
        #    5                                                                  X 
        #
        #PERSON/BULLET/ITEM SHOULD NOT TRAVEL FASTER JUST BECAUSE OF TRAVELING DIAGONALLY. THE CODE BELOW ADJUSTS FOR THIS:
        if XDelta != 0 and YDelta != 0:
            tempXDelta = (XDelta/abs(XDelta)) * (math.cos(math.atan(abs(YDelta/XDelta))) * speed)
            YDelta = (YDelta/abs(YDelta)) * (math.sin(math.atan(abs(YDelta/XDelta))) * speed)
            XDelta = tempXDelta
        return XDelta, YDelta

    def screenSynchWithCharacterMovement(self, yok, xok, personYDelta, personXDelta, displayHeight, displayWidth, tileToScreenYOffset, tileToScreenXOffset, personYDeltaButScreenOffset, personXDeltaButScreenOffset, tileHeight, tileWidth, tileLevelYLoc, tileLevelXLoc, playerYBlock, playerXBlock, y, x, thisLevelMapWidth, thisLevelMapHeight):

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
    #          |SCROLLING*|
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

    #*UNLESS SCREEN SCROLLING PUTS CAMERA VIEW OUTSIDE OF THE WORLD

        #(IS PLAYER MOVING TO THE LEFT TO LEAVE MIDDLE THIRD AND IS IT NOT THE CASE THAT SCREEN SCROLLING WOULD PLACE THE CAMERA FARTHER LEFT THAN WORLD START)    OR    (IS PLAYER MOVING TO THE RIGHT TO LEAVE MIDDLE THIRD AND IS IT NOT THE CASE THAT SCREEN SCROLLING WOULD PLACE CAMERA FARTHER RIGHT THAN WORLD END)?
        if xok == 1 and ((tileLevelXLoc > 0 and personXDelta < 0 and x + personXDelta < (1*displayWidth)/3.0 and personXDelta < 0) or (int(tileLevelXLoc - ((tileToScreenXOffset-personXDelta)/float(tileWidth)) + 2 + displayWidth/float(tileWidth)) < thisLevelMapWidth and personXDelta >0 and x + personXDelta > (2*displayWidth)/3.0)):
            tileToScreenXOffset = tileToScreenXOffset - personXDelta #MOVE CAMERA ALONG X AXIS
            personXDeltaButScreenOffset = -personXDelta #KEEP PLAYER'S CHARACTER FIXED @ MIDDLE 9TH EDGE
        else:
            personXDeltaButScreenOffset = 0

        if yok == 1 and ((tileLevelYLoc > 0 and personYDelta < 0 and y + personYDelta < (1*displayHeight)/3.0 and personYDelta < 0) or (int(tileLevelYLoc - ((tileToScreenYOffset-personYDelta)/float(tileHeight)) + 2 + displayHeight/float(tileHeight)) < thisLevelMapHeight and personYDelta >0 and y + personYDelta > (2*displayHeight)/3.0)):
            tileToScreenYOffset = tileToScreenYOffset - personYDelta #MOVE CAMERA ALONG X AXIS
            personYDeltaButScreenOffset = -personYDelta #KEEP PLAYER'S CHARACTER FIXED @ MIDDLE 9TH EDGE
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
        return personYDelta, personXDelta, tileToScreenYOffset, tileToScreenXOffset, personYDeltaButScreenOffset, personXDeltaButScreenOffset, tileLevelYLoc, tileLevelXLoc, playerYBlock, playerXBlock, y, x

    def generateparticles(self, shotsFiredFromMe, myParticles, personYFacing, personXFacing, playerYBlock, playerXBlock, tileHeight, tileWidth, DEFAULTBULLETSPEED, currentGun, gfx):
        if shotsFiredFromMe == True and not(personYFacing == 0 and personXFacing == 0):
            speed = DEFAULTBULLETSPEED #units are world blocks, not pixels!
            if personXFacing == 0:
                tempDX = 0 #THIS AVOIDS THE DIVIDE BY 0 ERROR
                if personYFacing == 0:
                    tempDY = 0
                    img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][currentGun], (180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/3.14159265358972)
                else:
                    tempDY = (personYFacing/float(abs(personYFacing))) * speed
                    img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][currentGun], ((-personYFacing/float(abs(personYFacing))) * 180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/3.14159265358972)
            else:
                if personYFacing == 0:
                    tempDX = (personXFacing/float(abs(personXFacing))) * speed
                    tempDY = 0
                    img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][currentGun], (180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/3.14159265358972)
                else:
                    tempDX = (personXFacing/float(abs(personXFacing))) * (math.cos(math.atan(abs(personYFacing/float(personXFacing)))) * speed)
                    tempDY = (personYFacing/float(abs(personYFacing))) * (math.sin(math.atan(abs(personYFacing/float(personXFacing)))) * speed)
                    img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][currentGun], ((-personYFacing/float(abs(personYFacing))) * 180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/3.14159265358972)
                           #Name, weapon, world X Loc, world Y Loc,  dx,    dy, damage, bounces remaining, bullet width px, bullet height px, speed
            myParticles.append(["User Bullet", currentGun, playerXBlock, playerYBlock, tempDX, tempDY, 10, 1, 16, 16, speed, DEFAULTBULLETSPEED, img]) #putting multiple instances of the image itself in the array because they could be rotated at different directions and putting a pointer to one image and then rotating many many times severly impacts FPS due to slow rotate method
            shotsFiredFromMe = False
        return myParticles, shotsFiredFromMe

    def moveParticlesAndHandleParticleCollision(self, myParticles, thisLevelMap):
        myDeletedParticles = []
        for i in xrange(len(myParticles)):
            if myParticles[i][2] + myParticles[i][4] + 1 > len(thisLevelMap[0]) or myParticles[i][3] + myParticles[i][5] + 1 > len(thisLevelMap) or myParticles[i][2] + myParticles[i][4] < 0 or myParticles[i][3] + myParticles[i][5] < 0:
                myDeletedParticles.append(i)
            else:
                myParticles[i][2] = myParticles[i][2] + myParticles[i][4]
                myParticles[i][3] = myParticles[i][3] + myParticles[i][5]
        for i in xrange(len(myDeletedParticles)):
            del myParticles[myDeletedParticles[i]-i]
        return myParticles

    def applyGravityToWorld(self, gravityYDelta, timeSpentFalling, tileHeight):
        return (min(gravityYDelta + (.00005 * (timeSpentFalling**2)), tileHeight / 3.0)), timeSpentFalling + 1

    def getNextGravityApplicationToWorld(self, gravityYDelta, timeSpentFalling, tileHeight):
        a, b = self.applyGravityToWorld(gravityYDelta, timeSpentFalling, tileHeight)
        return a

    def manageTimeAndFrameRate(self, lastTick, clock):
        timeElapsedSinceLastFrame = clock.get_time() - lastTick
        lastTick = clock.tick()
        return timeElapsedSinceLastFrame

    def alterAllSpeeds(self, timeElapsedSinceLastFrame, particleList, defaultPersonSpeed, personXDelta, personYDelta):
        #MAKE PARTICLE SPEED CHANGE BASED ON FRAME RATE
        personSpeedThisFrameRate = defaultPersonSpeed
        for i in xrange(len(particleList)):
            particleList[i][10] = particleList[i][11] * timeElapsedSinceLastFrame
            if particleList[i][4] < 0:
                particleList[i][4] = -particleList[i][10]
            elif particleList[i][4] > 0:
                particleList[i][4] = particleList[i][10]
            if particleList[i][5] < 0:
                particleList[i][5] = -particleList[i][10]
            elif particleList[i][5] > 0:
                particleList[i][5] = particleList[i][10]
        #REDUCE PARTICLE SPEED SO IT DOESN'T TRAVEL FASTER WHEN DIAGONAL
            particleList[i][4], particleList[i][5] = self.diagSpeedFix(particleList[i][4], particleList[i][5], particleList[i][10])
        if timeElapsedSinceLastFrame < 2000:
            personSpeedThisFrameRate = defaultPersonSpeed * timeElapsedSinceLastFrame
            
        personXDelta, personYDelta = self.diagSpeedFix(personXDelta, personYDelta, personSpeedThisFrameRate)
        return personSpeedThisFrameRate, particleList, personXDelta, personYDelta

class gameplayObject(object):
    pass

class characterObject(gameplayObject):
    pass


class particleObject(gameplayObject):
    pass

class worldObject(gameplayObject):
    pass

class game(object):
    def __init__(self, displayWidth, displayHeight):
        self.gravityYDelta = 0
        self.clock = pygame.time.Clock()
        self.displayWidth = displayWidth #1280 #960
        self.displayHeight = displayHeight #720 #540
        self.gameDisplay = pygame.display.set_mode((displayWidth, displayHeight))#, pygame.FULLSCREEN)
        pygame.display.set_caption("Generic 2D Game Template")
        self.tileSheetRows = 10
        self.tileSheetColumns = 1
        self.tileWidth = 64
        self.tileHeight = 64
        self.tileXPadding = 0
        self.tileYPadding = 0
        self.gfx = gfxHandler()
        self.gfx.loadGfxDictionary("spritesheet.png", "World Tiles", self.tileSheetRows, self.tileSheetColumns, self.tileWidth, self.tileHeight, self.tileXPadding, self.tileYPadding)
        self.gfx.loadGfxDictionary("bullets.png", "Particles", 3, 1, 16, 16, 0, 0)
        self.exiting = False
        self.lost = False
        self.personWidth = 32 #IN PIXELS
        self.personHeight = 32 #IN PIXELS
        self.ammo = 50000
        self.enemiesAlive = 0
        self.currentLevel = 0
        self.currentGun = 1
        self.myHealth = 100
        self.myParticles = [] #[NAME, X1, Y1, DX, DY, R, G, B, SPEED, 0]
        self.myEnemies = [] #[species, weapon, health, aggression, speed, img, x, y, dx, dy, width, height]
        self.gravityAppliesToWorld = False #CHOOSE TRUE FOR SLIDE-SCROLLER TYPE GAME, OR FALSE FOR RPG TYPE GAME!
        self.DEFAULTPERSONSPEED = .5 #PLAYER SPEED IN PIXELS/MILLISECOND
        self.personSpeed = 0 #ACTUAL PLAYER MOVEMENT BASED ON COMPUTER'S FRAME RATE
        self.personXDelta = 0
        self.DEFAULTBULLETSPEED = .01 #BULLET SPEED IN WORLD BLOCKS/MILLISECOND
        self.personXDeltaButScreenOffset = 0
        self.personYDelta = 0
        self.personYDeltaButScreenOffset = 0
        self.personXFacing = 0
        self.personYFacing = 0
        self.score = 0
        self.shotsFiredFromMe = False
        self.x = (((self.displayWidth/float(self.tileWidth))/2)*self.tileWidth)
        self.y = (((self.displayHeight/float(self.tileHeight))/2)*self.tileHeight)
        self.playerXBlock = 0
        self.playerYBlock = 0
        self.tileToScreenXOffset = 0
        self.tileToScreenYOffset = 0
        self.tileLevelYLoc = 14
        self.tileLevelXLoc = 14
        self.timeSpentFalling = 0 #This is important to track because falling velocity due to gravity is non-linear -9.8m/s^2
        self.thisLevelMap = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]
                        
        self.lastTick = 0
        self.thisLevelMapHeight = len(self.thisLevelMap)
        self.thisLevelMapWidth = len(self.thisLevelMap[0])
        self.timeElapsedSinceLastFrame = 0
        self.clock = pygame.time.Clock()
        self.myGameLogicHandler = gameLogicHandler()
        self.myGFXHandler = gfxHandler()

    def play(self):
        # GAME LOOP
        while not self.exiting:
            #FIGURE OUT HOW MUCH TIME HAS ELAPSED SINCE LAST FRAME WAS DRAWN
            self.timeElapsedSinceLastFrame = self.myGameLogicHandler.manageTimeAndFrameRate(self.lastTick, self.clock)
            
            #HANDLE KEY PRESSES AND PYGAME EVENTS
            self.exiting, self.lost, self.ammo, self.personXDelta, self.personYDelta, self.personSpeed, self.currentGun, self.shotsFiredFromMe, self.personXFacing, self.personYFacing = self.myGameLogicHandler.keyPressAndGameEventHandler(self.exiting, self.lost, self.ammo, self.personXDelta, self.personYDelta, self.personSpeed, self.currentGun, self.shotsFiredFromMe, self.personXFacing, self.personYFacing)

            #MAKE CHARACTER FACE THE DIRECTION THE USER INDICATED W/ KEYPRESS
            #[NOT IMPLEMENTED YET]

            #NOW THAT KEY PRESSES HAVE BEEN HANDLED, ADJUST THE SPEED OF EVERYTHING BASED ON HOW MUCH TIME ELAPSED SINCE LAST FRAME DRAW, AND PREVENT DIAGONAL SPEED UP ISSUE
            self.personSpeed, self.myParticles, self.personXDelta, self.personYDelta = self.myGameLogicHandler.alterAllSpeeds(self.timeElapsedSinceLastFrame, self.myParticles, self.DEFAULTPERSONSPEED, self.personXDelta, self.personYDelta)

            #CHECK FOR CHARACTER-WALL COLLISIONS & MOVE CHARACTER
            self.yok, self.xok, self.tileLevelYLoc, self.tileLevelXLoc, self.personYDelta, self.personXDelta, self.personYDeltaButScreenOffset, self.personXDeltaButScreenOffset, self.timeSpentFalling, self.gravityYDelta = self.myGameLogicHandler.characterWallCollisionTest(self.thisLevelMap, self.tileLevelYLoc, self.tileLevelXLoc, self.tileToScreenYOffset, self.tileToScreenXOffset, self.personYDelta, self.personXDelta, self.personYDeltaButScreenOffset, self.personXDeltaButScreenOffset, self.tileHeight, self.tileWidth, self.personHeight, self.personWidth, self.personSpeed, self.y, self.x, self.timeSpentFalling, self.gravityYDelta, self.gravityAppliesToWorld)

            #self.personXDelta, self.personYDelta = self.myGameLogicHandler.diagSpeedFix(self.personXDelta, self.personYDelta, self.personSpeed)

            #TODO: generateBadGuys()
            #TODO: badGuysMoveOrAttack()
            
            #SYNCH SCREEN WITH CHARACTER MOVEMENT
            self.personYDelta, self.personXDelta, self.tileToScreenYOffset, self.tileToScreenXOffset, self.personYDeltaButScreenOffset, self.personXDeltaButScreenOffset, self.tileLevelYLoc, self.tileLevelXLoc, self.playerYBlock, self.playerXBlock, self.y, self.x = self.myGameLogicHandler.screenSynchWithCharacterMovement(self.yok, self.xok, self.personYDelta, self.personXDelta, self.displayHeight, self.displayWidth, self.tileToScreenYOffset, self.tileToScreenXOffset, self.personYDeltaButScreenOffset, self.personXDeltaButScreenOffset, self.tileHeight, self.tileWidth, self.tileLevelYLoc, self.tileLevelXLoc, self.playerYBlock, self.playerXBlock, self.y, self.x, self.thisLevelMapWidth, self.thisLevelMapHeight)
            if self.gravityAppliesToWorld == True:
                self.gravityYDelta, self.timeSpentFalling = self.myGameLogicHandler.applyGravityToWorld(self.gravityYDelta, self.timeSpentFalling, self.tileHeight)
            #MOVE PARTICLES
            self.myParticles = self.myGameLogicHandler.moveParticlesAndHandleParticleCollision(self.myParticles, self.thisLevelMap)
            #GENERATE PARTICLES
            self.myParticles, self.shotsFiredFromMe = self.myGameLogicHandler.generateparticles(self.shotsFiredFromMe, self.myParticles, self.personYFacing, self.personXFacing, self.playerYBlock, self.playerXBlock, self.tileHeight, self.tileWidth, self.DEFAULTBULLETSPEED, self.currentGun, self.gfx)# (self.bullets, rain drops, snowflakes, etc...)
            #DRAW THE WORLD IN TILES BASED ON THE THE NUMBERS IN THE thisLevelMap ARRAY
            self.myGFXHandler.drawTiles(self.tileToScreenXOffset, self.tileToScreenYOffset, self.tileLevelYLoc, self.tileLevelXLoc, self.tileWidth, self.tileHeight, self.displayWidth, self.displayHeight, self.thisLevelMap, self.gfx, self.gameDisplay)
            #DRAW PEOPLE, ENEMIES, OBJECTS AND PARTICLES
            self.myGFXHandler.drawObjectsAndParticles(self.myParticles, self.gameDisplay, self.tileLevelYLoc, self.tileLevelXLoc, self.tileToScreenYOffset, self.tileToScreenXOffset, self.tileHeight, self.tileWidth, self.displayWidth, self.displayHeight, self.y, self.x, self.gfx)

            #DRAW GAME STATS
            #self.myGFXHandler.smallMessageDisplay("Health: " + str(self.myHealth), 0, self.gameDisplay, white, self.displayWidth)
            #self.myGFXHandler.smallMessageDisplay("Ammo: " + str(self.ammo), 1, self.gameDisplay, white, self.displayWidth)
            #self.myGFXHandler.smallMessageDisplay("Level: " + str(self.currentLevel), 2, self.gameDisplay, white, self.displayWidth)
            #self.myGFXHandler.smallMessageDisplay("Score: " + str(self.score), 3, self.gameDisplay, white, self.displayWidth)
            #self.myGFXHandler.smallMessageDisplay("Player X: " + str(self.playerXBlock), 4, self.gameDisplay, white, self.displayWidth)
            #self.myGFXHandler.smallMessageDisplay("Player Y: " + str(self.playerYBlock), 5, self.gameDisplay, white, self.displayWidth)
            #self.myGFXHandler.smallMessageDisplay("View X: " + str(self.tileLevelXLoc), 7, self.gameDisplay, white, self.displayWidth)
            #self.myGFXHandler.smallMessageDisplay("View Y: " + str(self.tileLevelYLoc), 8, self.gameDisplay, white, self.displayWidth)
            self.myGFXHandler.smallMessageDisplay("FPS: " + str(1000/max(1, self.timeElapsedSinceLastFrame)), 9, self.gameDisplay, white, self.displayWidth)
            pygame.display.update()
            if self.myHealth <= 0:
                self.lost = True
                self.exiting = True
                self.myGFXHandler.largeMessageDisplay("YOU LOSE", self.gameDisplay, white)
                self.gameDisplay.fill(black)
                self.myGFXHandler.largeMessageDisplay(str(self.score) + " pts", self.gameDisplay, white)

            
        #OUT OF THE GAME LOOP
        if self.lost == True:
            #LOST GAME ACTION HERE
            pass
        else:
            pygame.quit()
            quit()

pygame.init()
PLAYER = pygame.image.load("person.png")
#myCharacter = pygame.image.load(myFile)
myGame = game(1280, 720)
myGame.play()

