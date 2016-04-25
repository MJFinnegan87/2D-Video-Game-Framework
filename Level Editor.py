import pygame
import time
import random
import sys,os
import math
import sqlite3

#Python 2.7
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)


class gfxHandler(object):
    def __init__(self):
        self.gfxDictionary = {}

    def loadGfxDictionary(self, file_name, imageIndicator, rows, columns, width, height, pictureXPadding, pictureYPadding):
        self.spriteSheet = pygame.image.load(file_name)
        imgTransparency = True
        
        if imageIndicator == "World Tiles":# or imageIndicator == "Level Editor Frame":
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

    def drawImg(self, myImage, myCoords, myGameDisplay):
        #pygame.draw.rect(myImage, grayConst, myCoords)
         myGameDisplay.blit(myImage, (myCoords[0], myCoords[1]))

    def drawDialogs(self, conversationArray, (backR, backG, backB, backA), (foreR, foreG, foreB, foreA), (borderR, borderG, borderB, borderA), borderSize = 5):        
        conversationSelections = []
        return conversationSelections
    
    def drawObjectsAndParticles(self, myParticles, gameDisplay, camera, tileHeight, tileWidth, y, x):
        #self.drawImg(PLAYER, (x, y), gameDisplay)
        for i in xrange(len(myParticles)):
            if myParticles[i][0] == "User Bullet":
                #print "x: " + str((1 + cameraViewX + (-cameraViewToScreenPxlOffsetX/float(tileWidth)) - myParticles[i][2]) * -tileWidth)
                #print "y: " + str((1 + cameraViewY + (-cameraViewToScreenPxlOffsetY/float(tileHeight)) - myParticles[i][3]) * -tileHeight)
                if ((1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - myParticles[i][2]) * -tileWidth) + myParticles[i][8] > 0 and (1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - myParticles[i][2]) * -tileWidth < camera.displayWidth:
                    #self.drawObject("bullet" + str(myParticles[i][1]) + ".png", (1 + cameraViewX + (-cameraViewToScreenPxlOffsetX/float(tileWidth)) - myParticles[i][2]) * -tileWidth, (1 + cameraViewY + (-cameraViewToScreenPxlOffsetY/float(tileHeight)) - myParticles[i][3]) * -tileHeight, gameDisplay)
                    #print math.acos(myParticles[i][4]/float((myParticles[i][4]**2 + myParticles[i][5]**2)**.5))
                    #img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][myParticles[i][1]], (180*math.acos(myParticles[i][4]/float((myParticles[i][4]**2 + myParticles[i][5]**2)**.5)))/3.14159265358972)
                    self.drawImg(myParticles[i][12], ((1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - myParticles[i][2]) * -tileWidth, (1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) - myParticles[i][3]) * -tileHeight), gameDisplay)

    def drawWorldInCameraView(self, camera, tileWidth, tileHeight, thisLevelMap, gameDisplay, LEFrame):
        for i in xrange(int(camera.displayWidth/float(tileWidth))+2-LEFrame.frameWidth):
            for j in xrange(int(camera.displayHeight/float(tileHeight))+2):
                try:
                    self.drawImg(self.gfxDictionary["World Tiles"][thisLevelMap[j+camera.viewY][i+camera.viewX]],
                          (((i-1)*tileWidth)+camera.viewToScreenPxlOffsetX,
                          ((j-1)*tileHeight)+camera.viewToScreenPxlOffsetY,
                          (((i-1)*tileWidth)+camera.viewToScreenPxlOffsetX)+ tileWidth * camera.zoom,
                          (((j-1)*tileHeight)+camera.viewToScreenPxlOffsetY) + tileHeight * camera.zoom), gameDisplay)
                except:
                    pass

    def convertScreenCoordsToTileCoords(self, coordinates, camera, tileWidth, tileHeight):
##        for event in pygame.event.get():
##            print str(event)
        return int(coordinates[0]/float(tileWidth) - camera.viewToScreenPxlOffsetX/float(tileWidth) + float(camera.viewX) + 1), int(coordinates[1]/float(tileHeight) - camera.viewToScreenPxlOffsetY/float(tileHeight) + float(camera.viewY) + 1)
    
class levelEditorFrame(object):
    def __init__(self):
        self.frameWidth = 4
        self.frameHeight = 16
        self.paletteY = 3
        self.paletteX = 1
        self.paletteSelectL = 0
        self.paletteSelectR = 0
        
    def drawLevelEditorFrame(self, camera, tileWidth, tileHeight, thisLevelMap, gfx, gameDisplay):
        for i in xrange(int(camera.displayWidth/float(tileWidth))-self.frameWidth, int(camera.displayWidth/float(tileWidth))+(self.frameWidth-1)):
            for j in xrange(int(camera.displayHeight/float(tileHeight))+2):
              gfx.drawImg(gfx.gfxDictionary["Level Editor Frame"][1],
                          (((i-1)*tileWidth),
                          ((j-1)*tileHeight),
                          (((i-1)*tileWidth))+ tileWidth,
                          (((j-1)*tileHeight)) + tileHeight), gameDisplay)
    def drawTextUI(self):
        pass

    def drawTileAndObjectPalette(self, camera, tileWidth, tileHeight, gfx, gameDisplay):
        for eachPaletteSelector in range(2): #FOR EACH LEFT AND RIGHT SELECTOR
            if eachPaletteSelector == 0:
                thisPaletteSelector = self.paletteSelectL
            elif eachPaletteSelector == 1:
                thisPaletteSelector = self.paletteSelectR
            gfx.drawImg(gfx.gfxDictionary["World Tiles"][thisPaletteSelector],
                          ((int(camera.displayWidth/float(tileWidth))-self.frameWidth + eachPaletteSelector)*tileWidth,
                          (1)*tileHeight,
                          (int(camera.displayWidth/float(tileWidth))-self.frameWidth + eachPaletteSelector)*tileWidth,
                          (2) * tileHeight), gameDisplay)
                                        
        for i in xrange(len(gfx.gfxDictionary["World Tiles"])):
                    gfx.drawImg(gfx.gfxDictionary["World Tiles"][i],
                          ((int(camera.displayWidth/float(tileWidth))-self.frameWidth + self.paletteX - 1)*tileWidth,
                          (i+self.paletteY)*tileHeight,
                          (int(camera.displayWidth/float(tileWidth))-self.frameWidth + self.paletteX - 1)*tileWidth,
                          (i+self.paletteY) + tileHeight), gameDisplay)

    def paletteItemSelect(self, userMouse, camera, tileWidth, tileHeight):
        if userMouse.btn[0] == 1:
            self.paletteSelectL = int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))
        if userMouse.btn[2] == 1:
            self.paletteSelectR = int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))
        return self
            
class logicHandler(object):
    def mouseEventHandler(self, userMouse, camera, displayFrame, tileWidth, tileHeight, thisLevelMap):
        self.displayFrame = displayFrame
        self.thisLevelMap = thisLevelMap
        if userMouse.btn[0] == 1 or userMouse.btn[2] == 1:
            if (userMouse.coords[0] >= (int(camera.displayWidth/float(tileWidth)) - self.displayFrame.frameWidth + self.displayFrame.paletteX - 1)*tileWidth) and (userMouse.coords[0] <= (int(camera.displayWidth/float(tileWidth)) - self.displayFrame.frameWidth + self.displayFrame.paletteX - 1)*tileWidth + tileWidth) and userMouse.coords[1] >= self.displayFrame.paletteY * tileHeight + 1:
                self.displayFrame = self.displayFrame.paletteItemSelect(userMouse, camera, tileWidth, tileHeight)
            else:
                self.editLevel(userMouse, displayFrame.paletteSelectL, displayFrame.paletteSelectR, thisLevelMap)
        return self.displayFrame, self.thisLevelMap

    def editLevel(self, userMouse, paletteSelectL, paletteSelectR, thisLevelMap):
        if userMouse.btn[2] == 1:
            thisLevelMap[userMouse.yTile][userMouse.xTile] = paletteSelectR
        if userMouse.btn[0] == 1:
            thisLevelMap[userMouse.yTile][userMouse.xTile] = paletteSelectL
        return thisLevelMap

    def keyPressAndGameEventHandler(self, exiting, lost, ammo, personXDelta, personYDelta, personSpeed, currentGun, shotsFiredFromMe, personXFacing, personYFacing):
        #HANDLE KEY PRESS/RELEASE/USER ACTIONS
        enterPressed = False
        keys = pygame.key.get_pressed()
        mouseCoords = pygame.mouse.get_pos()
        mouseBtn = pygame.mouse.get_pressed()
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
                if event.key == pygame.K_KP4 or event.key == pygame.K_4:
                    currentGun = 3
                if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                    enterPressed = True
            
        personXDelta = 0
        personYDelta = 0                                #VS. ASK WHAT KEYS ARE DOWN AT THIS MOMENT.
        if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            personXDelta = personSpeed
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            personXDelta = -personSpeed
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            personYDelta = -personSpeed
        if keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            personYDelta = personSpeed

        if personXDelta != 0 or personYDelta != 0:
            personXFacing = 0
            personYFacing = 0
            if personXDelta != 0:
                personXFacing = personXDelta/abs(personXDelta)
            if personYDelta != 0:
                personYFacing = personYDelta/abs(personYDelta)

            
        #IF PLAYER SHOULD BE ABLE TO HOLD DOWN TRIGGER:
        #if keys[pygame.K_SPACE] and ammo >0:
        #    shotsFiredFromMe = True
        #    ammo = ammo - 1

        return exiting, lost, ammo, personXDelta, personYDelta, personSpeed, currentGun, shotsFiredFromMe, personXFacing, personYFacing, enterPressed, mouseCoords, mouseBtn

    def cameraWorldEdgeCollisionCheck(self, thisLevelMap, camera, personXDelta, personYDelta, tileWidth, tileHeight, LEFrame):
        #SNAP CAMERA TO THE EDGE OF THE WORLD IF PAST IT
        atWorldEdgeX = False
        atWorldEdgeY = False
            #camera X  +      tiles on screen              +        frac. person next move         +   frac camera X                                         
        if (camera.viewX + (camera.displayWidth/float(tileWidth)) + (personXDelta/float(tileWidth)) - LEFrame.frameWidth - (camera.viewToScreenPxlOffsetX/float(tileWidth)) >= len(thisLevelMap[0])) and personXDelta > 0:
            camera.viewToScreenPxlOffsetX = (float(float(camera.displayWidth/float(tileWidth)) - int(camera.displayWidth/float(tileWidth))))*tileWidth
            camera.viewX = int(len(thisLevelMap[0]) + LEFrame.frameWidth - int(camera.displayWidth/float(tileWidth)))
            atWorldEdgeX = True
        else:
            if (camera.viewX + camera.viewToScreenPxlOffsetX/float(tileWidth) + (personXDelta/float(tileWidth)) <= -1 and personXDelta <0):
                camera.viewX = -1
                camera.viewToScreenPxlOffsetX = 0
                atWorldEdgeX = True
        
        if (camera.viewY + (camera.displayHeight/float(tileHeight)) + (personYDelta/float(tileHeight)) - (camera.viewToScreenPxlOffsetY/float(tileHeight)) + 1 >= len(thisLevelMap)) and personYDelta > 0:
            camera.viewToScreenPxlOffsetY = (float(float(camera.displayHeight/float(tileHeight)) - int(camera.displayHeight/float(tileHeight))))*tileHeight
            camera.viewY = int(len(thisLevelMap) - int(camera.displayHeight/float(tileHeight))) - 1
            atWorldEdgeY = True
        else:
            if (camera.viewY + camera.viewToScreenPxlOffsetY/float(tileHeight) + (personYDelta/float(tileHeight)) <= -1 and personYDelta < 0):
                camera.viewY = -1
                camera.viewToScreenPxlOffsetY = 0
                atWorldEdgeY = True
        return camera, atWorldEdgeX, atWorldEdgeY


    def diagSpeedFix(self, XDelta, YDelta, speed):
        #FIX DIAGONAL SPEED INCREASE
        #  
        #  |\                                                                 |\
        #  | \                                                                | \
        # 5|  \ >5  -> solve for X and Y, while keeping x:y the same ratio: Y |  \ 5
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

    def screenSynchWithCharacterMovement(self, yok, xok, personYDelta, personXDelta, camera, personYDeltaButScreenOffset, personXDeltaButScreenOffset, tileHeight, tileWidth, y, x, thisLevelMapWidth, thisLevelMapHeight, atWorldEdgeX, atWorldEdgeY):

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
        if xok == 1 and atWorldEdgeX == False: #and ((personXDelta < 0 and x + personXDelta < (1*camera.displayWidth)/3.0) or (personXDelta >0 and x + personXDelta > (2*camera.displayWidth)/3.0)):
            camera.viewToScreenPxlOffsetX = camera.viewToScreenPxlOffsetX - personXDelta #MOVE CAMERA ALONG X AXIS
            personXDeltaButScreenOffset = -personXDelta #KEEP PLAYER'S CHARACTER FIXED @ MIDDLE 9TH EDGE
        else:
            personXDeltaButScreenOffset = 0

        if yok == 1 and atWorldEdgeY == False: #and ((personYDelta < 0 and y + personYDelta < (1*camera.displayHeight)/3.0) or (personYDelta >0 and y + personYDelta > (2*camera.displayHeight)/3.0)):
            camera.viewToScreenPxlOffsetY = camera.viewToScreenPxlOffsetY - personYDelta #MOVE CAMERA ALONG Y AXIS
            personYDeltaButScreenOffset = -personYDelta #KEEP PLAYER'S CHARACTER FIXED @ MIDDLE 9TH EDGE
        else:
            personYDeltaButScreenOffset = 0

        #SCREEN MOVES IN PIXELS, BUT THE WORLD IS BUILT IN TILES.
        #WHEN SCREEN MOVES IN PIXELS WITH USER'S MOVEMENT, THIS
        #IS STORED IN cameraViewToScreenPxlOffsetX/Y. BUT IF USER'S
        #MOVEMENT (AND THEREFORE, cameraViewToScreenPxlOffsetX/Y) GOES BEYOND
        #THE SIZE OF A TILE, THEN TAKE AWAY THE TILE SIZE FROM THE 
        #cameraViewToScreenPxlOffsetX/Y, AND CONSIDER THAT THE USER HAS MOVED
        #1 TILE IN DISTANCE IN THE WORLD. THIS IS IMPORTANT IN
        #ACCURATELY TRACKING THE USER'S LOCATION COORDINATES HELD
        #IN playerX/YTile
        if camera.viewToScreenPxlOffsetX >= tileWidth:
            camera.viewToScreenPxlOffsetX = camera.viewToScreenPxlOffsetX - tileWidth
            camera.viewX = camera.viewX - 1
            
        elif camera.viewToScreenPxlOffsetX <0:
            camera.viewToScreenPxlOffsetX = camera.viewToScreenPxlOffsetX + tileWidth
            camera.viewX = camera.viewX + 1

        if camera.viewToScreenPxlOffsetY >= tileHeight:
            camera.viewToScreenPxlOffsetY = camera.viewToScreenPxlOffsetY - tileHeight
            camera.viewY = camera.viewY - 1

        elif camera.viewToScreenPxlOffsetY <0:
            camera.viewToScreenPxlOffsetY = camera.viewToScreenPxlOffsetY + tileHeight
            camera.viewY = camera.viewY + 1
            
        if xok == 1:
            x = x + personXDelta + personXDeltaButScreenOffset #MOVE USER'S CHARACTER, BUT DON'T MOVE HIM IN ONE DIRECTION IF THE SCREEN SCROLL IS ALSO MOVING IN THAT DIRECTION
            #mouseXTile = 1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + (x/float(tileWidth)) #0 BASED, JUST LIKE THE ARRAY, THIS IS LEFT MOST POINT OF USER'S CHAR
        if yok == 1:
            y = y + personYDelta + personYDeltaButScreenOffset #MOVE USER'S CHARACTER, BUT DON'T MOVE HIM IN ONE DIRECTION IF THE SCREEN SCROLL IS ALSO MOVING IN THAT DIRECTION
            #mouseYTile = 1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + (y/float(tileHeight)) #0 BASED, JUST LIKE THE ARRAY, THIS IS TOP MOST POINT OF USER'S CHAR
        return personYDelta, personXDelta, camera, personYDeltaButScreenOffset, personXDeltaButScreenOffset, y, x

    def generateparticles(self, shotsFiredFromMe, myParticles, personYFacing, personXFacing, mouseYTile, mouseXTile, tileHeight, tileWidth, DEFAULTBULLETSPEED, currentGun, gfx):
        if shotsFiredFromMe == True and not(personYFacing == 0 and personXFacing == 0):
            speed = DEFAULTBULLETSPEED #units are world tiles, not pixels!
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
                           #Name, weapon, world X Loc, world Y Loc,  dx,    dy, damage, bounces remaining, bullet width px, bullet height px, frame speed, default speed, image
            myParticles.append(["User Bullet", currentGun, mouseXTile, mouseYTile, tempDX, tempDY, 10, 1, 16, 16, speed, DEFAULTBULLETSPEED, img]) #putting multiple instances of the image itself in the array because they could be rotated at different directions and putting a pointer to one image and then rotating many many times severly impacts FPS due to slow rotate method
            shotsFiredFromMe = False
        return myParticles, shotsFiredFromMe

    def moveParticlesAndHandleParticleCollision(self, myParticles, thisLevelMap):
        #MOVE PARTICLES, OR DELETE THEM IF THEY REACH WORLD END
        myDeletedParticles = []
        for i in xrange(len(myParticles)):
            if myParticles[i][2] + myParticles[i][4] + 1 > len(thisLevelMap[0]) or myParticles[i][3] + myParticles[i][5] + 1 > len(thisLevelMap) or myParticles[i][2] + myParticles[i][4] < 0 or myParticles[i][3] + myParticles[i][5] < 0:
                myDeletedParticles.append(i)
            else:
                myParticles[i][2] = myParticles[i][2] + myParticles[i][4]
                myParticles[i][3] = myParticles[i][3] + myParticles[i][5]
        for i in xrange(len(myDeletedParticles)):
            del myParticles[myDeletedParticles[i]-i]

        #COLLISION DETECT IF WALL HIT, AND BOUNCE/PERFORM ACTION IF NECESSARY
            
        return myParticles

    def applyGravityToWorld(self, gravityYDelta, timeSpentFalling, tileHeight):
        return (min(gravityYDelta + (.00005 * (timeSpentFalling**2)), tileHeight / 3.0)), timeSpentFalling + 1

    def getNextGravityApplicationToWorld(self, gravityYDelta, timeSpentFalling, tileHeight):
        a, b = self.applyGravityToWorld(gravityYDelta, timeSpentFalling, tileHeight)
        return a

    def manageTimeAndFrameRate(self, lastTick, clock, FPSLimit):
        timeElapsedSinceLastFrame = clock.get_time() - lastTick
        lastTick = clock.tick(FPSLimit)
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

    def determineCharPicBasedOnDirectionFacing(self, myEnemies, personXFacing, personYFacing, personImgDirectionIndex):
        if personXFacing == 0 and personYFacing > 0:
            #down
            personImgDirectionIndex = 0
        if personXFacing == 0 and personYFacing < 0:
            #up
            personImgDirectionIndex = 1
        if personXFacing > 0 and personYFacing == 0:
            #right
            personImgDirectionIndex = 2
        if personXFacing < 0 and personYFacing == 0:
            #left
            personImgDirectionIndex = 3
        if personXFacing > 0 and personYFacing > 0:
            #down right
            personImgDirectionIndex = 4
        if personXFacing < 0 and personYFacing < 0:
            #up left
            personImgDirectionIndex = 5
        if personXFacing > 0 and personYFacing < 0:
            #up right
            personImgDirectionIndex = 6
        if personXFacing < 0 and personYFacing > 0:
            #down left
            personImgDirectionIndex = 7

        #for each enemy in myEnemies:
            #Determine this enemy's directionImgIndex
        
        return myEnemies, personImgDirectionIndex

    def determineCharPicBasedOnWalkOrMovement(self, myEnemies, millisecondsOnEachLeg, millisecondsOnThisLeg, millisecondsSinceLastFrame, numberOfFramesAnimPerWalk, personImgLegIndex, personXDelta, personYDelta):
        if personXDelta == 0 and personYDelta == 0:
            personImgLegIndex = 0
            millisecondsOnThisLeg = 0
        else:
            if (millisecondsOnThisLeg >= millisecondsOnEachLeg):
                personImgLegIndex = (personImgLegIndex + 1) % numberOfFramesAnimPerWalk
                millisecondsOnThisLeg = 0
            else:
                millisecondsOnThisLeg = millisecondsOnThisLeg + millisecondsSinceLastFrame

            #for each enemy in myEnemies:
                #Determine this enemy's legImgIndex
        
        return myEnemies, millisecondsOnThisLeg, personImgLegIndex

class menuScreen(object):
    def __init__(self, menuType, screenResSelection, difficultySelection, displayType, gameDisplay):
        self.gameDisplay = gameDisplay
        self.menuType = menuType
        self.screenResSelection = screenResSelection
        self.difficultySelection = difficultySelection
        self.displayType = displayType
        self.menuDirectory = "Main"
        self.menuJustOpened = True
        self.difficultyChoices = ["Easy", "Medium", "Hard", "Expert"]
        self.score = 0
        self.highScoreDifficulty = 0
        self.myHealth = 100
        self.currentLevel = 0
        self.menuSelectionIndex = 6
        self.ammo = 0
        self.displayWidth = screenResChoices[screenResSelection][0]
        self.displayHeight = screenResChoices[screenResSelection][1]
        if self.displayType == "Full Screen":
            self.gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight), pygame.FULLSCREEN)
        else:
            self.gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight))
        self.colorIntensity = 255
        self.colorIntensityDirection = 5
        self.startPlay = False
        self.gfx = gfxHandler()
        self.logic = logicHandler()
        self.exiting = False
        self.lost = False
        self.ammo = 0
        self.personXDelta = 0
        self.personYDelta = 0
        self.personSpeed = 1
        self.currentGun = ""
        self.shotsFiredFromMe = False
        self.personXFacing = 0
        self.personYFacing = 0
        self.screenMoveCounter = 0
        self.menuFPSLimit = 120
        self.clock = pygame.time.Clock()
        self.clock.tick()
        self.enterPressed = False
        self.personXDeltaWas = 0
        self.personYDeltaWas = 0
        self.userMouse = mouse()
        self.myHighScoreDatabase = highScoresDatabase()
        self.myHighScores = self.myHighScoreDatabase.loadHighScores()

    def updateScreenAndLimitFPS(self, FPSLimit):
        self.limit = FPSLimit
        pygame.display.update()
        self.clock.tick(FPSLimit)
        
    def displayMenuScreenAndHandleUserInput(self):
        while self.exiting == False and self.startPlay == False:
            self.displayTitle()
            self.selectionColorPulsate()
            self.handleMenuBackground()
            self.getKeyPress()
            if self.menuDirectory == "Main":
                self.displayMainMenu()
                if self.menuJustOpened == False:
                    self.handleUserInputMainMenu()
                self.menuJustOpened = False
            elif self.menuDirectory == "Settings":
                self.displaySettingsMenu()
                self.handleUserInputSettingsMenu()
            elif self.menuDirectory == "Credits":
                self.displayCreditsMenu()
                self.handleUserInputCreditsMenu()
            elif self.menuDirectory == "How To Play":
                self.displayHowToMenu()
                self.handleUserInputHowToMenu()
            elif self.menuDirectory == "High Scores":
                self.displayHighScoresMenu()
                self.handleUserInputHighScoresMenu()
                
            self.personYDeltaWas = self.personYDelta
            self.personXDeltaWas = self.personXDelta
            self.updateScreenAndLimitFPS(self.menuFPSLimit)
            self.gameDisplay.fill(black)
        del self.clock
        return self.difficultySelection, self.screenResSelection, self.displayType, self.exiting
    
    def displayTitle(self):
        gameTitle = "2d Game Framework"
        self.smallText = pygame.font.Font("freesansbold.ttf", 24)
        self.largeText = pygame.font.Font("freesansbold.ttf", 48)
        self.textSurf, self.textRect = self.gfx.textObjects(gameTitle, self.largeText, white)
        self.textRect.center = ((self.displayWidth/2.0), (self.screenMoveCounter + 25))
        self.gameDisplay.blit(self.textSurf, self.textRect)
        if self.menuType == "Paused":
            self.textSurf, self.textRect = self.gfx.textObjects("-Paused-", self.smallText, white)
            self.textRect.center = ((self.displayWidth/2.0), (self.screenMoveCounter + 60))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def selectionColorPulsate(self):
        if self.colorIntensity + self.colorIntensityDirection > 255:
            self.colorIntensityDirection = -5
        elif self.colorIntensity + self.colorIntensityDirection < 65:
            self.colorIntensityDirection = 5
        self.colorIntensity = self.colorIntensity + self.colorIntensityDirection

    def handleMenuBackground(self):
        pass
        #self.currentLevel, self.currentGun, self.enemiesAlive, self.myEnemies, self.myProjectiles = self.menuGameEventHandler.addGameObjects(
            #self.enemiesAlive, self.currentLevel, self.currentGun, self.myEnemies, self.starProbabilitySpace, self.starDensity, self.starMoveSpeed, self.myProjectiles, self.displayWidth)
        #self.starMoveSpeed = self.menuGameEventHandler.adjustStarMoveSpeed(self.maximumStarMoveSpeed, self.numberOfStarSpeeds)
        #self.myProjectiles, self.myEnemies, self.myHealth, self.score, self.enemiesAlive, self.y, self.ammo = self.menuGameEventHandler.moveAndDrawProjectilesAndEnemies(
            #self.myProjectiles, self.myEnemies, self.myHealth, self.score, self.enemiesAlive, self.x, self.y, self.rocketWidth, self.rocketHeight, self.difficultySelection, self.displayWidth, self.displayHeight, self.ammo, self.starMoveSpeed)
        #self.menuGameEventHandler.drawObject(myCharacter, self.x, self.y)

    def getKeyPress(self):
        self.exiting, self.lost, self.ammo, self.personXDelta, self.personYDelta, self.personSpeed, self.currentGun, self.shotsFiredFromMe, self.personXFacing, self.personYFacing, self.enterPressed, self.userMouse.coords, self.userMouse.btn = self.logic.keyPressAndGameEventHandler(self.exiting, self.lost, self.ammo, self.personXDelta, self.personYDelta, self.personSpeed, self.currentGun, self.shotsFiredFromMe, self.personXFacing, self.personYFacing)

    def displayMainMenu(self):
        self.mainMenuItemMargin = 25
        for self.i in xrange(7):
            self.rgb = (255, 255, 255)
            if self.i == self.menuSelectionIndex:
                self.rgb = (self.colorIntensity, 0, 0)
            if self.i == 6:
                if self.menuType == "Paused":
                    self.text = "Resume"
                else:
                    self.text = "Start Level Editor"
            if self.i == 5:
                self.text = "Difficulty: " + self.difficultyChoices[self.difficultySelection]
                if self.menuType == "Paused":
                    self.tempRGB = (self.rgb[0]*.25, self.rgb[1]*.25, self.rgb[2]*.25)
                    self.rgb = self.tempRGB
            if self.i == 4:
                self.text = "High Scores"
            if self.i == 3:
                self.text = "How To Play"
            if self.i == 2:
                self.text = "Settings"
            if self.i == 1:
                self.text = "Credits"
            if self.i == 0:
                self.text = "Quit"
            self.textSurf, self.textRect = self.gfx.textObjects(self.text, self.smallText, self.rgb)
            self.textRect.center = ((self.displayWidth/2.0), (self.displayHeight/2.0 - self.i*(self.mainMenuItemMargin) + self.screenMoveCounter))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def displaySettingsMenu(self):
        self.fullScreenWindowChanged = False
        for self.i in xrange(5):
            self.rgb = (255, 255, 255)
            if self.i == 4:
                self.text = "Screen Size: " + str(screenResChoices[self.screenResSelection][0]) + "x" + str(screenResChoices[self.screenResSelection][1])
            if self.i == 3:
                self.text = "Screen: " + self.displayType
            if self.i == 2:
                self.text = "Music Volume: 100"
            if self.i == 1:
                self.text = "SFX Volume: 100"
            if self.i == 0:
                self.text = "Go Back"
            if self.i == self.menuSelectionIndex:
                self.rgb = (self.colorIntensity, 0, 0)
            self.textSurf, self.textRect = self.gfx.textObjects(self.text, self.smallText, self.rgb)
            self.textRect.center = ((self.displayWidth/2.0), (self.displayHeight/2.0 - self.i*(self.mainMenuItemMargin)))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def displayCreditsMenu(self):
        creditsMoveSpeed = 5
        if self.screenMoveCounter < self.displayHeight:
            self.screenMoveCounter = self.screenMoveCounter + creditsMoveSpeed
            self.displayTitle()
            self.displayMainMenu()
    
        for self.i in xrange(3):
            self.rgb = (255, 255, 255)
            if self.i == 2:
                self.text = "Programming by Mike Finnegan"
            if self.i == 1:
                self.text = "Art by Mike Finnegan"
            if self.i == 0:
                self.text = "Music/SFX by Mike Finnegan"
            self.textSurf, self.textRect = self.gfx.textObjects(self.text, self.smallText, self.rgb)
            #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.personSpeed)))
            self.textRect.center = ((self.displayWidth/2.0), ((self.i * self.mainMenuItemMargin) + self.screenMoveCounter - self.displayHeight/2.0))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def displayHowToMenu(self):
        howToSpeed = 5
        if self.screenMoveCounter < self.displayHeight:
            self.screenMoveCounter = self.screenMoveCounter + howToSpeed
            self.displayTitle()
            self.displayMainMenu()
        for self.i in xrange(3):
            self.rgb = (255, 255, 255)
            if self.i == 2:
                self.text = "Escape key: pause game"
            if self.i == 1:
                self.text = "Space bar: shoot aliens"
            if self.i == 0:
                self.text = "Arrow keys Up, Down, Left, Right: fly spacecraft"
            self.textSurf, self.textRect = self.gfx.textObjects(self.text, self.smallText, self.rgb)
            #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.personSpeed)))
            self.textRect.center = ((self.displayWidth/2.0), ((self.i * self.mainMenuItemMargin) + self.screenMoveCounter - self.displayHeight/2.0))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def displayHighScoresMenu(self):
        if self.menuSelectionIndex == 0:
            self.rgb = (self.colorIntensity, 0, 0)
        else:
            self.rgb = (255, 255, 255)
        if self.highScoreDifficulty == 0:
            self.textSurf, self.textRect = self.gfx.textObjects("<<  Easy High Scores  >>", self.smallText, self.rgb)
        if self.highScoreDifficulty == 1:
            self.textSurf, self.textRect = self.gfx.textObjects("<<  Medium High Scores  >>", self.smallText, self.rgb)
        if self.highScoreDifficulty == 2:
            self.textSurf, self.textRect = self.gfx.textObjects("<<  Hard High Scores  >>", self.smallText, self.rgb)
        if self.highScoreDifficulty == 3:
            self.textSurf, self.textRect = self.gfx.textObjects("<<  Expert High Scores  >>", self.smallText, self.rgb)
        self.textRect.center = ((self.displayWidth/2.0), (self.screenMoveCounter + 90))
        self.gameDisplay.blit(self.textSurf, self.textRect)
        for self.i in xrange(-1, 11):
            for self.j in xrange(5):
                if self.i == -1:
                    self.rgb = (255, 255, 255)
                    if self.j == 0:
                        self.text = "Rank"
                    elif self.j == 1:
                        self.text = "Name"
                    elif self.j == 2:
                        self.text = "Score"
                    elif self.j == 3:
                        self.text = "State"
                    elif self.j == 4:
                        self.text = "Country"
                    self.textSurf, self.textRect = self.gfx.textObjects(self.text, self.smallText, self.rgb)
                    #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.personSpeed)))
                    self.textRect.center = ((self.displayWidth*((self.j+1)/6.0)), ((self.i * self.mainMenuItemMargin) + self.displayHeight/2.0))
                elif self.i == self.myHighScoreDatabase.numberOfRecordsPerDifficulty:
                    if self.menuSelectionIndex == 1:
                        self.rgb = (self.colorIntensity, 0, 0)
                    else:
                        self.rgb = (255, 255, 255)
                    self.text = "Go Back"
                    self.textSurf, self.textRect = self.gfx.textObjects(self.text, self.smallText, self.rgb)
                    self.textRect.center = ((self.displayWidth*.8), (self.displayHeight * .95))
                else:
                    self.rgb = (255, 255, 255)
                    self.text = str(self.myHighScores[self.highScoreDifficulty][self.i][self.j])
                    self.textSurf, self.textRect = self.gfx.textObjects(self.text, self.smallText, self.rgb)
                    #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.personSpeed)))
                    self.textRect.center = ((self.displayWidth*((self.j+1)/6.0)), ((self.i * self.mainMenuItemMargin) + self.displayHeight/2.0))
                self.gameDisplay.blit(self.textSurf, self.textRect)

    def handleUserInputMainMenu(self):
        if self.personYDelta == self.personSpeed and self.personYDeltaWas == 0 and self.menuSelectionIndex >0:
            self.menuSelectionIndex = self.menuSelectionIndex - 1
            if self.menuSelectionIndex == 5 and self.menuType == "Paused":
                self.menuSelectionIndex = self.menuSelectionIndex - 1
        if self.personYDelta == -self.personSpeed and self.personYDeltaWas == 0 and self.menuSelectionIndex < 6:
            self.menuSelectionIndex = self.menuSelectionIndex + 1
            if self.menuSelectionIndex == 5 and self.menuType == "Paused":
                self.menuSelectionIndex = self.menuSelectionIndex + 1    
        if ((self.personXDelta == self.personSpeed and self.personXDeltaWas == 0) or (self.enterPressed == True)) and self.menuSelectionIndex == 5:
            self.difficultySelection = (self.difficultySelection + 1) %len(self.difficultyChoices)
        if (self.personXDelta == -self.personSpeed and self.personXDeltaWas == 0) and self.menuSelectionIndex == 5:
            self.difficultySelection = (self.difficultySelection - 1) %len(self.difficultyChoices)
        if self.enterPressed == True and self.menuSelectionIndex == 1:
            self.menuDirectory = "Credits"
        if self.enterPressed == True and self.menuSelectionIndex == 3:
            self.menuDirectory = "How To Play"
        if self.enterPressed == True and self.menuSelectionIndex == 6:
            self.startPlay = True
            del self.myHighScoreDatabase
        if self.enterPressed == True and self.menuSelectionIndex == 0:
            self.exiting = True
        if self.enterPressed == True and self.menuSelectionIndex == 4:
            self.menuDirectory = "High Scores"
            self.menuSelectionIndex = 0
        if self.enterPressed == True and self.menuSelectionIndex == 2:
            self.menuDirectory = "Settings"
            self.menuSelectionIndex = 4

    def handleUserInputSettingsMenu(self):
        if self.personYDelta == self.personSpeed and self.personYDeltaWas == 0 and self.menuSelectionIndex >0:
            self.menuSelectionIndex = self.menuSelectionIndex - 1
        if self.personYDelta == -self.personSpeed and self.personYDeltaWas == 0 and self.menuSelectionIndex < 4:
            self.menuSelectionIndex = self.menuSelectionIndex + 1
        if ((self.personXDelta == self.personSpeed and self.personXDeltaWas == 0) or (self.enterPressed == True)) and self.menuSelectionIndex == 4:
            self.screenResSelection = (self.screenResSelection + 1) %len(screenResChoices)
        if (self.personXDelta == -self.personSpeed and self.personXDeltaWas == 0) and self.menuSelectionIndex == 4:
            self.screenResSelection = (self.screenResSelection - 1) %len(screenResChoices)
        if (self.enterPressed == True or (abs(self.personXDelta) == self.personSpeed and self.personXDeltaWas == 0))and self.menuSelectionIndex == 3:
            if self.displayType == "Window":
                self.displayType = "Full Screen"
            else:
                self.displayType = "Window"
            self.fullScreenWindowChanged = True
        if ((((self.personXDelta == self.personSpeed and self.personXDeltaWas == 0) or (self.enterPressed == True)) and self.menuSelectionIndex == 4) or ((self.personXDelta == -self.personSpeed and self.personXDeltaWas == 0) and self.menuSelectionIndex == 4)) or self.fullScreenWindowChanged == True:
            self.displayWidth = screenResChoices[self.screenResSelection][0]
            self.displayHeight = screenResChoices[self.screenResSelection][1]
            if self.displayType == "Window":
                gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight))
            else:
                gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight), pygame.FULLSCREEN)
            self.myProjectiles = []
            #self.x = (self.displayWidth/2.0)-(self.rocketWidth/2.0)
            #self.y = (self.displayHeight-self.rocketHeight)
            self.fullScreenWindowChanged = False
        if self.enterPressed == True and self.menuSelectionIndex == 0:
            self.menuDirectory = "Main"
            self.menuSelectionIndex = 2

    def handleUserInputCreditsMenu(self):
        if self.enterPressed == True:
            self.screenMoveCounter = 0
            self.menuDirectory = "Main"

    def handleUserInputHowToMenu(self):
        if self.enterPressed == True:
            self.screenMoveCounter = 0
            self.menuDirectory = "Main"

    def handleUserInputHighScoresMenu(self):
        if (self.personYDelta == self.personSpeed and self.personYDeltaWas == 0):
            self.menuSelectionIndex = (self.menuSelectionIndex + 1) % 2
        if (self.personYDelta == -self.personSpeed and self.personYDeltaWas == 0):
            self.menuSelectionIndex = (self.menuSelectionIndex - 1) % 2
        if (self.menuSelectionIndex == 0 and self.personXDelta == self.personSpeed and self.personXDeltaWas == 0):
            self.highScoreDifficulty = (self.highScoreDifficulty + 1) % len(self.difficultyChoices)
        if (self.menuSelectionIndex == 0 and self.personXDelta == -self.personSpeed and self.personXDeltaWas == 0):
            self.highScoreDifficulty = (self.highScoreDifficulty - 1) % len(self.difficultyChoices)
        if self.menuSelectionIndex == 1 and self.enterPressed == True:
            self.screenMoveCounter = 0
            self.menuDirectory = "Main"
            self.menuSelectionIndex = 4

class highScoresDatabase(object):
    def __init__(self):
        self.numberOfRecordsPerDifficulty = 10
        
    def fillInBlankHighScores(self, highScoresArray):
        self.workingArray = highScoresArray
        self.iNeedThisManyMoreBlankSlots = self.numberOfRecordsPerDifficulty - len(self.workingArray)
        self.n = 0
        self.b = [[],]
        for self.row in xrange(self.iNeedThisManyMoreBlankSlots):
            self.n = self.n + 1
            self.b.append([self.n, "-", 0, "-", "-"])
        self.b.remove([])
        #self.workingArray.append(self.b)
        #return self.workingArray
        return self.b

    def loadHighScores(self):
        try:
            self.highScoresArray = [[],]
            self.connection = sqlite3.connect("High_Scores.db")
            self.c = self.connection.cursor()
            self.row = ([])
            for self.loadCounter in xrange(5):
                self.a = [[],]
                if self.loadCounter == 0:
                    self.c.execute("""SELECT * FROM easyHighScoreTable ORDER BY scoreRecordPK""")
                elif self.loadCounter == 1:
                    self.c.execute("""SELECT * FROM mediumHighScoreTable ORDER BY scoreRecordPK""")
                elif self.loadCounter == 2:
                    self.c.execute("""SELECT * FROM hardHighScoreTable ORDER BY scoreRecordPK""")
                elif self.loadCounter == 3:
                    self.c.execute("""SELECT * FROM expertHighScoreTable ORDER BY scoreRecordPK""")
                for self.row in self.c.fetchall():
                    self.a.append([self.row[0], str(self.row[1]), self.row[2], str(self.row[3]), str(self.row[4])])
                #self.highScoresArray.append([row(0), row(1), row(2), row(3), row(4)])
                self.a.remove([])
                #self.a = self.a.append(self.fillInBlankHighScores(self.a))
                #self.a.remove([])
                #print self.a
                self.highScoresArray.insert(self.loadCounter, self.a)
        except:
            self.initializeDatabase()
        
        self.connection.close()
        return self.highScoresArray

    def initializeDatabase(self):
        self.connection = sqlite3.connect("High_Scores.db")
        self.c = self.connection.cursor()
        self.c.execute("DROP TABLE IF EXISTS easyHighScoreTable")
        self.c.execute("CREATE TABLE easyHighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")
        self.c.execute("DROP TABLE IF EXISTS mediumHighScoreTable")
        self.c.execute("CREATE TABLE mediumHighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")
        self.c.execute("DROP TABLE IF EXISTS hardHighScoreTable")
        self.c.execute("CREATE TABLE hardHighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")
        self.c.execute("DROP TABLE IF EXISTS expertHighScoreTable")
        self.c.execute("CREATE TABLE expertHighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")
        for self.loadCounter in xrange(5):
            #self.highScoresArray.append([])
            self.highScoresArray.insert(self.loadCounter, self.fillInBlankHighScores(self.highScoresArray[self.loadCounter]))
            #self.highScoresArray = self.fillInBlankHighScores(self.highScoresArray[self.loadCounter])
        self.highScoresArray.remove([])
        for self.loadCounter in xrange(5):
            self.updateHighScoresForThisDifficulty(self.highScoresArray[self.loadCounter], self.loadCounter)
        self.connection.close()
        return self.highScoresArray
                
    def updateHighScoresForThisDifficulty(self, workingArray, difficulty):
        try:
            self.workingArray = workingArray
            self.difficulty = difficulty
            self.connection = sqlite3.connect("High_Scores.db")
            self.c = self.connection.cursor()
            self.updateCounter = -1
            for self.row in self.workingArray:
                self.updateCounter = self.updateCounter + 1
                if self.difficulty == 0:
                    if self.updateCounter == 0:
                        self.c.execute("DROP TABLE IF EXISTS easyHighScoreTable")
                        self.c.execute("CREATE TABLE easyHighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")
                    self.c.execute("INSERT INTO easyHighScoreTable Values(?, ?, ?, ?, ?)", tuple((int(workingArray[self.updateCounter][0]), self.workingArray[self.updateCounter][1], int(self.workingArray[self.updateCounter][2]), self.workingArray[self.updateCounter][3], self.workingArray[self.updateCounter][4])))
                if self.difficulty == 1:
                    if self.updateCounter == 0:
                        self.c.execute("DROP TABLE IF EXISTS mediumHighScoreTable")
                        self.c.execute("CREATE TABLE mediumHighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")
                    self.c.execute("INSERT INTO mediumHighScoreTable Values(?, ?, ?, ?, ?)", tuple((int(workingArray[self.updateCounter][0]), self.workingArray[self.updateCounter][1], int(self.workingArray[self.updateCounter][2]), self.workingArray[self.updateCounter][3], self.workingArray[self.updateCounter][4])))
                if self.difficulty == 2:
                    if self.updateCounter == 0:
                        self.c.execute("DROP TABLE IF EXISTS hardHighScoreTable")
                        self.c.execute("CREATE TABLE hardHighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")
                    self.c.execute("INSERT INTO hardHighScoreTable Values(?, ?, ?, ?, ?)", tuple((int(workingArray[self.updateCounter][0]), self.workingArray[self.updateCounter][1], int(self.workingArray[self.updateCounter][2]), self.workingArray[self.updateCounter][3], self.workingArray[self.updateCounter][4])))
                if self.difficulty == 3:
                    if self.updateCounter == 0:
                        self.c.execute("DROP TABLE IF EXISTS expertHighScoreTable")
                        self.c.execute("CREATE TABLE expertHighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")
                    self.c.execute("INSERT INTO expertHighScoreTable Values(?, ?, ?, ?, ?)", tuple((int(workingArray[self.updateCounter][0]), self.workingArray[self.updateCounter][1], int(self.workingArray[self.updateCounter][2]), self.workingArray[self.updateCounter][3], self.workingArray[self.updateCounter][4])))                
                self.connection.commit()
        except:
            self.initializeDatabase()
        self.connection.close()
        
class gameplayObject(object):
    pass

class characterObject(gameplayObject):
    pass


class particleObject(gameplayObject):
    #Name, weapon, world X Loc, world Y Loc,  dx,    dy, damage, physics actions remaining, particle width px, particle height px, frame speed, default speed, image, particlePhysicsLevel
    #if particlePhysicsLevel >= wallPhysicsLevel + 3 then particle pushes the wall
    #if particlePhysicsLevel = wallPhysicsLevel + 2 then particle goes through wall
    #if particlePhysicsLevel = wallPhysicsLevel + 1 then particle bounces off wall
    #if particlePhysicsLevel <= wallPhysicsLevel then particle absorbs into wall

    #physics actions represent the number of remaining times the particle can push/go through/bounce off walls
    pass

class worldObject(gameplayObject):
    pass


class mouse(object):
    def __init__(self):
        self.coords = (0,0)
        self.btn = (0,0,0)
        self.xTile = 0
        self.yTile = 0

class camera(object):
    def __init__(self, screenResSelection, displayType):
        self.screenResSelection = screenResSelection
        self.displayType = displayType
        self.viewX = 14 #Camera view X-coord measured in tiles
        self.viewY = 14 #Camera view Y-coord measured in tiles
        self.viewToScreenPxlOffsetX = 0 #Offset the camera view X-coord to the screen based on player fractional tile movement, in pixels
        self.viewToScreenPxlOffsetY = 0 #Offset the camera view Y-coord to the screen based on player fractional tile movement, in pixels
        self.zoom = 1

    def updateScreenSettings(self):
        self.displayWidth = screenResChoices[self.screenResSelection][0]
        self.displayHeight = screenResChoices[self.screenResSelection][1]
        #self.displayWidth = displayWidth #1280 #960
        #self.displayHeight = displayHeight #720 #54
        if self.displayType == "Full Screen":
            gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight), pygame.FULLSCREEN)
        else:
            gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight))
        return gameDisplay
        #TODO: Resolution/screen size change can put character outside of camera view
        #TODO: Resolution/screen size change can put camera view outside of world
    

class game(object):
    def __init__(self, screenResSelection, fullScreen):        
        self.clock = pygame.time.Clock()
        self.camera = camera(screenResSelection, fullScreen)
        self.gameDisplay = self.camera.updateScreenSettings()
        self.displayFrame = levelEditorFrame()
        self.userMouse = mouse()
        self.logic = logicHandler()
        self.gfx = gfxHandler()
        
        
        pygame.display.set_caption("2D Game Framework - Level Editor")
        
        self.lastTick = 0
        self.timeElapsedSinceLastFrame = 0

        self.exiting = False
        self.paused = False
        self.lost = False
        self.difficultySelection = 0
        self.enterPressed = False

        self.DEFAULTBULLETSPEED = .01 #BULLET SPEED IN WORLD TILES/MILLISECOND

        self.tileSheetRows = 10
        self.tileSheetColumns = 1
        self.tileWidth = 64 * self.camera.zoom
        self.tileHeight = 64 * self.camera.zoom
        self.tileXPadding = 0
        self.tileYPadding = 0
        self.enemiesAlive = 0
        self.currentLevel = 0
        self.myParticles = [] #[NAME, X1, Y1, DX, DY, R, G, B, SPEED, 0]
        self.myEnemies = [] #[species, weapon, health, aggression, speed, img, x, y, dx, dy, width, height]
        self.gravityAppliesToWorld = False #CHOOSE TRUE FOR SLIDE-SCROLLER TYPE GAME, OR FALSE FOR RPG TYPE GAME!

        
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
        self.thisLevelMapHeight = len(self.thisLevelMap)
        self.thisLevelMapWidth = len(self.thisLevelMap[0])

        
               
        self.personImgDirectionIndex = 0
        self.personImgLegIndex = 0
        self.millisecondsOnEachLeg = 250
        self.millisecondsOnThisLeg = 0
        self.timeSpentFalling = 0 #This is important to track because falling velocity due to gravity is non-linear
        self.personXDelta = 0
        self.personYDelta = 0
        self.gravityYDelta = 0
        self.personXFacing = 0
        self.personYFacing = 0
        self.userMouse.xTile = 0 #Mouse world X-coord in tiles
        self.userMouse.yTile = 0 #Mouse world Y-coord in tiles
        self.x = (((self.camera.displayWidth/float(self.tileWidth))/2)*self.tileWidth) #Player screen X-coord in pixels
        self.y = (((self.camera.displayHeight/float(self.tileHeight))/2)*self.tileHeight) #Player screen Y-coord in pixels
        self.xok = 1
        self.yok = 1
        self.personXDeltaButScreenOffset = 0 #Offsets character screen velocity when camera moves with character
        self.personYDeltaButScreenOffset = 0 #Offsets character screen velocity when camera moves with character
        self.mouseWidth = self.tileWidth #IN PIXELS
        self.personHeight = self.tileHeight #IN PIXELS
        self.DEFAULTPERSONSPEED = 1 #PLAYER SPEED IN PIXELS/MILLISECOND
        self.personSpeed = 0 #ACTUAL PLAYER MOVEMENT BASED ON COMPUTER'S FRAME RATE
        self.numberOfFramesAnimPerWalk = 1
        self.ammo = 50000
        self.currentGun = 1
        self.myHealth = 100
        self.score = 0
        self.shotsFiredFromMe = False

        self.gfx.loadGfxDictionary("spritesheet.png", "World Tiles", self.tileSheetRows, self.tileSheetColumns, self.tileWidth, self.tileHeight, self.tileXPadding, self.tileYPadding)
        self.gfx.loadGfxDictionary("characters.png", "Characters", 8, self.numberOfFramesAnimPerWalk, self.mouseWidth, self.personHeight, 0, 0)
        self.gfx.loadGfxDictionary("level editor frame.png", "Level Editor Frame", 2, 4, self.mouseWidth, self.personHeight, 0, 0)
        self.gfx.loadGfxDictionary("bullets.png", "Particles", 4, 1, 16, 16, 0, 0)
        
        self.FPSLimit = 30
    def showMenu(self, displayMenu, camera):
        
        myMenuSystem = menuScreen(displayMenu, self.camera.screenResSelection , self.difficultySelection, self.camera.displayType, self.gameDisplay)
        self.difficultySelection, self.camera.screenResSelection, self.camera.displayType, self.exiting = myMenuSystem.displayMenuScreenAndHandleUserInput()
        self.paused = False
        del myMenuSystem
        self.camera.updateScreenSettings()

    def play(self):
        # GAME LOOP
        while not self.paused:
            #FIGURE OUT HOW MUCH TIME HAS ELAPSED SINCE LAST FRAME WAS DRAWN
            self.timeElapsedSinceLastFrame = self.logic.manageTimeAndFrameRate(self.lastTick, self.clock, self.FPSLimit)
            
            #HANDLE KEY PRESSES AND PYGAME EVENTS
            self.paused, self.lost, self.ammo, self.personXDelta, self.personYDelta, self.personSpeed, self.currentGun, self.shotsFiredFromMe, self.personXFacing, self.personYFacing, self.enterPressed, self.userMouse.coords, self.userMouse.btn = self.logic.keyPressAndGameEventHandler(self.paused, self.lost, self.ammo, self.personXDelta, self.personYDelta, self.personSpeed, self.currentGun, self.shotsFiredFromMe, self.personXFacing, self.personYFacing)

            #NOW THAT KEY PRESSES HAVE BEEN HANDLED, ADJUST THE SPEED OF EVERYTHING BASED ON HOW MUCH TIME ELAPSED SINCE LAST FRAME DRAW, AND PREVENT DIAGONAL SPEED UP ISSUE
            self.personSpeed, self.myParticles, self.personXDelta, self.personYDelta = self.logic.alterAllSpeeds(self.timeElapsedSinceLastFrame, self.myParticles, self.DEFAULTPERSONSPEED, self.personXDelta, self.personYDelta)
            #Select the correct image for all characters based on direction facing
            self.myEnemies, self.personImgDirectionIndex = self.logic.determineCharPicBasedOnDirectionFacing(self.myEnemies, self.personXFacing, self.personYFacing, self.personImgDirectionIndex)
            #Select the correct image for all characters based on what leg they are standing on
            self.myEnemies, self.millisecondsOnThisLeg, self.personImgLegIndex = self.logic.determineCharPicBasedOnWalkOrMovement(self.myEnemies, self.millisecondsOnEachLeg, self.millisecondsOnThisLeg, self.timeElapsedSinceLastFrame, self.numberOfFramesAnimPerWalk, self.personImgLegIndex, self.personXDelta, self.personYDelta)

            self.camera, self.atWorldEdgeX, self.atWorldEdgeY = self.logic.cameraWorldEdgeCollisionCheck(self.thisLevelMap, self.camera, self.personXDelta, self.personYDelta, self.tileWidth, self.tileHeight, self.displayFrame)
            #MOVE CHARACTERS & CHECK FOR CHARACTER-WALL COLLISIONS
            #self.yok, self.xok, self.camera, personXDelta, personYDelta = self.logic.characterWorldEdgeCollisionCheck(self.thisLevelMap, self.camera, self.userMouse.xTile, self.userMouse.yTile, self.personXDelta, self.personYDelta, self.tileWidth, self.tileHeight, self.x, self.y, self.displayFrame)
            #self.personXDelta, self.personYDelta = self.logic.diagSpeedFix(self.personXDelta, self.personYDelta, self.personSpeed)
            
            #TODO: generateBadGuys()
            #TODO: badGuysMoveOrAttack()
            
            #SYNCH SCREEN WITH CHARACTER MOVEMENT
            self.personYDelta, self.personXDelta, self.camera, self.personYDeltaButScreenOffset, self.personXDeltaButScreenOffset, self.y, self.x = self.logic.screenSynchWithCharacterMovement(self.yok, self.xok, self.personYDelta, self.personXDelta, self.camera, self.personYDeltaButScreenOffset, self.personXDeltaButScreenOffset, self.tileHeight, self.tileWidth, self.y, self.x, self.thisLevelMapWidth, self.thisLevelMapHeight, self.atWorldEdgeX, self.atWorldEdgeY)
            if self.gravityAppliesToWorld == True:
                self.gravityYDelta, self.timeSpentFalling = self.logic.applyGravityToWorld(self.gravityYDelta, self.timeSpentFalling, self.tileHeight)

            #MOVE PARTICLES
            #self.myParticles = self.logic.moveParticlesAndHandleParticleCollision(self.myParticles, self.thisLevelMap)
            #GENERATE PARTICLES
            #self.myParticles, self.shotsFiredFromMe = self.logic.generateparticles(self.shotsFiredFromMe, self.myParticles, self.personYFacing, self.personXFacing, self.userMouse.yTile, self.userMouse.xTile, self.tileHeight, self.tileWidth, self.DEFAULTBULLETSPEED, self.currentGun, self.gfx)# (self.bullets, rain drops, snowflakes, etc...)
            #DRAW THE WORLD IN TILES BASED ON THE THE NUMBERS IN THE thisLevelMap ARRAY
            self.gfx.drawWorldInCameraView(self.camera, self.tileWidth, self.tileHeight, self.thisLevelMap, self.gameDisplay, self.displayFrame)
            #DRAW THE LEVEL EDITOR FRAME AND FRAME OBJECTS
            self.displayFrame.drawLevelEditorFrame(self.camera, self.tileWidth, self.tileHeight, self.thisLevelMap, self.gfx, self.gameDisplay)
            self.displayFrame.drawTileAndObjectPalette(self.camera, self.tileWidth, self.tileHeight, self.gfx, self.gameDisplay)
            #DRAW PEOPLE, ENEMIES, OBJECTS AND PARTICLES
            self.gfx.drawObjectsAndParticles(self.myParticles, self.gameDisplay, self.camera, self.tileHeight, self.tileWidth, self.y, self.x)
            #CONVERT MOUSE COORDS -> WORLD TILES
            self.userMouse.xTile, self.userMouse.yTile = self.gfx.convertScreenCoordsToTileCoords(self.userMouse.coords, self.camera, self.tileWidth, self.tileHeight)

            self.displayFrame, self.thisLevelMap = self.logic.mouseEventHandler(self.userMouse, self.camera, self.displayFrame, self.tileWidth, self.tileHeight, self.thisLevelMap)
            #DRAW GAME STATS
            #self.gfx.smallMessageDisplay("Health: " + str(self.myHealth), 0, self.gameDisplay, white, self.displayWidth)
            #self.gfx.smallMessageDisplay("Ammo: " + str(self.ammo), 1, self.gameDisplay, white, self.displayWidth)
            #self.gfx.smallMessageDisplay("Level: " + str(self.currentLevel), 2, self.gameDisplay, white, self.displayWidth)
            #self.gfx.smallMessageDisplay("Score: " + str(self.score), 3, self.gameDisplay, white, self.displayWidth)
            self.gfx.smallMessageDisplay("Mouse X: " + str(self.userMouse.xTile), 4, self.gameDisplay, white, self.camera.displayWidth)
            self.gfx.smallMessageDisplay("Mouse Y: " + str(self.userMouse.yTile), 5, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.smallMessageDisplay("View X: " + str(self.camera.viewX), 7, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.smallMessageDisplay("View Y: " + str(self.camera.viewY), 8, self.gameDisplay, white, self.camera.displayWidth)
            self.gfx.smallMessageDisplay("FPS: " + str(1000/max(1, self.timeElapsedSinceLastFrame)), 9, self.gameDisplay, white, self.camera.displayWidth)
            pygame.display.update()
            if self.myHealth <= 0:
                self.lost = True
                #self.exiting = True
                self.gfx.largeMessageDisplay("YOU LOSE", self.gameDisplay, white)
                self.gameDisplay.fill(black)
                self.gfx.largeMessageDisplay(str(self.score) + " pts", self.gameDisplay, white)

            
        #OUT OF THE GAME LOOP
        if self.lost == True:
            #LOST GAME ACTION HERE
            pass
        else:
            pass
            #del self.clock


pygame.init()
allResolutionsAvail = pygame.display.list_modes()
#ADD IN GAME-SPECIFIC LOGIC IF CERTAIN RESOLUTIONS ARE TO BE EXCLUDED FROM USER SELECTION
screenResChoices = allResolutionsAvail
del allResolutionsAvail
screenResChoices.sort()
#PLAYER = pygame.image.load("person.png")
exiting = False
while exiting == False:
    myGame = game(int(len(screenResChoices)/2), "Window")
    exiting = myGame.showMenu("Main Menu", myGame.camera)
    while myGame.exiting == False and myGame.lost == False:
        myGame.play()
        myGame.showMenu("Paused", myGame.camera)
        #myMenuSystem = menuScreen("Main Menu", screenResSelection, difficultySelection, displayType)
        #del myMenuSystem
    del myGame
pygame.quit()
quit()
