import pygame
import time
import random
import sys,os
import math
import sqlite3
import wx

#Python 2.7
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
PI = math.pi


class GfxHandler(object):
    def __init__(self):
        self.gfxDictionary = {}

    def LoadGfxDictionary(self, file_name="", imageIndicator="", rows=0, columns=0, width=0, height=0, pictureXPadding=0, pictureYPadding=0):
        self.spriteSheet = pygame.image.load(file_name)
        imgTransparency = True
        
        if imageIndicator == "World Tiles":
            imgTransparency = False
        self.gfxDictionary.update({imageIndicator:{}}) #NESTED HASHTABLE

        for j in xrange(rows):
            for k in xrange(columns):
                #self.gfxDictionary[(j*k) + j] = self.GetImage(self.GetCoords((j*k) + j, width, height, pictureXPadding, pictureYPadding, rows, columns))
                self.gfxDictionary[imageIndicator].update({(j*columns) + k:self.GetImage(self.GetCoords((j*columns) + k, width, height, pictureXPadding, pictureYPadding, rows, columns), imgTransparency)})

    def GetImage(self, Coords, requiresTransparency):
        image = pygame.Surface([Coords[2], Coords[3]])
        image.blit(self.spriteSheet, (0,0), Coords)
        if requiresTransparency == True:
            image.set_colorkey((0,0,0))
        return image

    def GetCoords(self, tileRequested, tileWidth, tileHeight, pictureXPadding, pictureYPadding, gfxHandlerRows, gfxHandlerColumns):
        #print int((tileRequested%gfxHandlerColumns)*tileWidth)+(int(tileRequested%gfxHandlerColumns))*pictureXPadding
        #a = raw_input("")
        return (int((tileRequested%gfxHandlerColumns)*tileWidth)+(int(tileRequested%gfxHandlerColumns))*pictureXPadding,
                int((tileRequested/gfxHandlerColumns)*tileHeight)+(int(tileRequested/gfxHandlerColumns))*pictureYPadding,
                tileWidth,
                tileHeight)

    def CreateTextObjects(self, text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def DrawLargeMessage(self, text, myGameDisplay, myColor):
        largeText = pygame.font.Font("freesansbold.ttf", 135)
        textSurf, textRect = self.CreateTextObjects(text, largeText, myColor)
        textRect.center = ((displayWidth/2), (displayHeight/2))
        myGameDisplay.blit(textSurf, textRect)
        pygame.display.update()
        time.sleep(2)

    def DrawSmallMessage(self, text, lineNumber, myGameDisplay, myColor, displayWidth):
        smallText = pygame.font.Font("freesansbold.ttf", 16)
        textSurf, textRect = self.CreateTextObjects(text, smallText, myColor)
        textRect.center = ((displayWidth-60), 15 + (15*lineNumber))
        myGameDisplay.blit(textSurf, textRect)

    def DrawImg(self, myImage, myCoords, myGameDisplay):
        #pygame.draw.rect(myImage, grayConst, myCoords)
         myGameDisplay.blit(myImage, (myCoords[0], myCoords[1]))

    def DrawDialogs(self, conversationArray, (backR, backG, backB, backA), (foreR, foreG, foreB, foreA), (borderR, borderG, borderB, borderA), borderSize = 5):
        conversationSelections = []
        return conversationSelections
    
    def DrawObjectsAndParticles(self, particles, gameDisplay, camera, tileHeight, tileWidth, character):
        self.DrawImg(self.gfxDictionary[character.imagesGFXNameDesc][character.imgDirectionIndex+(character.numberOfDirectionsFacingToDisplay*character.imgLegIndex)], (character.x, character.y), gameDisplay)
        for i in xrange(len(particles)):
            if particles[i].name == "User Bullet":
                #print "x: " + str((1 + cameraViewX + (-cameraViewToScreenPxlOffsetX/float(tileWidth)) - particles[i][2]) * -tileWidth)
                #print "y: " + str((1 + cameraViewY + (-cameraViewToScreenPxlOffsetY/float(tileHeight)) - particles[i][3]) * -tileHeight)
                if ((1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particles[i].xTile) * -tileWidth) + particles[i].width > 0 and (1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particles[i].xTile) * -tileWidth < camera.displayWidth:
                    #self.drawObject("bullet" + str(particles[i][1]) + ".png", (1 + cameraViewX + (-cameraViewToScreenPxlOffsetX/float(tileWidth)) - particles[i][2]) * -tileWidth, (1 + cameraViewY + (-cameraViewToScreenPxlOffsetY/float(tileHeight)) - particles[i][3]) * -tileHeight, gameDisplay)
                    #print math.acos(particles[i][4]/float((particles[i][4]**2 + particles[i][5]**2)**.5))
                    #img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][particles[i][1]], (180*math.acos(particles[i][4]/float((particles[i][4]**2 + particles[i][5]**2)**.5)))/PI)
                    self.DrawImg(particles[i].img, ((1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particles[i].xTile) * -tileWidth, (1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) - particles[i].yTile) * -tileHeight), gameDisplay)

    def DrawWorldInCameraView(self, tileSet, camera, tileWidth, tileHeight, thisLevelMap, gameDisplay, timeElapsedSinceLastFrame=0):
        for i in xrange(int(camera.displayWidth/float(tileWidth))+2):
            for j in xrange(int(camera.displayHeight/float(tileHeight))+2):
                try:
                    imgToDraw, thisLevelMap = self.GetImageForLocation(thisLevelMap, i, j, camera.viewX, camera.viewY, tileSet, timeElapsedSinceLastFrame)
                    if imgToDraw != "":
                        self.DrawImg(imgToDraw,
                          (((i-1)*tileWidth)+camera.viewToScreenPxlOffsetX,
                          ((j-1)*tileHeight)+camera.viewToScreenPxlOffsetY,
                          (((i-1)*tileWidth)+camera.viewToScreenPxlOffsetX)+ tileWidth,
                          (((j-1)*tileHeight)+camera.viewToScreenPxlOffsetY) + tileHeight), gameDisplay)
                except:
                    pass
        return thisLevelMap    

    def GetImageForLocation(self, thisLevelMap, i, j, viewX, viewY, tileSet, timeElapsedSinceLastFrame):
        imgToDraw = ""
        if thisLevelMap[j+viewY][i+viewX] != []:
            if type(thisLevelMap[j+viewY][i+viewX]) is int:
                imgToDraw = self.gfxDictionary[tileSet][thisLevelMap[j+viewY][i+viewX]]
            else:
                thisLevelMap[j+viewY][i+viewX].timeElapsedSinceLastFrame = thisLevelMap[j+viewY][i+viewX].timeElapsedSinceLastFrame + timeElapsedSinceLastFrame
                while thisLevelMap[j+viewY][i+viewX].timeElapsedSinceLastFrame > thisLevelMap[j+viewY][i+viewX].timeBetweenAnimFrame:
                    thisLevelMap[j+viewY][i+viewX].timeElapsedSinceLastFrame = thisLevelMap[j+viewY][i+viewX].timeElapsedSinceLastFrame - thisLevelMap[j+viewY][i+viewX].timeBetweenAnimFrame
                    thisLevelMap[j+viewY][i+viewX].activeImage = thisLevelMap[j+viewY][i+viewX].activeImage + 1
                    if thisLevelMap[j+viewY][i+viewX].activeImage >= ((thisLevelMap[j+viewY][i+viewX].ID + 1) * thisLevelMap[j+viewY][i+viewX].columns - thisLevelMap[j+viewY][i+viewX].ID):
                        thisLevelMap[j+viewY][i+viewX].activeImage = thisLevelMap[j+viewY][i+viewX].activeImage - thisLevelMap[j+viewY][i+viewX].columns
                #print thisLevelMap[j+viewY][i+viewX].activeImage
                imgToDraw = self.gfxDictionary[tileSet][thisLevelMap[j+viewY][i+viewX].activeImage + int(thisLevelMap[j+viewY][i+viewX].ID)]
        return imgToDraw, thisLevelMap

    def ConvertScreenCoordsToTileCoords(self, coordinates, camera, tileWidth, tileHeight):
        return int(coordinates[0]/float(tileWidth) - camera.viewToScreenPxlOffsetX/float(tileWidth) + float(camera.viewX) + 1), int(coordinates[1]/float(tileHeight) - camera.viewToScreenPxlOffsetY/float(tileHeight) + float(camera.viewY) + 1)


class LevelEditorFrame(object):
    def __init__(self, gfx, camera, tileHeight, tileWidth, resChangeOnly=False):
        self.paletteY = 3
        self.paletteX = 1        
        self.frameHeight = int(camera.displayHeight/float(tileHeight))
        self.frameWidth = int(2 + math.ceil(len(gfx.gfxDictionary["World Tiles"])/float(self.frameHeight-self.paletteY)))

        if resChangeOnly == False:
            self.paletteSelectL = 0
            self.paletteSelectR = 0
        self.numberOfWorldTiles = len(gfx.gfxDictionary["World Tiles"])
        
    def DrawLevelEditorFrame(self, camera, tileWidth, tileHeight, thisLevelMap, gfx, gameDisplay):
        for i in xrange(int(camera.displayWidth/float(tileWidth))-self.frameWidth, int(camera.displayWidth/float(tileWidth))+(self.frameWidth-1)):
            for j in xrange(int(camera.displayHeight/float(tileHeight))+2):
              gfx.DrawImg(gfx.gfxDictionary["Level Editor Frame"][1],
                          (((i-1)*tileWidth),
                          ((j-1)*tileHeight),
                          (((i-1)*tileWidth))+ tileWidth,
                          (((j-1)*tileHeight)) + tileHeight), gameDisplay)
    def DrawTextUI(self):
        pass

    def DrawTileAndObjectPalette(self, camera, tileWidth, tileHeight, gfx, gameDisplay):
        for eachPaletteSelector in range(2): #FOR EACH LEFT AND RIGHT SELECTOR
            if eachPaletteSelector == 0:
                thisPaletteSelector = self.paletteSelectL
            elif eachPaletteSelector == 1:
                thisPaletteSelector = self.paletteSelectR
            gfx.DrawImg(gfx.gfxDictionary["World Tiles"][thisPaletteSelector],
                          ((int(camera.displayWidth/float(tileWidth))-self.frameWidth + eachPaletteSelector)*tileWidth,
                          (1)*tileHeight,
                          (int(camera.displayWidth/float(tileWidth))-self.frameWidth + eachPaletteSelector)*tileWidth,
                          (2) * tileHeight), gameDisplay)
        j = 1
        for i in xrange(len(gfx.gfxDictionary["World Tiles"])):
            if (int(i/float(j))+self.paletteY) >= self.frameHeight:
                j = j + 1
            gfx.DrawImg(gfx.gfxDictionary["World Tiles"][i],
                          ((int(camera.displayWidth/float(tileWidth))-self.frameWidth + (j-1) + self.paletteX - 1)*tileWidth,
                          ((i%(self.frameHeight - self.paletteY))+self.paletteY)*tileHeight,
                          (int(camera.displayWidth/float(tileWidth))-self.frameWidth + (j-1) + self.paletteX - 1)*tileWidth,
                          ((i%(self.frameHeight - self.paletteY))+self.paletteY) + tileHeight), gameDisplay)

    def PaletteItemSelect(self, userMouse, camera, tileWidth, tileHeight, gfx):
        if userMouse.btn[0] == 1:
            #self.paletteSelectL = int(((camera.displayWidth - userMouse.coords[0])/float(tileWidth) - int(int(camera.displayWidth/float(tileWidth)) - (self.frameWidth + self.paletteX - 1)*tileWidth))*(self.frameHeight - self.paletteY)) + int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))
            #self.paletteSelectL = int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))
            #self.paletteSelectL = int()
            #print str(int((userMouse.coords[0] - (self.paletteX * tileWidth))/float(tileWidth)) - (int(camera.displayWidth/float(tileWidth)) - self.frameWidth) + 1)
            if ((int((userMouse.coords[0] - (self.paletteX * tileWidth))/float(tileWidth)) - (int(camera.displayWidth/float(tileWidth)) - self.frameWidth) + 1) * int(self.frameHeight - self.paletteY)) + int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight)) < len(gfx.gfxDictionary["World Tiles"]):
                self.paletteSelectL = ((int((userMouse.coords[0] - (self.paletteX * tileWidth))/float(tileWidth)) - (int(camera.displayWidth/float(tileWidth)) - self.frameWidth) + 1) * int(self.frameHeight - self.paletteY)) + int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))
        if userMouse.btn[2] == 1:
            #self.paletteSelectR = int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))
            if ((int((userMouse.coords[0] - (self.paletteX * tileWidth))/float(tileWidth)) - (int(camera.displayWidth/float(tileWidth)) - self.frameWidth) + 1) * int(self.frameHeight - self.paletteY)) + int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight)) < len(gfx.gfxDictionary["World Tiles"]):
                self.paletteSelectR = ((int((userMouse.coords[0] - (self.paletteX * tileWidth))/float(tileWidth)) - (int(camera.displayWidth/float(tileWidth)) - self.frameWidth) + 1) * int(self.frameHeight - self.paletteY)) + int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))

class LogicHandler(object):
    def HandleMouseEvents(self, userMouse, camera, displayFrame, tileWidth, tileHeight, thisLevelMap, gfx):
        self.displayFrame = displayFrame
        self.thisLevelMap = thisLevelMap
        if userMouse.btn[0] == 1 or userMouse.btn[2] == 1:
            if (userMouse.coords[0] >= (int(camera.displayWidth/float(tileWidth)) - self.displayFrame.frameWidth + self.displayFrame.paletteX - 1)*tileWidth) and userMouse.coords[1] >= self.displayFrame.paletteY * tileHeight + 1:
            #and (userMouse.coords[0] <= (int(camera.displayWidth/float(tileWidth)) - self.displayFrame.frameWidth + self.displayFrame.paletteX - 1)*tileWidth + tileWidth)
                self.displayFrame.PaletteItemSelect(userMouse, camera, tileWidth, tileHeight, gfx)
            else:
                self.EditLevel(userMouse, displayFrame.paletteSelectL, displayFrame.paletteSelectR, thisLevelMap)
        return self.displayFrame, self.thisLevelMap

    def EditLevel(self, userMouse, paletteSelectL, paletteSelectR, thisLevelMap):
        if userMouse.btn[2] == 1:
            thisLevelMap[userMouse.yTile][userMouse.xTile] = paletteSelectR
        if userMouse.btn[0] == 1:
            thisLevelMap[userMouse.yTile][userMouse.xTile] = paletteSelectL
        return thisLevelMap
    
    def HandleHeyPressAndGameEvents(self, exiting, lost, character):
        #HANDLE KEY PRESS/RELEASE/USER ACTIONS
        enterPressed = False
        keys = pygame.key.get_pressed()
        mouseCoords = pygame.mouse.get_pos()
        mouseBtn = pygame.mouse.get_pressed()
        savePressed = False
        for event in pygame.event.get():                #ASK WHAT EVENTS OCCURRED
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                exiting = True
                lost = False
            #IF PLAYER MUST PRESS TRIGGER REPEATEDLY, FIRE ON KEY UP:
            #if event.type == pygame.KEYUP and keys[pygame.K_SPACE] and ammo >0:
            #   character.shotsFiredFromMe = True

            #IF PLAYER MUST PRESS TRIGGER REPEATEDLY, FIRE ON KEY DOWN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    character.shotsFiredFromMe = True
                if event.key == pygame.K_KP1 or event.key == pygame.K_1:
                    character.activeWeapon = 0
                if event.key == pygame.K_KP2 or event.key == pygame.K_2:
                    character.activeWeapon = 1
                if event.key == pygame.K_KP3 or event.key == pygame.K_3:
                    character.activeWeapon = 2
                if event.key == pygame.K_KP4 or event.key == pygame.K_4:
                    character.activeWeapon = 3
                if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                    enterPressed = True
                if event.key == 115:
                    savePressed = True
            
        character.deltaX = 0
        character.deltaY = 0                                #VS. ASK WHAT KEYS ARE DOWN AT THIS MOMENT.
        if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            character.deltaX = character.speed
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            character.deltaX = -character.speed
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            character.deltaY = -character.speed
        if keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            character.deltaY = character.speed

        if character.deltaX != 0 or character.deltaY != 0:
            character.xFacing = 0
            character.yFacing = 0
            if character.deltaX != 0:
                character.xFacing = character.deltaX/abs(character.deltaX)
            if character.deltaY != 0:
                character.yFacing = character.deltaY/abs(character.deltaY)

            
        #IF PLAYER SHOULD BE ABLE TO HOLD DOWN TRIGGER:
        #if keys[pygame.K_SPACE] and ammo >0:
        #    shotsFiredFromMe = True
        return exiting, lost, character, enterPressed, mouseCoords, mouseBtn, savePressed

    def FixDiagSpeed(self, XDelta, YDelta, speed):
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

    def GenerateParticles(self, particles, character, tileHeight, tileWidth, gfx):
        if character.shotsFiredFromMe == True and not(character.yFacing == 0 and character.xFacing == 0) and character.activeWeapon < len(character.weapons):
            userBullet = Bullet("User Bullet", character.weapons[character.activeWeapon].name, character.xTile, character.yTile, 0, 0, character.weapons[character.activeWeapon].damage, character.weapons[character.activeWeapon].physicsIndicator, 1, character.weapons[character.activeWeapon].generateBulletWidth, character.weapons[character.activeWeapon].generateBulletHeight, character.weapons[character.activeWeapon].generateBulletSpeed, character.weapons[character.activeWeapon].generateBulletSpeed) #putting multiple instances of the image itself in the array because they could be rotated at different directions and putting a pointer to one image and then rotating many many times severly impacts FPS due to slow rotate method
            userBullet.speed = userBullet.defaultSpeed
            if character.xFacing == 0:
                tempDX = 0 #THIS AVOIDS THE DIVIDE BY 0 ERROR
                if character.yFacing == 0:
                    tempDY = 0
                    img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][int(userBullet.weapon)], (180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
                else:
                    tempDY = (character.yFacing/float(abs(character.yFacing))) * userBullet.speed
                    img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][int(userBullet.weapon)], ((-character.yFacing/float(abs(character.yFacing))) * 180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
            else:
                if character.yFacing == 0:
                    tempDX = (character.xFacing/float(abs(character.xFacing))) * userBullet.speed
                    tempDY = 0
                    img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][int(userBullet.weapon)], (180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
                else:
                    tempDX = (character.xFacing/float(abs(character.xFacing))) * (math.cos(math.atan(abs(character.yFacing/float(character.xFacing)))) * userBullet.speed)
                    tempDY = (character.yFacing/float(abs(character.yFacing))) * (math.sin(math.atan(abs(character.yFacing/float(character.xFacing)))) * userBullet.speed)
                    img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][int(userBullet.weapon)], ((-character.yFacing/float(abs(character.yFacing))) * 180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
                           #Name, weapon, world X Loc, world Y Loc,  dx,    dy, damage, bounces remaining, bullet width px, bullet height px, frame speed, default speed, image
            userBullet.dx = tempDX
            userBullet.dy = tempDY
            userBullet.img = img
            particles.append(userBullet)
            character.shotsFiredFromMe = False
        return particles, character

    def MoveParticlesAndHandleParticleCollision(self, particles, thisLevelMap):
        #Move PARTICLES, OR DELETE THEM IF THEY REACH WORLD END
        myDeletedParticles = []
        for i in xrange(len(particles)):
            if particles[i].xTile + particles[i].dx > len(thisLevelMap[0]) or particles[i].yTile + particles[i].dy > len(thisLevelMap) or particles[i].xTile + particles[i].dx < 0 or particles[i].yTile + particles[i].dy < 0:
                myDeletedParticles.append(i)
            else:
                particles[i].xTile = particles[i].xTile + particles[i].dx
                particles[i].yTile = particles[i].yTile + particles[i].dy
        for i in xrange(len(myDeletedParticles)):
            del particles[myDeletedParticles[i]-i]
            
        #COLLISION DETECT IF WALL HIT, AND BOUNCE/PERFORM ACTION IF NECESSARY
            
        return particles

    def ManageTimeAndFrameRate(self, lastTick, clock, FPSLimit):
        timeElapsedSinceLastFrame = clock.get_time() - lastTick
        lastTick = clock.tick(FPSLimit)
        return timeElapsedSinceLastFrame

    def AdjustSpeedBasedOnFrameRate(self, timeElapsedSinceLastFrame, particleList, character):
        #MAKE PARTICLE SPEED CHANGE BASED ON FRAME RATE
        #character.speedThisFrameRate = character.defaultSpeed
        for i in xrange(len(particleList)):
            particleList[i].speed = particleList[i].defaultSpeed * timeElapsedSinceLastFrame
            if particleList[i].dx < 0:
                particleList[i].dx = -particleList[i].speed
            elif particleList[i].dx > 0:
                particleList[i].dx = particleList[i].speed
            if particleList[i].dy < 0:
                particleList[i].dy = -particleList[i].speed
            elif particleList[i].dy > 0:
                particleList[i].dy = particleList[i].speed
        #REDUCE PARTICLE SPEED SO IT DOESN'T TRAVEL FASTER WHEN DIAGONAL
            particleList[i].dx, particleList[i].dy = self.FixDiagSpeed(particleList[i].dx, particleList[i].dy, particleList[i].speed)
        if timeElapsedSinceLastFrame < 2000:
            character.speed = character.defaultSpeed * timeElapsedSinceLastFrame
            
        character.deltaX, character.deltaY = self.FixDiagSpeed(character.deltaX, character.deltaY, character.speed)        
        return particleList, character

class MenuScreen(object):
    def __init__(self, menuType, screenResSelection, difficultySelection, displayType, gameDisplay):
        self.gameDisplay = gameDisplay
        self.menuType = menuType
        self.screenResSelection = screenResSelection
        self.difficultySelection = difficultySelection
        self.displayType = displayType
        self.menuDirectory = "Main"
        self.menuJustOpened = True
        #self.score = 0
        self.highScoreDifficulty = 0
        #self.myHealth = 100
        self.currentLevel = 0
        self.menuSelectionIndex = 6
        #self.ammo = 0
        self.displayWidth = screenResChoices[screenResSelection][0]
        self.displayHeight = screenResChoices[screenResSelection][1]
        if self.displayType == "Full Screen":
            self.gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight), pygame.FULLSCREEN)
        else:
            self.gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight))
        self.colorIntensity = 255
        self.colorIntensityDirection = 5
        self.startPlay = False
        self.gfx = GfxHandler()
        self.logic = LogicHandler()
        self.userMouse = Mouse()
        self.exiting = False
        self.lost = False
        self.userCharacter = Character("User")
        self.userCharacter.speed = 1
        self.screenMoveCounter = 0
        self.menuFPSLimit = 120
        self.clock = pygame.time.Clock()
        self.clock.tick()
        self.enterPressed = False
        self.personXDeltaWas = 0
        self.personYDeltaWas = 0
        self.myHighScoreDatabase = HighScoresDatabase()
        self.myHighScores = self.myHighScoreDatabase.LoadHighScores()
        self.difficultyChoices = self.myHighScoreDatabase.difficulties

    def UpdateScreenAndLimitFPS(self, FPSLimit):
        self.limit = FPSLimit
        pygame.display.update()
        self.clock.tick(FPSLimit)
        
    def DisplayMenuScreenAndHandleUserInput(self):
        while self.exiting == False and self.startPlay == False:
            self.DisplayTitle()
            self.PulsateSelectionColor()
            self.HandleMenuBackground()
            self.GetKeyPress()
            if self.menuDirectory == "Main":
                self.DisplayMainMenu()
                if self.menuJustOpened == False:
                    self.HandleUserInputMainMenu()
                self.menuJustOpened = False
            elif self.menuDirectory == "Settings":
                self.DisplaySettingsMenu()
                self.HandleUserInputSettingsMenu()
            elif self.menuDirectory == "Credits":
                self.DisplayCreditsMenu()
                self.HandleUserInputCreditsMenu()
            elif self.menuDirectory == "How To Play":
                self.DisplayHowToMenu()
                self.HandleUserInputHowToMenu()
            elif self.menuDirectory == "High Scores":
                self.DisplayHighScoresMenu()
                self.HandleUserInputHighScoresMenu()
                
            self.personYDeltaWas = self.userCharacter.deltaY
            self.personXDeltaWas = self.userCharacter.deltaX
            self.UpdateScreenAndLimitFPS(self.menuFPSLimit)
            self.gameDisplay.fill(black)
        del self.clock
        return self.difficultySelection, self.screenResSelection, self.displayType, self.exiting
    
    def DisplayTitle(self):
        gameTitle = "2d Game Framework"
        self.smallText = pygame.font.Font("freesansbold.ttf", 24)
        self.largeText = pygame.font.Font("freesansbold.ttf", 48)
        self.textSurf, self.textRect = self.gfx.CreateTextObjects(gameTitle, self.largeText, white)
        self.textRect.center = ((self.displayWidth/2.0), (self.screenMoveCounter + 25))
        self.gameDisplay.blit(self.textSurf, self.textRect)
        if self.menuType == "Paused":
            self.textSurf, self.textRect = self.gfx.CreateTextObjects("-Paused-", self.smallText, white)
            self.textRect.center = ((self.displayWidth/2.0), (self.screenMoveCounter + 60))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def PulsateSelectionColor(self):
        if self.colorIntensity + self.colorIntensityDirection > 255:
            self.colorIntensityDirection = -5
        elif self.colorIntensity + self.colorIntensityDirection < 65:
            self.colorIntensityDirection = 5
        self.colorIntensity = self.colorIntensity + self.colorIntensityDirection

    def HandleMenuBackground(self):
        pass
        #self.currentLevel, self.activeWeapon, self.enemiesAlive, self.myEnemies, self.myProjectiles = self.menuGameEventHandler.addGameObjects(
            #self.enemiesAlive, self.currentLevel, self.activeWeapon, self.myEnemies, self.starProbabilitySpace, self.starDensity, self.starMoveSpeed, self.myProjectiles, self.displayWidth)
        #self.starMoveSpeed = self.menuGameEventHandler.adjustStarMoveSpeed(self.maximumStarMoveSpeed, self.numberOfStarSpeeds)
        #self.myProjectiles, self.myEnemies, self.myHealth, self.score, self.enemiesAlive, self.y, self.ammo = self.menuGameEventHandler.MoveAndDrawProjectilesAndEnemies(
            #self.myProjectiles, self.myEnemies, self.myHealth, self.score, self.enemiesAlive, self.x, self.y, self.rocketWidth, self.rocketHeight, self.difficultySelection, self.displayWidth, self.displayHeight, self.ammo, self.starMoveSpeed)
        #self.menuGameEventHandler.drawObject(myCharacter, self.x, self.y)

    def GetKeyPress(self):
        self.exiting, self.lost, self.userCharacter, self.enterPressed, self.userMouse.coords, self.userMouse.btn, self.savePressed = self.logic.HandleHeyPressAndGameEvents(self.exiting, self.lost, self.userCharacter)

    def DisplayMainMenu(self):
        self.mainMenuItemMargin = 25
        for self.i in xrange(7):
            self.rgb = (255, 255, 255)
            if self.i == self.menuSelectionIndex:
                self.rgb = (self.colorIntensity, 0, 0)
            if self.i == 6:
                if self.menuType == "Paused":
                    self.text = "Resume"
                else:
                    self.text = "Play"
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
            self.textSurf, self.textRect = self.gfx.CreateTextObjects(self.text, self.smallText, self.rgb)
            self.textRect.center = ((self.displayWidth/2.0), (self.displayHeight/2.0 - self.i*(self.mainMenuItemMargin) + self.screenMoveCounter))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def DisplaySettingsMenu(self):
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
            self.textSurf, self.textRect = self.gfx.CreateTextObjects(self.text, self.smallText, self.rgb)
            self.textRect.center = ((self.displayWidth/2.0), (self.displayHeight/2.0 - self.i*(self.mainMenuItemMargin)))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def DisplayCreditsMenu(self):
        creditsMoveSpeed = 5
        if self.screenMoveCounter < self.displayHeight:
            self.screenMoveCounter = self.screenMoveCounter + creditsMoveSpeed
            self.DisplayTitle()
            self.DisplayMainMenu()
    
        for self.i in xrange(3):
            self.rgb = (255, 255, 255)
            if self.i == 2:
                self.text = "Programming by Mike Finnegan"
            if self.i == 1:
                self.text = "Art by Mike Finnegan"
            if self.i == 0:
                self.text = "Music/SFX by Mike Finnegan"
            self.textSurf, self.textRect = self.gfx.CreateTextObjects(self.text, self.smallText, self.rgb)
            #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.character.speed)))
            self.textRect.center = ((self.displayWidth/2.0), ((self.i * self.mainMenuItemMargin) + self.screenMoveCounter - self.displayHeight/2.0))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def DisplayHowToMenu(self):
        howToSpeed = 5
        if self.screenMoveCounter < self.displayHeight:
            self.screenMoveCounter = self.screenMoveCounter + howToSpeed
            self.DisplayTitle()
            self.DisplayMainMenu()
        for self.i in xrange(3):
            self.rgb = (255, 255, 255)
            if self.i == 2:
                self.text = "Escape key: pause game"
            if self.i == 1:
                self.text = "Space bar: shoot aliens"
            if self.i == 0:
                self.text = "Arrow keys Up, Down, Left, Right: fly spacecraft"
            self.textSurf, self.textRect = self.gfx.CreateTextObjects(self.text, self.smallText, self.rgb)
            #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.character.speed)))
            self.textRect.center = ((self.displayWidth/2.0), ((self.i * self.mainMenuItemMargin) + self.screenMoveCounter - self.displayHeight/2.0))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def DisplayHighScoresMenu(self):
        if self.menuSelectionIndex == 0:
            self.rgb = (self.colorIntensity, 0, 0)
        else:
            self.rgb = (255, 255, 255)
        self.textSurf, self.textRect = self.gfx.CreateTextObjects("<<  " + self.difficultyChoices[self.highScoreDifficulty] + " High Scores  >>", self.smallText, self.rgb)
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
                    self.textSurf, self.textRect = self.gfx.CreateTextObjects(self.text, self.smallText, self.rgb)
                    #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.character.speed)))
                    self.textRect.center = ((self.displayWidth*((self.j+1)/6.0)), ((self.i * self.mainMenuItemMargin) + self.displayHeight/2.0))
                elif self.i == self.myHighScoreDatabase.numberOfRecordsPerDifficulty:
                    if self.menuSelectionIndex == 1:
                        self.rgb = (self.colorIntensity, 0, 0)
                    else:
                        self.rgb = (255, 255, 255)
                    self.text = "Go Back"
                    self.textSurf, self.textRect = self.gfx.CreateTextObjects(self.text, self.smallText, self.rgb)
                    self.textRect.center = ((self.displayWidth*.8), (self.displayHeight * .95))
                else:
                    self.rgb = (255, 255, 255)
                    #print str(self.highScoreDifficulty)
                    self.text = str(self.myHighScores[self.highScoreDifficulty][self.i][self.j])
                    self.textSurf, self.textRect = self.gfx.CreateTextObjects(self.text, self.smallText, self.rgb)
                    #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.character.speed)))
                    self.textRect.center = ((self.displayWidth*((self.j+1)/6.0)), ((self.i * self.mainMenuItemMargin) + self.displayHeight/2.0))
                self.gameDisplay.blit(self.textSurf, self.textRect)

    def HandleUserInputMainMenu(self):
        if self.userCharacter.deltaY == self.userCharacter.speed and self.personYDeltaWas == 0 and self.menuSelectionIndex >0:
            self.menuSelectionIndex = self.menuSelectionIndex - 1
            if self.menuSelectionIndex == 5 and self.menuType == "Paused":
                self.menuSelectionIndex = self.menuSelectionIndex - 1
        if self.userCharacter.deltaY == -self.userCharacter.speed and self.personYDeltaWas == 0 and self.menuSelectionIndex < 6:
            self.menuSelectionIndex = self.menuSelectionIndex + 1
            if self.menuSelectionIndex == 5 and self.menuType == "Paused":
                self.menuSelectionIndex = self.menuSelectionIndex + 1    
        if ((self.userCharacter.deltaX == self.userCharacter.speed and self.personXDeltaWas == 0) or (self.enterPressed == True)) and self.menuSelectionIndex == 5:
            self.difficultySelection = (self.difficultySelection + 1) %len(self.difficultyChoices)
        if (self.userCharacter.deltaX == -self.userCharacter.speed and self.personXDeltaWas == 0) and self.menuSelectionIndex == 5:
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

    def HandleUserInputSettingsMenu(self):
        if self.userCharacter.deltaY == self.userCharacter.speed and self.personYDeltaWas == 0 and self.menuSelectionIndex >0:
            self.menuSelectionIndex = self.menuSelectionIndex - 1
        if self.userCharacter.deltaY == -self.userCharacter.speed and self.personYDeltaWas == 0 and self.menuSelectionIndex < 4:
            self.menuSelectionIndex = self.menuSelectionIndex + 1
        if ((self.userCharacter.deltaX == self.userCharacter.speed and self.personXDeltaWas == 0) or (self.enterPressed == True)) and self.menuSelectionIndex == 4:
            self.screenResSelection = (self.screenResSelection + 1) %len(screenResChoices)
        if (self.userCharacter.deltaX == -self.userCharacter.speed and self.personXDeltaWas == 0) and self.menuSelectionIndex == 4:
            self.screenResSelection = (self.screenResSelection - 1) %len(screenResChoices)
        if (self.enterPressed == True or (abs(self.userCharacter.deltaX) == self.userCharacter.speed and self.personXDeltaWas == 0))and self.menuSelectionIndex == 3:
            if self.displayType == "Window":
                self.displayType = "Full Screen"
            else:
                self.displayType = "Window"
            self.fullScreenWindowChanged = True
        if ((((self.userCharacter.deltaX == self.userCharacter.speed and self.personXDeltaWas == 0) or (self.enterPressed == True)) and self.menuSelectionIndex == 4) or ((self.userCharacter.deltaX == -self.userCharacter.speed and self.personXDeltaWas == 0) and self.menuSelectionIndex == 4)) or self.fullScreenWindowChanged == True:
            self.displayWidth = screenResChoices[self.screenResSelection][0]
            self.displayHeight = screenResChoices[self.screenResSelection][1]
            if self.displayType == "Window":
                gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight))
            else:
                gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight), pygame.FULLSCREEN)
            self.myProjectiles = []
            self.fullScreenWindowChanged = False
        if self.enterPressed == True and self.menuSelectionIndex == 0:
            self.menuDirectory = "Main"
            self.menuSelectionIndex = 2

    def HandleUserInputCreditsMenu(self):
        if self.enterPressed == True:
            self.screenMoveCounter = 0
            self.menuDirectory = "Main"

    def HandleUserInputHowToMenu(self):
        if self.enterPressed == True:
            self.screenMoveCounter = 0
            self.menuDirectory = "Main"

    def HandleUserInputHighScoresMenu(self):
        if (self.userCharacter.deltaY == self.userCharacter.speed and self.personYDeltaWas == 0):
            self.menuSelectionIndex = (self.menuSelectionIndex + 1) % 2
        if (self.userCharacter.deltaY == -self.userCharacter.speed and self.personYDeltaWas == 0):
            self.menuSelectionIndex = (self.menuSelectionIndex - 1) % 2
        if (self.menuSelectionIndex == 0 and self.userCharacter.deltaX == self.userCharacter.speed and self.personXDeltaWas == 0):
            self.highScoreDifficulty = (self.highScoreDifficulty + 1) % len(self.difficultyChoices)
        if (self.menuSelectionIndex == 0 and self.userCharacter.deltaX == -self.userCharacter.speed and self.personXDeltaWas == 0):
            self.highScoreDifficulty = (self.highScoreDifficulty - 1) % len(self.difficultyChoices)
        if self.menuSelectionIndex == 1 and self.enterPressed == True:
            self.screenMoveCounter = 0
            self.menuDirectory = "Main"
            self.menuSelectionIndex = 4

class HighScoresDatabase(object):
    def __init__(self):
        self.numberOfRecordsPerDifficulty = 10
        self.difficulties = ["Easy", "Medium", "Hard", "Expert"]
        self.databaseName = "../Data/High_Scores.db"
        
    def FillInBlankHighScores(self, highScoresArray):
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

    def LoadHighScores(self):
        try:
            self.highScoresArray = [[],]
            self.connection = sqlite3.connect(self.databaseName)
            self.c = self.connection.cursor()
            self.row = ([])
            for self.loadCounter in xrange(len(self.difficulties)):
                self.a = [[],]                
                self.c.execute("""SELECT * FROM " + self.difficulties[self.loadCounter] + "HighScoreTable ORDER BY scoreRecordPK""")
                for self.row in self.c.fetchall():
                    self.a.append([self.row[0], str(self.row[1]), self.row[2], str(self.row[3]), str(self.row[4])])
                #self.highScoresArray.append([row(0), row(1), row(2), row(3), row(4)])
                self.a.remove([])
                #self.a = self.a.append(self.FillInBlankHighScores(self.a))
                #self.a.remove([])
                #print self.a
                self.highScoresArray.insert(self.loadCounter, self.a)
        except:
            self.InitializeDatabase()
        
        self.connection.close()
        return self.highScoresArray

    def InitializeDatabase(self):
        self.connection = sqlite3.connect(self.databaseName)
        self.c = self.connection.cursor()
        for difficulty in self.difficulties:
            self.c.execute("DROP TABLE IF EXISTS " + difficulty + "HighScoreTable")
            self.c.execute("CREATE TABLE " + difficulty + "HighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")

        for self.loadCounter in xrange(len(self.difficulties)):
            #self.highScoresArray.append([])
            self.highScoresArray.insert(self.loadCounter, self.FillInBlankHighScores(self.highScoresArray[self.loadCounter]))
            #self.highScoresArray = self.FillInBlankHighScores(self.highScoresArray[self.loadCounter])
        self.highScoresArray.remove([])
        for self.loadCounter in xrange(len(self.difficulties)):
            self.UpdateHighScoresForThisDifficulty(self.highScoresArray[self.loadCounter], self.loadCounter)
        self.connection.close()
        return self.highScoresArray
                
    def UpdateHighScoresForThisDifficulty(self, workingArray, difficulty):
        try:
            self.workingArray = workingArray
            self.difficulty = difficulty
            self.connection = sqlite3.connect(self.databaseName)
            self.c = self.connection.cursor()
            self.updateCounter = -1            
            for self.row in self.workingArray:
                self.updateCounter = self.updateCounter + 1
                if self.updateCounter == 0:
                    self.c.execute("DROP TABLE IF EXISTS " + self.difficulties[self.difficulty] + "HighScoreTable")
                    self.c.execute("CREATE TABLE " + self.difficulties[self.difficulty] + "HighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")
                self.c.execute("INSERT INTO " + self.difficulties[self.difficulty] + "HighScoreTable Values(?, ?, ?, ?, ?)", tuple((int(workingArray[self.updateCounter][0]), self.workingArray[self.updateCounter][1], int(self.workingArray[self.updateCounter][2]), self.workingArray[self.updateCounter][3], self.workingArray[self.updateCounter][4])))                
                self.connection.commit()
        except:
            self.InitializeDatabase()
        self.connection.close()
        
class GameplayObject(object):
    pass

class Weapon(GameplayObject):
    def __init__(self, name, damage, ammo, physIndic, generateBulletWidth, generateBulletHeight, generateBulletSpeed):
        self.name = name
        self.damage = damage
        self.ammo = ammo
        self.physicsIndicator = physIndic
        self.generateBulletWidth = generateBulletWidth
        self.generateBulletHeight = generateBulletHeight
        self.generateBulletSpeed = generateBulletSpeed

class WorldObject(GameplayObject):
    def __init__(self, name = "", desc = "", columns = 0, touchAction = 0, attackAction = 0, time = 0, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThrough = False):
        self.name = name
        self.desc = desc
        self.columns = columns
        self.walkThroughPossible = walkThrough
        self.actionOnTouch = touchAction
        self.actionOnAttack = attackAction
        self.activeImage = ID*(columns - 1)
        self.timeBetweenAnimFrame = time
        self.timeElapsedSinceLastFrame = 0
        self.ID = ID
        self.scoreChangeOnTouch = scoreChangeOnTouch
        self.scoreChangeOnAttack = scoreChangeOnAttack
        self.healthChangeOnTouch = healthChangeOnTouch
        self.healthChangeOnAttack = healthChangeOnAttack

class Bullet(WorldObject):
    #Name, weapon, world X Loc, world Y Loc,  dx,    dy, damage, physics actions remaining, particle width px, particle height px, frame speed, default speed, image, particlePhysicsLevel
    #if particlePhysicsLevel >= wallPhysicsLevel + 3 then particle pushes the wall
    #if particlePhysicsLevel = wallPhysicsLevel + 2 then particle goes through wall
    #if particlePhysicsLevel = wallPhysicsLevel + 1 then particle bounces off wall
    #if particlePhysicsLevel <= wallPhysicsLevel then particle absorbs into wall

    #physics actions represent the number of remaining times the particle can push/go through/bounce off walls

    #Name, weapon, world X Loc, world Y Loc,  dx,    dy, damage, bounces remaining, bullet width px, bullet height px, frame speed, default speed, image
    
    def __init__(self, name, weapon, xTile, yTile, dx, dy, damage, physicsIndicator, physicsCounter, width, height, speed = .01, defaultSpeed = .01, img=None):
        self.name = name
        self.defaultSpeed = defaultSpeed
        self.speed = speed
        self.xTile = xTile
        self.yTile = yTile
        self.dx = dx
        self.dy = dy
        self.width = width
        self.height = height
        self.damage = damage
        self.physicsIndicator = physicsIndicator
        self.physicsCounter = physicsCounter
        self.cameFromObjectName = weapon
        self.img = img #IMAGE ASSIGNED BECAUSE 1) IMAGE NEEDS TO BE GENERATE AT TIME OF OBJECT CREATION, AND 2) WILL NOT BE CHANGING THROUGHOUT THE LIFE OF THE OBJECT
        #self.worldObjectID = worldObjectID
        self.imagesGFXName = "../Images/bullets.png"
        self.imagesGFXNameDesc = "Bullets"
        self.imagesGFXRows = 4
        self.imagesGFXColumns = 1
        self.weapon = weapon

class Character(WorldObject):
    def __init__(self, name = "", boundToCamera = False, xFacing = 0, yFacing = 0, xTile = 18, yTile = 18, deltaX = 0, deltaY = 0, timeSpentFalling = 0, gravityYDelta = 0, imgDirectionIndex = 0, imgLegIndex = 0, millisecondsOnEachLeg = 250, numberOfFramesAnimPerWalk = 3, defaultSpeed = .5, ammo = 1000, activeWeapon = 0, score = 0, weapons = [], inventory = [], width = 32, height = 32, shotsFiredFromMe = False):
        #GENERAL
        self.name = name
        self.numberOfFramesAnimPerWalk = numberOfFramesAnimPerWalk #3
        self.numberOfDirectionsFacingToDisplay = 8
        self.imagesGFXName = "../Images/userplayer.png"
        self.imagesGFXNameDesc = "User Player"
        self.imagesGFXRows = self.numberOfDirectionsFacingToDisplay
        self.imagesGFXColumns = self.numberOfFramesAnimPerWalk

        #LOCATION/APPEARANCE
        self.xFacing = xFacing
        self.yFacing = yFacing
        self.xTile = xTile
        self.yTile = yTile - 1
        self.x = 0 #NEEDS TO BE CALCULATED
        self.y = 0 #NEEDS TO BE CALCULATED
        self.xok = 1
        self.yok = 1 
        self.deltaX = deltaX #specifies the change in xTile on the next frame
        self.deltaY = deltaY #specifies the change in yTile on the next frame
        self.timeSpentFalling = timeSpentFalling #This is important to track because falling velocity due to gravity is non-linear
        self.gravityYDelta = 0
        self.imgDirectionIndex = imgDirectionIndex #IMAGE INDICIES REFERENCE IMAGE BECAUSE IMAGE WILL CHANGE THROUGHOUT LIFE OF THE OBJECT
        self.imgLegIndex = imgLegIndex
        self.millisecondsOnEachLeg = millisecondsOnEachLeg #250
        self.millisecondsOnThisLeg = 0
        self.boundToCamera = boundToCamera

        #SPECIFIC PROPERTIES
        self.defaultSpeed = defaultSpeed #.5
        self.speed = 0
        self.health = 100
        self.ammo = ammo
        self.activeWeapon = activeWeapon
        self.score = score
        self.weapons = weapons
        self.inventory = inventory
        self.width = width
        self.height = height
        self.deltaXScreenOffset = 0 #THIS WILL ALWAYS BE CALCULATED BY THE GAME, ABSTRACTED AWAY
        self.deltaYScreenOffset = 0 #THIS WILL ALWAYS BE CALCULATED BY THE GAME, ABSTRACTED AWAY
        self.shotsFiredFromMe = shotsFiredFromMe
        self.weapons = weapons

    def AI(self):
        pass

    def InitializeScreenPosition(self, camera, tileWidth, tileHeight):
        self.x = (self.xTile - camera.viewX) * tileWidth
        self.y = (self.yTile - camera.viewY) * tileHeight

    def Move(self, camera, tileWidth, tileHeight, deltaX, deltaY):
        if self.xok == 1:
            self.x = self.x + deltaX + self.deltaXScreenOffset #Move USER'S CHARACTER, BUT DON'T Move HIM IN ONE DIRECTION IF THE SCREEN SCROLL IS ALSO MOVING IN THAT DIRECTION
            self.xTile = 1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + (self.x/float(tileWidth)) #0 BASED, JUST LIKE THE ARRAY, THIS IS LEFT MOST POINT OF USER'S CHAR
        if self.yok == 1:
            self.y = self.y + deltaY + self.deltaYScreenOffset #Move USER'S CHARACTER, BUT DON'T Move HIM IN ONE DIRECTION IF THE SCREEN SCROLL IS ALSO MOVING IN THAT DIRECTION
            self.yTile = 1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + (self.y/float(tileHeight)) #0 BASED, JUST LIKE THE ARRAY, THIS IS TOP MOST POINT OF USER'S CHAR

    def GetLocationInWorld(self):
        return [self.xTile, self.yTile] #UNITS IN WORLD TILES

    def GetLocationOnScreen(self):
        return [self.x, self.y] #UNITS IN SCREEN PIXELS

    def TestIfLocationVisibleOnScreen(self):
        pass

    def UpdateDirectionBasedOnWallCollisionTest(self, thisLevelMap, camera, tileHeight, tileWidth, gravityAppliesToWorld, stickToWallsOnCollision):

        #This acts as a buffer to allow user to not get up against floor/ceiling
        #because the distance the user will travel over the next frame cannot
        #be known with absolute certainty because it is a function of the speed
        #at which the next frame is drawn. This prevents clipping by making
        #a judgement call that the next frame won't likely be drawn twice as slow as,
        #or longer, than this frame was drawn.
        
        #CHARACTER<->WALL COLLISION DETECTION:
        #COLLISION DETECTION ACTUALLY HAS TO CHECK 2 DIRECTIONS FOR EACH OF THE 4 CORNERS FOR 2D MoveMENT:
        #EACH OF THESE 2x4 CHECKS ARE LABLED BELOW AND CODE IS MARKED INDICATING WHICH
        #CORNER CHECK IS OCCURRING. THIS WOULD BE GOOD ENOUGH IF WE JUST STOPPED THE self
        #ON COLLISION. FOR A BETTER USER EXPERIENCE, IF USER IS MOVING IN 2 DIRECTIONS (FOR EX LEFT + DOWN),
        #BUT ONLY ONE DIRECTION (FOR EX: LEFT) COLLIDES, THEN WE WANT TO KEEP THE USER MOVING
        #IN THE 1 GOOD DIRECTION ONLY. THIS REQUIRES 2 COLLISION CHECKS @ EACH OF THE 8 POINTS BECAUSE
        #THE OUTCOME AND REMEDIATION OF A COLLISION CHECK ON ONE SIDE AFFECTS BY THE OUTCOME AND REMEDIATION
        #OF THE NEXT COLLISION CHECK @ 90deg/270deg DIFFERENT DIRECTION AND BECAUSE PLAYER'S self IS SMALLER
        #THAN THE TILES THE WORLD IS MADE OF.

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


        self.yok = 1
        self.xok = 1
        needToRevert = 0
        #COLLISION CHECK @ C or @ D or @ H or @ G
        if (self.deltaX > 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + self.deltaY + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + (self.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+(-self.deltaXScreenOffset + self.deltaX)+ self.deltaXScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (self.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + self.deltaY + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + (self.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+(-self.deltaXScreenOffset + self.deltaX)+ self.deltaXScreenOffset)/float(tileWidth)))])) or ((self.deltaX)< 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + self.deltaY + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+(-self.deltaXScreenOffset + self.deltaX)+ self.deltaXScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (self.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + self.deltaY + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+(-self.deltaXScreenOffset + self.deltaX)+ self.deltaXScreenOffset)/float(tileWidth)))])):
            tempxok = self.xok #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
            tempdeltaXScreenOffset = self.deltaXScreenOffset #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
            temppersonXDelta = self.deltaX #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
            self.xok = 0
            self.deltaXScreenOffset = 0
            if stickToWallsOnCollision == False:
                self.deltaX = 0
            needToRevert = 1

        #COLLISION CHECK @ A or @ B or @ F or @ E 
        #IF WE HANDLED A COLLISION @ C, D, H, OR G OR NO COLLISION @ C, D, H, OR G OCCURED,
        #WOULD A COLLISION OCCUR @ A, B, F, OR E ??? (NOTE HOW THIS FORMULA IS DEPENDENT ON VARS ABOVE THAT WERE CHANGED!)
        
        #if (self.deltaY < 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y - (self.deltaYScreenOffset + self.speed) + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+self.deltaX + self.deltaXScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y - (self.deltaYScreenOffset + self.speed) + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + (self.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+self.deltaX + self.deltaXScreenOffset)/float(tileWidth)))])) or (self.deltaY > 0 and (thisLevelMap[int(1 + (self.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + (-self.deltaYScreenOffset + self.speed + self.GetNextGravityApplicationToWorld(self.gravityYDelta, self.timeSpentFalling, tileHeight)) + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+self.deltaX + self.deltaXScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (self.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + (-self.deltaYScreenOffset + self.speed + self.GetNextGravityApplicationToWorld(self.gravityYDelta, self.timeSpentFalling, tileHeight)) + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + (self.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+self.deltaX + self.deltaXScreenOffset)/float(tileWidth)))])):
        if (self.deltaY < 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y - (self.deltaYScreenOffset - self.deltaY) + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+self.deltaX + self.deltaXScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y - (self.deltaYScreenOffset - self.deltaY) + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + (self.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+self.deltaX + self.deltaXScreenOffset)/float(tileWidth)))])) or (self.deltaY > 0 and (thisLevelMap[int(1 + (self.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + (-self.deltaYScreenOffset + self.deltaY + self.GetNextGravityApplicationToWorld(self.gravityYDelta, self.timeSpentFalling, tileHeight)) + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+self.deltaX + self.deltaXScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (self.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + (-self.deltaYScreenOffset + self.deltaY + self.GetNextGravityApplicationToWorld(self.gravityYDelta, self.timeSpentFalling, tileHeight)) + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + (self.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+self.deltaX + self.deltaXScreenOffset)/float(tileWidth)))])):
            self.yok = 0
            self.deltaYScreenOffset = 0
            if stickToWallsOnCollision == False:
                self.deltaY = 0
            if gravityAppliesToWorld == True and self.gravityYDelta != 0 and self.deltaY + self.GetNextGravityApplicationToWorld(self.gravityYDelta, self.timeSpentFalling, tileHeight) > 0:
                self.gravityYDelta = 0
                self.timeSpentFalling = 0
                self.deltaY = -1
                
        #RESET 1ST COLLISION CHECK PARAMATERS B/C NOW,
        #WE DON'T KNOW IF A COLLISION @ C or @ D or @ H or @ G WILL OCCUR
        #BECAUSE WE MAY HAVE HANDLED A COLLISION @ A, B, F, OR E.
        #KNOWING THIS BEFOREHAND AFFECTS THE OUTCOME OF COLLISION TEST.
        if needToRevert == 1:
            self.xok = tempxok
            self.deltaXScreenOffset = tempdeltaXScreenOffset
            self.deltaX = temppersonXDelta

        #COLLISION CHECK @ C or @ D or @ H or @ G
        #NOW TEST FOR COLLISION @ C, D, H, OR G NOW KNOWING THAT WE HANDLED MAY HAVE HANDLED A COLLISION @ C, D, H, OR G
        #LIKEWISE, THIS FORMULA IS DEPENDENT ON VARS IN 2ND SECTION THAT CHANGED
        if ((self.deltaX)> 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + self.deltaY + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + (self.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+(-self.deltaXScreenOffset + self.deltaX)+ self.deltaXScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (self.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + self.deltaY + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + (self.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+(-self.deltaXScreenOffset + self.deltaX)+ self.deltaXScreenOffset)/float(tileWidth)))])) or ((self.deltaX)< 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + self.deltaY + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+(-self.deltaXScreenOffset + self.deltaX)+ self.deltaXScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (self.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((self.y + self.deltaY + self.deltaYScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((self.x+(-self.deltaXScreenOffset + self.deltaX)+ self.deltaXScreenOffset)/float(tileWidth)))])):
            self.xok = 0
            self.deltaXScreenOffset = 0
            if stickToWallsOnCollision == False:
                self.deltaX = 0

    def CalculateNextGravityVelocity(self, tileHeight):
        return (min(self.gravityYDelta + (.00005 * (self.timeSpentFalling**2)), tileHeight / 3.0)), self.timeSpentFalling + 1

    def GetNextGravityApplicationToWorld(self, gravityYDelta, timeSpentFalling, tileHeight):
        character = Character("Temp")
        character.gravityYDelta = gravityYDelta
        character.timeSpentFalling = timeSpentFalling
        a, b = self.CalculateNextGravityVelocity(tileHeight)
        del character
        return a

    def DetermineCharPicBasedOnDirectionFacing(self):
        if self.xFacing == 0 and self.yFacing > 0:
            #down
            self.imgDirectionIndex = 0
        if self.xFacing == 0 and self.yFacing < 0:
            #up
            self.imgDirectionIndex = 1
        if self.xFacing > 0 and self.yFacing == 0:
            #right
            self.imgDirectionIndex = 2
        if self.xFacing < 0 and self.yFacing == 0:
            #left
            self.imgDirectionIndex = 3
        if self.xFacing > 0 and self.yFacing > 0:
            #down right
            self.imgDirectionIndex = 4
        if self.xFacing < 0 and self.yFacing < 0:
            #up left
            self.imgDirectionIndex = 5
        if self.xFacing > 0 and self.yFacing < 0:
            #up right
            self.imgDirectionIndex = 6
        if self.xFacing < 0 and self.yFacing > 0:
            #down left
            self.imgDirectionIndex = 7

    def DetermineCharPicBasedOnWalkOrMovement(self, millisecondsSinceLastFrame):
        if self.deltaX == 0 and self.deltaY == 0:
            self.imgLegIndex = 0
            self.millisecondsOnThisLeg = 0
        else:
            if (self.millisecondsOnThisLeg >= self.millisecondsOnEachLeg):
                self.imgLegIndex = (self.imgLegIndex + 1) % self.numberOfFramesAnimPerWalk
                self.millisecondsOnThisLeg = 0
            else:
                self.millisecondsOnThisLeg = self.millisecondsOnThisLeg + millisecondsSinceLastFrame

    def ApplyGravity(self):
        self.deltaY = self.deltaY + self.gravityYDelta

    def Attack(self):
        pass

class Camera(object):
    def __init__(self, screenResSelection, displayType, x, y):
        self.screenResSelection = screenResSelection
        self.displayType = displayType
        self.viewX = x #Camera view X-coord measured in tiles
        self.viewY = y - 1#Camera view Y-coord measured in tiles
        self.viewToScreenPxlOffsetX = 0 #Offset the camera view X-coord to the screen based on player fractional tile Movement, in pixels
        self.viewToScreenPxlOffsetY = 0 #Offset the camera view Y-coord to the screen based on player fractional tile Movement, in pixels
        self.zoom = 1

    def UpdateScreenSettings(self):
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
        #TODO: Resolution/screen size can be larger than the world itself, 
        #   thus the world must be centered for attractive appearance

    def Move(self, tileWidth, tileHeight, deltaX = 0, deltaY = 0):#, deltaZ = 0, deltaZoom = 0):
        self.viewToScreenPxlOffsetY = self.viewToScreenPxlOffsetY - deltaY #Move CAMERA ALONG Y AXIS
        self.viewToScreenPxlOffsetX = self.viewToScreenPxlOffsetX - deltaX #Move CAMERA ALONG X AXIS
        self.RefreshViewCoords(tileWidth, tileHeight)

    def MoveBasedOnCharacterMove(self, character, tileHeight, tileWidth, thisLevelMapWidth, thisLevelMapHeight):

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

        if character.boundToCamera == True:
            #IF CHARACTER IS PRESSING AGAINST BLOCK, BUT OUTSIDE OF MIDDLE 9TH AND CAMERA CAN Move FURTHER BEFORE HITTING THE EDGE OF THE WORLD, THEN Move CAMERA, BUT NOT THE PERSON

            #*UNLESS SCREEN SCROLLING PUTS CAMERA VIEW OUTSIDE OF THE WORLD
            #(IS PLAYER MOVING TO THE LEFT TO LEAVE MIDDLE THIRD AND IS IT NOT THE CASE THAT SCREEN SCROLLING WOULD PLACE THE CAMERA FARTHER LEFT THAN WORLD START)    OR    (IS PLAYER MOVING TO THE RIGHT TO LEAVE MIDDLE THIRD AND IS IT NOT THE CASE THAT SCREEN SCROLLING WOULD PLACE CAMERA FARTHER RIGHT THAN WORLD END)?
            if character.xok == 1 and self.atWorldEdgeX == False: ###and ((character.deltaX < 0 and character.x + character.deltaX < (1*self.displayWidth)/3.0) or (character.deltaX >0 and character.x + character.deltaX > (2*self.displayWidth)/3.0)):
                self.Move(tileWidth, tileHeight, deltaX = character.deltaX) #Move CAMERA ALONG X AXIS
                character.deltaXScreenOffset = -character.deltaX #KEEP PLAYER'S CHARACTER FIXED @ MIDDLE 9TH EDGE
            else:
                character.deltaXScreenOffset = 0

            if character.yok == 1 and self.atWorldEdgeY == False: ###and ((character.deltaY < 0 and character.y + character.deltaY < (1*self.displayHeight)/3.0) or (character.deltaY >0 and character.y + character.deltaY > (2*self.displayHeight)/3.0)):
                self.Move(tileWidth, tileHeight, deltaY = character.deltaY) #Move CAMERA ALONG Y AXIS
                character.deltaYScreenOffset = -character.deltaY #KEEP PLAYER'S CHARACTER FIXED @ MIDDLE 9TH EDGE
            else:
                character.deltaYScreenOffset = 0
        return character

    def RefreshViewCoords(self, tileWidth, tileHeight):
        #CAMERA MoveS IN PIXELS, BUT THE WORLD IS BUILT IN TILES.
        #WHEN SCREEN MoveS IN PIXELS WITH USER'S MoveMENT, THIS
        #IS STORED IN cameraViewToScreenPxlOffsetX/Y. BUT IF USER'S
        #MoveMENT (AND THEREFORE, cameraViewToScreenPxlOffsetX/Y) GOES BEYOND
        #THE SIZE OF A TILE, THEN TAKE AWAY THE TILE SIZE FROM THE 
        #cameraViewToScreenPxlOffsetX/Y, AND CONSIDER THAT THE CAMERA HAS MoveD
        #1 TILE IN DISTANCE IN THE WORLD. THIS IS IMPORTANT IN
        #ACCURATELY TRACKING THE CAMERA'S LOCATION COORDINATES.
        if self.viewToScreenPxlOffsetX >= tileWidth:
            self.viewToScreenPxlOffsetX = self.viewToScreenPxlOffsetX - tileWidth
            self.viewX = self.viewX - 1
            
        elif self.viewToScreenPxlOffsetX <0:
            self.viewToScreenPxlOffsetX = self.viewToScreenPxlOffsetX + tileWidth
            self.viewX = self.viewX + 1

        if self.viewToScreenPxlOffsetY >= tileHeight:
            self.viewToScreenPxlOffsetY = self.viewToScreenPxlOffsetY - tileHeight
            self.viewY = self.viewY - 1

        elif self.viewToScreenPxlOffsetY <0:
            self.viewToScreenPxlOffsetY = self.viewToScreenPxlOffsetY + tileHeight
            self.viewY = self.viewY + 1

    def GetLocationInWorld(self, tileHeight, tileWidth):
        return [1 + self.viewX - (self.viewToScreenPxlOffsetX/float(tileWidth)), 1 + self.viewY - (self.viewToScreenPxlOffsetY/float(tileHeight))]

    def SetLocationInWorld(self, x, y, tileHeight, tileWidth):
        pass
        #self.viewX = (self.viewToScreenPxlOffsetX/float(tileWidth)) + x - 1
        #self.viewY = (self.viewToScreenPxlOffsetY/float(tileHeight)) + y - 1

    def ValidatePosition(self, gameDisplay):
        #CAN'T BE BEYOND WORLD EDGES
            #WHAT IF CAMERA VIEW IS LARGER THAN WORLD SIZE?
        #CAN'T PUT USER CHARACTER OUTSIDE OF INNER NINTH IF CAMERA CAN Move CLOSER TO WORLD EDGE
        pass

    def TestIfAtWorldEdgeCollision(self, thisLevelMap, character, tileWidth, tileHeight, LEFrame):
        #SNAP CAMERA TO THE EDGE OF THE WORLD IF PAST IT
#        self.atWorldEdgeX = False
#        self.atWorldEdgeY = False
#            #camera X  +      tiles on screen              +        frac. person next Move         +   frac camera X                                         
#        if (1 + self.viewX + (self.displayWidth/float(tileWidth)) + (character.deltaX/float(tileWidth)) - (self.viewToScreenPxlOffsetX/float(tileWidth)) >= len(thisLevelMap[0])) and character.deltaX > 0:
#            self.viewToScreenPxlOffsetX = (float(float(self.displayWidth/float(tileWidth)) - int(self.displayWidth/float(tileWidth))))*tileWidth
#            self.viewX = int(len(thisLevelMap[0]) - int(self.displayWidth/float(tileWidth))) - 1
#            self.atWorldEdgeX = True
#        else:
#            if (1 + self.viewX - self.viewToScreenPxlOffsetX/float(tileWidth) + (character.deltaX/float(tileWidth)) <= 0 and character.deltaX <0):
#                self.viewX = -1
#                self.viewToScreenPxlOffsetX = 0
#                self.atWorldEdgeX = True
#        
#        if (1 + self.viewY + (self.displayHeight/float(tileHeight)) + (character.deltaY/float(tileHeight)) - (self.viewToScreenPxlOffsetY/float(tileHeight)) >= len(thisLevelMap)) and character.deltaY > 0:
#            self.viewToScreenPxlOffsetY = (float(float(self.displayHeight/float(tileHeight)) - int(self.displayHeight/float(tileHeight))))*tileHeight
#            self.viewY = int(len(thisLevelMap) - int(self.displayHeight/float(tileHeight))) - 1
#            self.atWorldEdgeY = True
#        else:
#            if (1 + self.viewY - self.viewToScreenPxlOffsetY/float(tileHeight) + (character.deltaY/float(tileHeight)) <= 0 and character.deltaY < 0):
#                self.viewY = -1
#                self.viewToScreenPxlOffsetY = 0
#                self.atWorldEdgeY = True
        self.atWorldEdgeX = False
        self.atWorldEdgeY = False
            #camera X  +      tiles on screen              +        frac. person next Move         +   frac camera X                                         
        if (self.viewX + (self.displayWidth/float(tileWidth)) + (character.deltaX/float(tileWidth)) - LEFrame.frameWidth - (self.viewToScreenPxlOffsetX/float(tileWidth)) >= len(thisLevelMap[0])) and character.deltaX > 0:
            self.viewToScreenPxlOffsetX = (float(float(self.displayWidth/float(tileWidth)) - int(self.displayWidth/float(tileWidth))))*tileWidth
            self.viewX = int(len(thisLevelMap[0]) + LEFrame.frameWidth - int(self.displayWidth/float(tileWidth)))
            self.atWorldEdgeX = True
        else:
            if (self.viewX - self.viewToScreenPxlOffsetX/float(tileWidth) + (character.deltaX/float(tileWidth)) <= -1 and character.deltaX <0):
                self.viewX = -1
                self.viewToScreenPxlOffsetX = 0
                self.atWorldEdgeX = True
        
        if (self.viewY + (self.displayHeight/float(tileHeight)) + (character.deltaY/float(tileHeight)) - (self.viewToScreenPxlOffsetY/float(tileHeight)) + 1 >= len(thisLevelMap)) and character.deltaY > 0:
            self.viewToScreenPxlOffsetY = (float(float(self.displayHeight/float(tileHeight)) - int(self.displayHeight/float(tileHeight))))*tileHeight
            self.viewY = int(len(thisLevelMap) - int(self.displayHeight/float(tileHeight))) - 1
            self.atWorldEdgeY = True
        else:
            if (self.viewY - self.viewToScreenPxlOffsetY/float(tileHeight) + (character.deltaY/float(tileHeight)) <= -1 and character.deltaY < 0):
                self.viewY = -1
                self.viewToScreenPxlOffsetY = 0
                self.atWorldEdgeY = True


class Mouse(object):
    def __init__(self):
        self.coords = (0,0)
        self.btn = (0,0,0)
        self.xTile = 0
        self.yTile = 0
        self.blockWidth = 0
        self.blockHeight = 0

class Level(object):
    def __init__(self, index, name, description, weather, sideScroller, wallMap, objectMap, music, loopMusic, startX, startY, startXFacing, startYFacing, xSize, ySize, gravity, stickToWallsOnCollision, tileSheetRows, tileSheetColumns, tileWidth, tileHeight, tileXPadding, tileYPadding):
        self.index = index
        self.name = name
        self.description = description
        self.weather = weather
        self.sideScroller = sideScroller
        self.wallMap = wallMap
        self.objectMap = objectMap
        self.music = music
        self.loopMusic = loopMusic
        self.startX = startX
        self.startY = startY
        self.startXFacing = startXFacing
        self.startYFacing = startYFacing
        self.gravity = gravity
        self.stickToWallsOnCollision = stickToWallsOnCollision
        self.levelHeight = len(objectMap)
        self.levelWidth = len(objectMap[0])

        self.tileSheetRows = 9
        self.tileSheetColumns = 1
        self.tileWidth = 64
        self.tileHeight = 64
        self.tileXPadding = 0
        self.tileYPadding = 0

class World(object):
    def __init__(self, filePath, fileName):
        self.filePath = filePath
        self.fileName = fileName

    def Reset(self):
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute("DROP TABLE IF EXISTS WALLMAPS")
        c.execute("DROP TABLE IF EXISTS OBJECTMAPS")
        c.execute("CREATE TABLE WALLMAPS(IndexPK INT, Map TEXT")
        c.execute("CREATE TABLE LEVELDATA(IndexPK INT, Name TEXT, Description TEXT, Weather TEXT, SideScroller BOOL")
        c.execute("CREATE TABLE OBJECTMAPS(IndexPK INT, Map TEXT")
        connection.commit()
        connection.close()
        
    def GetNumberOfLevels(self):
        pass

    def AddLevel(self, index, level):
        #INSERT BLANK INTO DATABASE
        self.UpdateLevel(index, level)

    def RemoveLevel(self, index):
        pass

    def GetLevel(self, index):                     
        return Level(index, name, description, weather, sideScroller, wallMap, objectMap, music, loopMusic, startX, startY, startXFacing, startYFacing, xSize, ySize, gravity, stickToWallsOnCollision, tileSheetRows, tileSheetColumns, tileWidth, tileHeight, tileXPadding, tileYPadding)

    def UpdateWorldWithLevel(self, index, level):
        index
        name
        description
        weather
        sideScroller
        wallMap
        objectMap
        music
        loopMusic
        startX = 22
        startY = 2
        startXFacing = 0
        startYFacing = 1
        gravity = False
        stickToWallsOnCollision = False
        tileSheetRows
        tileSheetColumns
        tileWidth
        tileHeight
        tileXPadding
        tileYPadding
    
class Game(object):
    def __init__(self, screenResSelection, fullScreen):        
        self.currentLevel = Level(0, "Demo", "This is a demonstration level", "Clear", False, [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
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
                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]], [[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[], WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, touchAction = 0, attackAction = 0, time = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThrough = True),[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, touchAction = 0, attackAction = 0, time = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThrough = True),[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, touchAction = 0, attackAction = 0, time = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThrough = True),[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, touchAction = 0, attackAction = 0, time = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThrough = True),[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, touchAction = 0, attackAction = 0, time = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThrough = True),[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]], "", True, 22, 2, 1, 0, 0, 0, False, False, 9, 1, 64, 64, 0, 0)

        self.clock = pygame.time.Clock()
        self.userMouse = Mouse()
        self.logic = LogicHandler()
        self.gfx = GfxHandler()
                
        pygame.display.set_caption("2D Game Framework")
        
        self.lastTick = 0
        self.timeElapsedSinceLastFrame = 0

        self.exiting = False
        self.paused = False
        self.lost = False
        self.difficultySelection = 0
        self.enterPressed = False
        
        #WORLD OBJECTS ARE STORED IN AN ARRAY THAT REPRESENTS X, Y COORDINATES OF THE LEVEL. LOCATIONS WITH NO WORLD OBJECTS ARE EMPTY.
        #THIS METHOD IS PREFERRED TO STORING AN ARRAY OF OBJECTS EACH CONTAINING AN X, Y PROPERTY BECAUSE THIS WAY ALLOWS MORE CODE REUSE,
        #AND ONLY ITERATING OVER SECTION OF THE LEVEL THAT IS VISIBLE TO THE CAMERA'S POINT OF VIEW, RATHER THAN ITERATING OVER EACH
        #LEVEL OBJECT AND TESTING IF ITS X, Y COORDINATES FALL WITHIN THE CAMERA'S POINT OF VIEW.
        self.particles = []

        self.camera = Camera(screenResSelection, fullScreen, 14, 0)
        self.gameDisplay = self.camera.UpdateScreenSettings()
        
        self.mouseWidth = self.currentLevel.tileWidth
        self.personHeight = self.currentLevel.tileHeight
        self.gfx.LoadGfxDictionary("../Images/spritesheet.png", "World Tiles", self.currentLevel.tileSheetRows, self.currentLevel.tileSheetColumns, self.currentLevel.tileWidth, self.currentLevel.tileHeight, self.currentLevel.tileXPadding, self.currentLevel.tileYPadding)
        self.userCharacter = Character(name = "User", boundToCamera = True, xFacing = self.currentLevel.startXFacing, yFacing = self.currentLevel.startYFacing, xTile = self.currentLevel.startX, yTile = self.currentLevel.startY, deltaX = 0, deltaY = 0) #particles: [NAME, X1, Y1, DX, DY, R, G, B, SPEED, 0])
        self.userCharacter.InitializeScreenPosition(self.camera, self.currentLevel.tileWidth, self.currentLevel.tileHeight)
        for i in xrange (4):
            self.userCharacter.weapons.append(Weapon(str(i), (i+1) * 10, 1000, 2, 16, 16, (i+1)/float(100)))
        self.characters = [self.userCharacter]
        ###for character in self.characters:
            ###self.gfx.LoadGfxDictionary(character.imagesGFXName, character.imagesGFXNameDesc, character.numberOfDirectionsFacingToDisplay, character.numberOfFramesAnimPerWalk, character.width, character.height, 0, 0)
        self.gfx.LoadGfxDictionary("../Images/bullets.png", "Particles", 4, 1, 16, 16, 0, 0)
        self.gfx.LoadGfxDictionary("../Images/world objects.png", "World Objects", 4, 4, 16, 16, 0, 0)
        self.gfx.LoadGfxDictionary("../Images/level editor frame.png", "Level Editor Frame", 2, 4, self.mouseWidth, self.personHeight, 0, 0)
        self.displayFrame = LevelEditorFrame(self.gfx, self.camera, self.currentLevel.tileHeight, self.currentLevel.tileWidth)
        self.FPSLimit = 200
        
    def ShowMenu(self, displayMenu, camera):
        menuSystem = MenuScreen(displayMenu, self.camera.screenResSelection , self.difficultySelection, self.camera.displayType, self.gameDisplay)
        self.difficultySelection, self.camera.screenResSelection, self.camera.displayType, self.exiting = menuSystem.DisplayMenuScreenAndHandleUserInput()
        self.paused = False
        del menuSystem
        self.camera.UpdateScreenSettings()

    def Play(self):
        # GAME LOOP
        while not self.paused:
            #HANDLE KEY PRESSES AND PYGAME EVENTS
            self.paused, self.lost, self.userCharacter, self.enterPressed, self.userMouse.coords, self.userMouse.btn, self.savePressed = self.logic.HandleHeyPressAndGameEvents(self.paused, self.lost, self.userCharacter)
            #Select the correct image for all characters based on direction facing
            self.userCharacter.DetermineCharPicBasedOnDirectionFacing()
            #Select the correct image for all characters based on what leg they are standing on
            self.userCharacter.DetermineCharPicBasedOnWalkOrMovement(self.timeElapsedSinceLastFrame)
            #FIGURE OUT HOW MUCH TIME HAS ELAPSED SINCE LAST FRAME WAS DRAWN
            self.timeElapsedSinceLastFrame = self.logic.ManageTimeAndFrameRate(self.lastTick, self.clock, self.FPSLimit)
            #NOW THAT KEY PRESSES HAVE BEEN HANDLED, ADJUST THE SPEED OF EVERYTHING BASED ON HOW MUCH TIME ELAPSED SINCE LAST FRAME DRAW, AND PREVENT DIAGONAL SPEED UP ISSUE
            self.particles, self.userCharacter = self.logic.AdjustSpeedBasedOnFrameRate(self.timeElapsedSinceLastFrame, self.particles, self.userCharacter)

            self.camera.TestIfAtWorldEdgeCollision(self.currentLevel.wallMap, self.userCharacter, self.currentLevel.tileWidth, self.currentLevel.tileHeight, self.displayFrame)
            self.userCharacter.ApplyGravity()
            #CHECK FOR CHARACTER-WALL COLLISIONS
            ###self.userCharacter.UpdateDirectionBasedOnWallCollisionTest(self.currentLevel.wallMap, self.camera, self.tileHeight, self.tileWidth, self.currentLevel.gravity, self.currentLevel.stickToWallsOnCollision)
            #ADJUST DIAGONAL SPEED IF USER PRESSES 2 ARROW KEYS
            self.userCharacter.deltaX, self.userCharacter.deltaY = self.logic.FixDiagSpeed(self.userCharacter.deltaX, self.userCharacter.deltaY, self.userCharacter.speed)

            #TODO: generateBadGuys()
            #TODO: badGuysMoveOrAttack()
            
            #TEST IF USER CHARACTER MoveS OUTSIDE OF INNER NINTH OF SCREEN
            self.userCharacter = self.camera.MoveBasedOnCharacterMove(self.userCharacter, self.currentLevel.tileHeight, self.currentLevel.tileWidth, self.currentLevel.levelWidth, self.currentLevel.levelHeight)
            #Move THE USER CHARACTER IN THE WORLD, AND ON THE SCREEN
            self.userCharacter.Move(self.camera, self.currentLevel.tileWidth, self.currentLevel.tileHeight, self.userCharacter.deltaX, self.userCharacter.deltaY)

            #I THINK I NEED TO DELETE THIS
            ###if self.currentLevel.gravity == True:
            ###    self.userCharacter.gravityYDelta, self.userCharacter.timeSpentFalling = self.userCharacter.CalculateNextGravityVelocity(self.currentLevel.tileHeight)

            #Move PARTICLES
            self.particles = self.logic.MoveParticlesAndHandleParticleCollision(self.particles, self.currentLevel.wallMap)
            #GENERATE PARTICLES
            self.particles, self.userCharacter = self.logic.GenerateParticles(self.particles, self.userCharacter, self.currentLevel.tileHeight, self.currentLevel.tileWidth, self.gfx)# (self.bullets, rain drops, snowflakes, etc...)
            #DRAW THE WORLD IN TILES BASED ON THE THE NUMBERS IN THE thisLevelMap ARRAY
            self.gfx.DrawWorldInCameraView("World Tiles", self.camera, self.currentLevel.tileWidth, self.currentLevel.tileHeight, self.currentLevel.wallMap, self.gameDisplay)
            #DRAW THE WORLD IN OBJECTS BASED ON THE THE NUMBERS IN THE self.thisLevelObjects ARRAY
            self.currentLevel.objectMap = self.gfx.DrawWorldInCameraView("World Objects", self.camera, self.currentLevel.tileWidth, self.currentLevel.tileHeight, self.currentLevel.objectMap, self.gameDisplay, self.timeElapsedSinceLastFrame)
            #DRAW PEOPLE, ENEMIES, OBJECTS AND PARTICLES
            ###self.gfx.DrawObjectsAndParticles(self.particles, self.gameDisplay, self.camera, self.tileHeight, self.tileWidth, self.userCharacter)

            #DRAW THE LEVEL EDITOR FRAME AND FRAME OBJECTS
            self.displayFrame.DrawLevelEditorFrame(self.camera, self.currentLevel.tileWidth, self.currentLevel.tileHeight, self.currentLevel.wallMap, self.gfx, self.gameDisplay)
            self.displayFrame.DrawTileAndObjectPalette(self.camera, self.currentLevel.tileWidth, self.currentLevel.tileHeight, self.gfx, self.gameDisplay)
            #CONVERT MOUSE COORDS -> WORLD TILES
            self.userMouse.xTile, self.userMouse.yTile = self.gfx.ConvertScreenCoordsToTileCoords(self.userMouse.coords, self.camera, self.currentLevel.tileWidth, self.currentLevel.tileHeight)

            self.displayFrame, self.currentLevel.wallMap = self.logic.HandleMouseEvents(self.userMouse, self.camera, self.displayFrame, self.currentLevel.tileWidth, self.currentLevel.tileHeight, self.currentLevel.wallMap, self.gfx)
            
            #DRAW GAME STATS
            #self.gfx.DrawSmallMessage("Health: " + str(self.myHealth), 0, self.gameDisplay, white, self.displayWidth)
            #self.gfx.DrawSmallMessage("Ammo: " + str(self.userCharacter.ammo), 1, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.DrawSmallMessage("Level: " + str(self.currentLevel), 2, self.gameDisplay, white, self.displayWidth)
            #self.gfx.DrawSmallMessage("Score: " + str(self.score), 3, self.gameDisplay, white, self.displayWidth)
            #self.gfx.DrawSmallMessage("Player wX: " + str(self.userCharacter.GetLocationInWorld()[0]), 4, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.DrawSmallMessage("Player wY: " + str(self.userCharacter.GetLocationInWorld()[1]), 5, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.DrawSmallMessage("Player sX: " + str(self.userCharacter.GetLocationOnScreen()[0]), 6, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.DrawSmallMessage("Player sY: " + str(self.userCharacter.GetLocationOnScreen()[1]), 7, self.gameDisplay, white, self.camera.displayWidth)

            ##self.gfx.DrawSmallMessage("X Offset: " + str(self.camera.viewToScreenPxlOffsetX), 6, self.gameDisplay, white, self.camera.displayWidth)
            ##self.gfx.DrawSmallMessage("Y Offset: " + str(self.camera.viewToScreenPxlOffsetY), 7, self.gameDisplay, white, self.camera.displayWidth)
            
            #self.gfx.DrawSmallMessage("Cam X: " + str(self.camera.GetLocationInWorld(self.tileWidth, self.tileHeight)[0]), 8, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.DrawSmallMessage("Cam Y: " + str(self.camera.GetLocationInWorld(self.tileWidth, self.tileHeight)[1]), 9, self.gameDisplay, white, self.camera.displayWidth)
            self.gfx.DrawSmallMessage("FPS: " + str(1000/max(1, self.timeElapsedSinceLastFrame)), 12, self.gameDisplay, white, self.camera.displayWidth)
            pygame.display.update()
            if self.userCharacter.health <= 0:
                self.lost = True
                #self.exiting = True
                self.gfx.DrawLargeMessage("YOU LOSE", self.gameDisplay, white)
                self.gameDisplay.fill(black)
                self.gfx.DrawLargeMessage(str(self.score) + " pts", self.gameDisplay, white)

        #OUT OF THE GAME LOOP
        if self.lost == True:
            #LOST GAME ACTION HERE
            pass
            del self.clock
        else:
            pass

class WorldEditorWindow(wx.Frame):
    def __init__(self, parent, title, windowWidth, windowHeight):
        super(Frame, self).__init__(parent, title=title, 
            size=(windowWidth, windowHeight), style=wx.NO_BORDER)# | wx.STAY_ON_TOP)
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        #Create a menu bar
        self.menuBar = wx.MenuBar()
        
        #Create a File submenu
        self.fileButton = wx.Menu()

        #Create submenu items
        self.openItem = wx.MenuItem(self.fileButton, wx.ID_OPEN, "Open\tCtrl+O")
        self.saveItem = wx.MenuItem(self.fileButton, wx.ID_SAVE, "Save\tCtrl+S")
        self.exitItem = wx.MenuItem(self.fileButton, wx.ID_EXIT, "Save\tCtrl+Q")
        #attach submenu items to the submenu
        self.fileButton.AppendItem(self.openItem)
        self.fileButton.AppendItem(self.saveItem)
        self.fileButton.AppendItem(self.exitItem)
        #Attach the submenu to the menu bar
        self.menuBar.Append(self.fileButton, "&File")

        #Create a Global Options submenu
        self.globalOptionsButton = wx.Menu()
        
        #Create submenu items
        #self.menuItem = wx.MenuItem(self.globalOptionsButton, wx.ID_XXXXX, "Menu Item Text")
        
        #attach submenu items to the submenu
        #self.globalOptionsButton.AppendItem(self.menuItem)
        
        #Attach the submenu to the menu bar
        self.menuBar.Append(self.globalOptionsButton, "&Global Game Options")


pygame.init()
allResolutionsAvail = pygame.display.list_modes()
#ADD IN GAME-SPECIFIC LOGIC IF CERTAIN RESOLUTIONS ARE TO BE EXCLUDED FROM USER SELECTION
screenResChoices = allResolutionsAvail
del allResolutionsAvail
screenResChoices.sort()
exiting = False
while exiting == False:
    myGame = Game(int(len(screenResChoices)/2), "Window")
    
    exiting = myGame.ShowMenu("Main Menu", myGame.camera)
    while myGame.exiting == False and myGame.lost == False:
        myGame.Play()
        myGame.ShowMenu("Paused", myGame.camera)
        #menuSystem = menuScreen("Main Menu", screenResSelection, difficultySelection, displayType)
        #del menuSystem
del myGame
pygame.quit()
quit()
