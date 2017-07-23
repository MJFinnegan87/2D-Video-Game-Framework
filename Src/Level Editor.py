import pygame
import time
import random
import sys,os
import math
import sqlite3
import wx
import json
import copy
from io import StringIO as StringIO

#Python 2.7
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
PI = math.pi

pygame.init()
allResolutionsAvail = pygame.display.list_modes()
#ADD IN GAME-SPECIFIC LOGIC IF CERTAIN RESOLUTIONS ARE TO BE EXCLUDED FROM USER SELECTION
screenResChoices = allResolutionsAvail
del allResolutionsAvail
screenResChoices.sort()

class JSONConverter(json.JSONEncoder):
    def toJSON(self, data):
        return json.dumps(data, default = lambda o: o.__dict__, sort_keys=True, indent = 4)

    def fromJSON(self, data, dataType):
        retData = json.loads(data)
        if type(retData) == dict:
            if dataType == "WallData":
                return WallObject(**retData)
            elif dataType == "ObjectData":
                return WorldObject(**retData)
        else:
            return retData
    
class GfxHandler(object):
    def __init__(self):
        self.gfxDictionary = {}

    def LoadGfxDictionary(self, file_name="", imageIndicator="", rows=0, columns=0, width=0, height=0, pictureXPadding=0, pictureYPadding=0):
        self.spriteSheet = pygame.image.load(file_name)
        imgTransparency = True
        
        if imageIndicator == "World Tiles":
            imgTransparency = False
        self.gfxDictionary.update({imageIndicator:{}}) #NESTED HASHTABLE

        for j in range(rows):
            for k in range(columns):
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
        #return (int((tileRequested%gfxHandlerColumns)*tileWidth)+(int(tileRequested%gfxHandlerColumns))*pictureXPadding,
        #        int((tileRequested/gfxHandlerColumns)*tileHeight)+(int(tileRequested/gfxHandlerColumns))*pictureYPadding,
        #        tileWidth,
        #        tileHeight)
        return (tileRequested - (int(tileRequested/gfxHandlerColumns) * gfxHandlerColumns)) * (tileWidth + pictureXPadding), int(tileRequested/gfxHandlerColumns) * (tileHeight + pictureYPadding),  tileWidth, tileHeight

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

##    def DrawDialogs(self, conversationArray, (backR, backG, backB, backA), (foreR, foreG, foreB, foreA), (borderR, borderG, borderB, borderA), borderSize = 5):
##        conversationSelections = []
##        return conversationSelections

    def DrawObjectsAndParticles(self, particles, gameDisplay, camera, tileHeight, tileWidth, character):
        self.DrawImg(self.gfxDictionary[character.imagesGFXNameDesc][character.imgDirectionIndex+(character.numberOfDirectionsFacingToDisplay*character.imgLegIndex)], (character.x, character.y), gameDisplay)
        for i in range(len(particles)):
            if particles[i].name == "User Bullet":
                #print "x: " + str((1 + cameraViewX + (-cameraViewToScreenPxlOffsetX/float(tileWidth)) - particles[i][2]) * -tileWidth)
                #print "y: " + str((1 + cameraViewY + (-cameraViewToScreenPxlOffsetY/float(tileHeight)) - particles[i][3]) * -tileHeight)
                if ((1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particles[i].xTile) * -tileWidth) + particles[i].width > 0 and (1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particles[i].xTile) * -tileWidth < camera.displayWidth:
                    #self.drawObject("bullet" + str(particles[i][1]) + ".png", (1 + cameraViewX + (-cameraViewToScreenPxlOffsetX/float(tileWidth)) - particles[i][2]) * -tileWidth, (1 + cameraViewY + (-cameraViewToScreenPxlOffsetY/float(tileHeight)) - particles[i][3]) * -tileHeight, gameDisplay)
                    #print math.acos(particles[i][4]/float((particles[i][4]**2 + particles[i][5]**2)**.5))
                    #img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][particles[i][1]], (180*math.acos(particles[i][4]/float((particles[i][4]**2 + particles[i][5]**2)**.5)))/PI)
                    self.DrawImg(particles[i].img, ((1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particles[i].xTile) * -tileWidth, (1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) - particles[i].yTile) * -tileHeight), gameDisplay)

    def DrawWorldInCameraView(self, tileSet, camera, tileWidth, tileHeight, thisLevelMap, gameDisplay, timeElapsedSinceLastFrame=0):
        for i in range(int(camera.displayWidth/float(tileWidth))+2):
            for j in range(int(camera.displayHeight/float(tileHeight))+2):
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
        if thisLevelMap[j+viewY][i+viewX] != None:
            if tileSet == "World Tiles":
                imgToDraw = self.gfxDictionary[tileSet][thisLevelMap[j+viewY][i+viewX].activeImage]
            elif tileSet == "World Objects":
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
    def __init__(self, gfx, camera, tileHeight, tileWidth, objectType, objectColumns, objects, resChangeOnly=False):
        self.objectType = objectType
        self.paletteY = 3
        self.paletteX = 1
        self.objects = objects
        self.frameHeight = int(camera.displayHeight/float(tileHeight))
        self.frameWidth = int(2 + math.ceil(len(gfx.gfxDictionary["World Tiles"])/float(self.frameHeight-self.paletteY)))
        self.objectColumns = objectColumns

        if resChangeOnly == False:
            self.paletteSelectL = self.objects[objectType][0].activeImage
            self.paletteSelectR = self.objects[objectType][0].activeImage
        #self.numberOfWorldTiles = len(gfx.gfxDictionary[objectType])
        self.numberOfWorldTiles = len(objects[objectType])
        
    def DrawLevelEditorFrame(self, camera, tileWidth, tileHeight, thisLevelMap, gfx, gameDisplay):
        for i in range(int(camera.displayWidth/float(tileWidth))-self.frameWidth, int(camera.displayWidth/float(tileWidth))+(self.frameWidth-1)):
            for j in range(int(camera.displayHeight/float(tileHeight))+2):
              gfx.DrawImg(gfx.gfxDictionary["Level Editor Frame"][1],
                          (((i-1)*tileWidth),
                          ((j-1)*tileHeight),
                          (((i-1)*tileWidth))+ tileWidth,
                          (((j-1)*tileHeight)) + tileHeight), gameDisplay)
    def DrawTextUI(self):
        pass

    def DrawTileAndObjectPalette(self, camera, tileWidth, tileHeight, gfx, gameDisplay, objectType):
        if self.objectType == "World Objects":
            multiplier = self.objectColumns
        else:
            multiplier = 1
        for eachPaletteSelector in range(2): #FOR EACH LEFT AND RIGHT SELECTOR
            if eachPaletteSelector == 0:
                thisPaletteSelector = self.paletteSelectL
            elif eachPaletteSelector == 1:
                thisPaletteSelector = self.paletteSelectR
            #gfx.DrawImg(gfx.gfxDictionary[objectType][thisPaletteSelector], #PALLET STATIC
            gfx.DrawImg(gfx.gfxDictionary[objectType][self.objects[objectType][thisPaletteSelector].activeImage], #PALLET ANIMATED
                          ((int(camera.displayWidth/float(tileWidth))-self.frameWidth + eachPaletteSelector)*tileWidth,
                          (1)*tileHeight,
                          (int(camera.displayWidth/float(tileWidth))-self.frameWidth + eachPaletteSelector)*tileWidth,
                          (2) * tileHeight), gameDisplay)
        j = 1
        #print(vars(self.objects[objectType][0]))
        #for i in range(int(len(gfx.gfxDictionary[objectType])/multiplier)):
        for i in range(len(self.objects[objectType])):
            if (int(i/float(j))+self.paletteY) >= self.frameHeight:
                j = j + 1
            gfx.DrawImg(gfx.gfxDictionary[objectType][self.objects[objectType][i].activeImage],
                          ((int(camera.displayWidth/float(tileWidth))-self.frameWidth + (j-1) + self.paletteX - 1)*tileWidth,
                          ((i%(self.frameHeight - self.paletteY))+self.paletteY)*tileHeight,
                          (int(camera.displayWidth/float(tileWidth))-self.frameWidth + (j-1) + self.paletteX - 1)*tileWidth,
                          ((i%(self.frameHeight - self.paletteY))+self.paletteY) + tileHeight), gameDisplay)

    def PaletteItemSelect(self, userMouse, camera, tileWidth, tileHeight, gfx, objectType):
        if userMouse.btn[0] == 1:
            #self.paletteSelectL = int(((camera.displayWidth - userMouse.coords[0])/float(tileWidth) - int(int(camera.displayWidth/float(tileWidth)) - (self.frameWidth + self.paletteX - 1)*tileWidth))*(self.frameHeight - self.paletteY)) + int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))
            #self.paletteSelectL = int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))
            #self.paletteSelectL = int()
            #print str(int((userMouse.coords[0] - (self.paletteX * tileWidth))/float(tileWidth)) - (int(camera.displayWidth/float(tileWidth)) - self.frameWidth) + 1)
            if ((int((userMouse.coords[0] - (self.paletteX * tileWidth))/float(tileWidth)) - (int(camera.displayWidth/float(tileWidth)) - self.frameWidth) + 1) * int(self.frameHeight - self.paletteY)) + int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight)) < len(self.objects[objectType]):
                self.paletteSelectL = ((int((userMouse.coords[0] - (self.paletteX * tileWidth))/float(tileWidth)) - (int(camera.displayWidth/float(tileWidth)) - self.frameWidth) + 1) * int(self.frameHeight - self.paletteY)) + int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))
                print("YOU SELECTED OBJECT: " +str(self.paletteSelectL))
                #print(str(self.paletteSelectL))
        if userMouse.btn[2] == 1:
            #self.paletteSelectR = int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))
            if ((int((userMouse.coords[0] - (self.paletteX * tileWidth))/float(tileWidth)) - (int(camera.displayWidth/float(tileWidth)) - self.frameWidth) + 1) * int(self.frameHeight - self.paletteY)) + int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight)) < len(self.objects[objectType]):
                self.paletteSelectR = ((int((userMouse.coords[0] - (self.paletteX * tileWidth))/float(tileWidth)) - (int(camera.displayWidth/float(tileWidth)) - self.frameWidth) + 1) * int(self.frameHeight - self.paletteY)) + int((userMouse.coords[1] - (self.paletteY * tileHeight))/float(tileHeight))

class LogicHandler(object):
    def HandleMouseEvents(self, userMouse, camera, displayFrame, tileWidth, tileHeight, wallMap, objectMap, gfx, objectType, wallObjects, worldObjects):
        self.displayFrame = displayFrame
        if userMouse.btn[0] == 1 or userMouse.btn[2] == 1:
            if (userMouse.coords[0] >= (int(camera.displayWidth/float(tileWidth)) - self.displayFrame.frameWidth + self.displayFrame.paletteX - 1)*tileWidth) and userMouse.coords[1] >= self.displayFrame.paletteY * tileHeight + 1:
            #and (userMouse.coords[0] <= (int(camera.displayWidth/float(tileWidth)) - self.displayFrame.frameWidth + self.displayFrame.paletteX - 1)*tileWidth + tileWidth)
                self.displayFrame.PaletteItemSelect(userMouse, camera, tileWidth, tileHeight, gfx, objectType)
            else:
                wallMap, objectMap = self.EditLevel(userMouse, displayFrame.paletteSelectL, displayFrame.paletteSelectR, wallMap, objectMap, wallObjects, worldObjects, objectType)
        return self.displayFrame, wallMap, objectMap

    def EditLevel(self, userMouse, paletteSelectL, paletteSelectR, wallMap, objectMap, wallObjects, worldObjects, objectType):
        if userMouse.btn[2] == 1:
            if objectType == "World Tiles":
                wallMap[userMouse.yTile][userMouse.xTile] = copy.deepcopy(wallObjects[paletteSelectR])
            elif objectType == "World Objects":
                objectMap[userMouse.yTile][userMouse.xTile] = copy.deepcopy(worldObjects[paletteSelectR])
        if userMouse.btn[0] == 1:
            if objectType == "World Tiles":
                wallMap[userMouse.yTile][userMouse.xTile] = copy.deepcopy(wallObjects[paletteSelectL])
            elif objectType == "World Objects":
                objectMap[userMouse.yTile][userMouse.xTile] = copy.deepcopy(worldObjects[paletteSelectL])
        #print(str(wallObjects[paletteSelectL].PK))
        #print(str(wallObjects[paletteSelectL].ID))
        #print(str(wallObjects[paletteSelectL].activeImage))
        #print(str(wallObjects[paletteSelectL].walkThroughPossible))
        #print('LEVEL EDITED: ' + str(paletteSelectL))
        return wallMap, objectMap
    
    def HandleHeyPressAndGameEvents(self, exiting, lost, character, world, objectType):
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
                if event.key == pygame.K_a and world != None:
                    world.AddLevel()
                if event.key == pygame.K_s and world != None:
                    world.SaveActiveLevel()
                    world.SaveWallObjects(world.wallObjects)
                    world.SaveWorldObjects(world.worldObjects)
                                          
                if event.key == 280 and world != None:
                    world.LoadLevel(world.activeLevel.index + 1)
                if event.key == 281 and world != None:
                    world.LoadLevel(world.activeLevel.index - 1)
                if event.key == 100 and world != None:
                    world.RemoveLevel(world.activeLevel.index)
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
                if event.key == pygame.K_o and objectType != "World Tiles":
                    objectType = "World Tiles"
                elif event.key == pygame.K_o and objectType == "World Tiles":
                    objectType = "World Objects"
            
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
        return exiting, lost, character, enterPressed, mouseCoords, mouseBtn, savePressed, objectType

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
        for i in range(len(particles)):
            if particles[i].xTile + particles[i].dx > len(thisLevelMap[0]) or particles[i].yTile + particles[i].dy > len(thisLevelMap) or particles[i].xTile + particles[i].dx < 0 or particles[i].yTile + particles[i].dy < 0:
                myDeletedParticles.append(i)
            else:
                particles[i].xTile = particles[i].xTile + particles[i].dx
                particles[i].yTile = particles[i].yTile + particles[i].dy
        for i in range(len(myDeletedParticles)):
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
        for i in range(len(particleList)):
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
        #self.world.activeLevel, self.activeWeapon, self.enemiesAlive, self.myEnemies, self.myProjectiles = self.menuGameEventHandler.addGameObjects(
            #self.enemiesAlive, self.world.activeLevel, self.activeWeapon, self.myEnemies, self.starProbabilitySpace, self.starDensity, self.starMoveSpeed, self.myProjectiles, self.displayWidth)
        #self.starMoveSpeed = self.menuGameEventHandler.adjustStarMoveSpeed(self.maximumStarMoveSpeed, self.numberOfStarSpeeds)
        #self.myProjectiles, self.myEnemies, self.myHealth, self.score, self.enemiesAlive, self.y, self.ammo = self.menuGameEventHandler.MoveAndDrawProjectilesAndEnemies(
            #self.myProjectiles, self.myEnemies, self.myHealth, self.score, self.enemiesAlive, self.x, self.y, self.rocketWidth, self.rocketHeight, self.difficultySelection, self.displayWidth, self.displayHeight, self.ammo, self.starMoveSpeed)
        #self.menuGameEventHandler.drawObject(myCharacter, self.x, self.y)

    def GetKeyPress(self):
        self.exiting, self.lost, self.userCharacter, self.enterPressed, self.userMouse.coords, self.userMouse.btn, self.savePressed, self.objectType = self.logic.HandleHeyPressAndGameEvents(self.exiting, self.lost, self.userCharacter, None, None)

    def DisplayMainMenu(self):
        self.mainMenuItemMargin = 25
        for self.i in range(7):
            self.rgb = (255, 255, 255)
            if self.i == self.menuSelectionIndex:
                self.rgb = (self.colorIntensity, 0, 0)
            if self.i == 6:
                if self.menuType == "Paused":
                    self.text = "Resume"
                else:
                    self.text = "Begin Level Editor"
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
        for self.i in range(5):
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
    
        for self.i in range(3):
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
        for self.i in range(3):
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
        for self.i in range(-1, 11):
            for self.j in range(5):
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
        for self.row in range(self.iNeedThisManyMoreBlankSlots):
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
            for self.loadCounter in range(len(self.difficulties)):
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

        for self.loadCounter in range(len(self.difficulties)):
            #self.highScoresArray.append([])
            self.highScoresArray.insert(self.loadCounter, self.FillInBlankHighScores(self.highScoresArray[self.loadCounter]))
            #self.highScoresArray = self.FillInBlankHighScores(self.highScoresArray[self.loadCounter])
        self.highScoresArray.remove([])
        for self.loadCounter in range(len(self.difficulties)):
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

class WallObject(object):
    def __init__(self, PK = 1, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 1,  activeImage = 0, walkThroughPossible = 1, actionOnTouch = '', actionOnAttack = '', isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0):
        self.PK = PK
        self.scoreChangeOnTouch = scoreChangeOnTouch
        self.scoreChangeOnAttack = scoreChangeOnAttack
        self.healthChangeOnTouch = healthChangeOnTouch
        self.healthChangeOnAttack = healthChangeOnAttack
        self.addsToCharacterInventoryOnTouch = 0
        self.destroyOnTouch = 0
        self.addsToCharacterInventoryOnAttack = 0
        self.destroyOnAttack = 0

        self.ID = ID
        self.activeImage = activeImage
        self.walkThroughPossible = walkThroughPossible
        self.actionOnTouch = actionOnTouch
        self.actionOnAttack = actionOnAttack
        self.isAnimated = False

class GamePlayObject(object):
    pass

class Weapon(GamePlayObject):
    def __init__(self, PK, name, damage, ammo, physIndic, physicsCount, generateBulletWidth, generateBulletHeight, generateBulletSpeed, gravity, gravityCoefficient = .00005, generateParticleIndex = 0, inventoryImageIndex = '', worldImageIndex = ''):
        self.PK = PK
        self.name = name
        self.damage = damage
        self.ammo = ammo
        self.physIndic = physIndic
        self.physicsCount = physicsCount
        self.generateBulletWidth = generateBulletWidth
        self.generateBulletHeight = generateBulletHeight
        self.generateBulletSpeed = generateBulletSpeed
        self.generateParticleIndex = generateParticleIndex
        self.gravityCoefficient = gravityCoefficient
        self.inventoryImageIndex = inventoryImageIndex
        self.worldImageIndex = worldImageIndex

class WorldObject(GamePlayObject):
    def __init__(self, PK = 1, xTile = 0, yTile = 0, name = "", desc = "", columns = 0, activeImage = None,  walkThroughPossible = False, actionOnTouch = 0,  actionOnAttack = 0, timeBetweenAnimFrame = 0, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0, ID = 0, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, timeElapsedSinceLastFrame = 0, maxColumns = 0, speed = 0, defaultSpeed = 0, deltaX = 0, deltaY = 0, deltaXScreenOffset = 0, deltaYScreenOffset = 0, tileWidth = 0, tileHeight = 0, isAnimated = True):
        self.PK = PK
        self.deltaX = deltaX
        self.deltaY = deltaX
        self.xTile = xTile
        self.yTile = yTile
        self.speed = speed
        self.defaultSpeed = defaultSpeed
        self.name = name
        self.desc = desc
        self.columns = columns
        self.walkThroughPossible = walkThroughPossible
        self.actionOnTouch = actionOnTouch
        self.actionOnAttack = actionOnAttack
        self.activeImage = int(ID)*(int(columns))
        self.timeBetweenAnimFrame = timeBetweenAnimFrame
        self.timeElapsedSinceLastFrame = 0
        self.ID = ID
        self.scoreChangeOnTouch = scoreChangeOnTouch
        self.scoreChangeOnAttack = scoreChangeOnAttack
        self.healthChangeOnTouch = healthChangeOnTouch
        self.healthChangeOnAttack = healthChangeOnAttack
        self.addsToCharacterInventoryOnTouch = addsToCharacterInventoryOnTouch
        self.destroyOnTouch = destroyOnTouch
        self.addsToCharacterInventoryOnAttack = addsToCharacterInventoryOnAttack
        self.destroyOnAttack = destroyOnAttack
        self.timeElapsedSinceLastFrame = timeElapsedSinceLastFrame
        self.deltaXScreenOffset = deltaXScreenOffset #THIS WILL ALWAYS BE CALCULATED BY THE GAME, ABSTRACTED AWAY
        self.deltaYScreenOffset = deltaYScreenOffset #THIS WILL ALWAYS BE CALCULATED BY THE GAME, ABSTRACTED AWAY
        self.isAnimated = isAnimated
        self.maxColumns = maxColumns
    
class Bullet(WorldObject):
    #Name, weapon, world X Loc, world Y Loc,  dx,    dy, damage, physics actions remaining, particle width px, particle height px, frame speed, default speed, image, particlePhysicsLevel
    #if particlePhysicsLevel >= wallPhysicsLevel + 3 then particle pushes the wall
    #if particlePhysicsLevel = wallPhysicsLevel + 2 then particle goes through wall
    #if particlePhysicsLevel = wallPhysicsLevel + 1 then particle bounces off wall
    #if particlePhysicsLevel <= wallPhysicsLevel then particle absorbs into wall

    #physics actions represent the number of remaining times the particle can push/go through/bounce off walls

    #Name, weapon, world X Loc, world Y Loc,  dx,    dy, damage, bounces remaining, bullet width px, bullet height px, frame speed, default speed, image
    
    def __init__(self, name, weapon, xTile, yTile, deltaX, deltaY, damage, physicsIndicator, physicsCounter, width, height, character, speed = .01, defaultSpeed = .01, img=None, gravity = False, gravityCoefficient = .00005, boundToCamera = False):
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
        self.img = img #IMAGE ASSIGNED BECAUSE 1) IMAGE NEEDS TO BE GENERATE AT timeElapsedSinceLastFrame OF OBJECT CREATION, AND 2) WILL NOT BE CHANGING THROUGHOUT THE LIFE OF THE OBJECT
        #self.worldObjectID = worldObjectID
        self.imagesGFXName = "../Images/bullets.png"
        self.imagesGFXNameDesc = "Bullets"
        self.imagesGFXRows = 4
        self.imagesGFXColumns = 1
        self.weapon = weapon

class AI(object):
    pass

class Character(WorldObject):
    def __init__(self, name = "", imagesGFXName = "../Images/userPlayer.png", boundToCamera = False, xTile = 18, yTile = 18, deltaX = 0, deltaY = 0, timeSpentFalling = 0, gravityYDelta = 0, imgDirectionIndex = 0, imgLegIndex = 0, millisecondsOnEachLeg = 250, numberOfFramesAnimPerWalk = 3, pictureXPadding = 0, pictureYPadding = 0, defaultSpeed = .5, ammo = 1000, activeWeapon = 0, score = 0, weapons = [], inventory = [], width = 32, height = 32, shotsFiredFromMe = False, gravity = False, gravityCoefficient = .00005, ID = 0, isUser = 1, defaultAggression = .25):
        #GENERAL
        self.name = name
        self.numberOfFramesAnimPerWalk = numberOfFramesAnimPerWalk #3
        self.numberOfDirectionsFacingToDisplay = 8
        self.imagesGFXName = "../Images/userplayer.png"
        self.imagesGFXNameDesc = "User Player"
        self.imagesGFXRows = self.numberOfDirectionsFacingToDisplay
        self.imagesGFXColumns = self.numberOfFramesAnimPerWalk

        #LOCATION/APPEARANCE
        self.xFacing = 1
        self.yFacing = 1
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
        self.AI = AI()
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
    def __init__(self, index = 0, name = "", description = "", weather = "", sideScroller = 0, wallMap = [], objectMap = [], music = "", loopMusic = False, startX = 0, startY = 0, startXFacing = 0, startYFacing = 0, levelWidth = 127, levelHeight = 127, gravity = False, stickToWallsOnCollision = False, tileSheetRows = 0, tileSheetColumns = 0, tileWidth = 0, tileHeight = 0, tileXPadding = 0, tileYPadding = 0):
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
        self.levelWidth = levelWidth
        self.levelHeight = levelHeight

        self.wallMap = []
        for x in range(self.levelWidth):
            self.wallMap.append([])
            for y in range(self.levelHeight):
                self.wallMap[x].extend([0])

        self.objectMap = []
        for x in range(self.levelWidth):
            self.objectMap.append([])
            for y in range(self.levelHeight):
                self.objectMap[x].extend([None])

        self.tileSheetRows = tileSheetRows
        self.tileSheetColumns = tileSheetColumns
        self.tileWidth = tileWidth
        self.tileHeight = tileHeight
        self.tileXPadding = tileXPadding
        self.tileYPadding = tileYPadding

    def mapsToJSON(self):        
        Marshaller = JSONConverter()
        self.wallMapJSON = None
        wallMapWithSerializedObjects = [[]]
        for h in range(len(self.wallMap)):
            if h != 0:
                wallMapWithSerializedObjects.append([])
            wallMapWithSerializedObjects[h].extend([0] *len(self.wallMap[0]))

        for i in range(len(self.wallMap)):
            for j in range(len(self.wallMap[0])):
                wallMapWithSerializedObjects[i][j] = Marshaller.toJSON(self.wallMap[i][j])
        self.wallMapJSON = Marshaller.toJSON(wallMapWithSerializedObjects)

        self.objectMapJSON = None
        objectMapWithSerializedObjects = [[]]
        for h in range(len(self.objectMap)):
            if h != 0:
                objectMapWithSerializedObjects.append([])
            objectMapWithSerializedObjects[h].extend([0] *len(self.objectMap[0]))

        for i in range(len(self.objectMap)):
            for j in range(len(self.objectMap[0])):
                objectMapWithSerializedObjects[i][j] = Marshaller.toJSON(self.objectMap[i][j])
        self.objectMapJSON = Marshaller.toJSON(objectMapWithSerializedObjects)

    def JSONToMaps(self, JSONWallData, JSONObjectData):
        Marshaller = JSONConverter()
        #print Marshaller.fromJSON(JSONWallData)
        wallMapJSON = copy.deepcopy(Marshaller.fromJSON(JSONWallData, "WallData"))
        objectMapJSON = copy.deepcopy(Marshaller.fromJSON(JSONObjectData, "ObjectData"))
        
        for i in range(len(wallMapJSON)):
            for j in range(len(wallMapJSON[0])):
                wallMapJSON[i][j] = Marshaller.fromJSON(str(wallMapJSON[i][j]),"WallData" )
        
        for i in range(len(objectMapJSON)):
            for j in range(len(objectMapJSON[0])):
                objectMapJSON[i][j] = Marshaller.fromJSON(str(objectMapJSON[i][j]), "ObjectData")

        self.wallMap = copy.deepcopy(wallMapJSON)
        self.objectMap = copy.deepcopy(objectMapJSON)

class World(object):
    def __init__(self, filePath, fileName):
        self.fileName = os.path.join(filePath, fileName)
        self._ValidateDB()
        self.activeLevel = Level()
        self.wallObjects = []
        self.worldObejcts = []

    def _AdaptArray(self, array):
        out = io.BytesIO()
        np.save(out, array)
        out.seek(0)
        return sqlite3.Binary(out.read())

    def _ValidateDB(self):
        try:
            self.GetNumberOfLevels()
            if 1 == 0:
                #if self.numberOfLevels == 0:
                self.Reset()
                self.activeLevel = Level()
                self.SaveActiveLevel()
                
        except:
            self.Reset()
            self.activeLevel = Level()
            self.SaveActiveLevel()

    def SaveCharacters(self, characters):
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute("DROP TABLE IF EXISTS Characters")
        c.execute('CREATE TABLE Characters (PK INT, name TEXT, boundToCamera BOOL, xTile INT, yTile INT, deltaX INT, deltaY INT, millisecondsOnEachLeg INT, imgDirectionIndex INT, numberOfFramesAnimPerWalk INT, defaultSpeed REAL, ammo INT, activeWeapon INT, score INT, weapons BLOB, inventory BLOB, width INT, height INT, gravity BOOL, gravityCoefficient REAL, ID INT, isUser BOOL, defaultAggression REAL)')
        connection.commit()
        i = 0
        for obj in particles:
            c.execute("INSERT INTO Particles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (i,
                       PK,
                       name,
                       boundToCamera,
                       xTile,
                       yTile,
                       deltaX,
                       deltaY,
                       millisecondsOnEachLeg,
                       imgDirectionIndex,
                       numberOfFramesAnimPerWalk,
                       defaultSpeed,
                       ammo,
                       activeWeapon,
                       score,
                       weapons,
                       inventory,
                       width,
                       height,
                       gravity,
                       gravityCoefficient,
                       ID,
                       isUser,
                       defaultAggression))
            i = i + 1

    def LoadCharacters(self):
        characters = []
        c = connection.cursor()
        c.execute('SELECT * FROM Characters')
        for character in c:
            characters.append({character[0] : [character[1], character[2], character[3], character[4], character[5], character[6], character[7], character[8], character[9], character[10], character[12], character[13], character[14], character[15], character[16], character[17], character[18], character[19], character[20], character[21], character[22], character[23]]})
        connection.close()
        return characters
        

    def SaveParticles(self, particles):
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute("DROP TABLE IF EXISTS Particles")
        c.execute('CREATE TABLE Particles (PK INT, name TEXT, weaponFK INT, xTile INT, yTile INT, deltaX REAL, deltaY REAL, damage REAL, physicsIndicator TEXT, physicsCounter INT, width INT, height INT, character INT, speed REAL, defaultSpeed REAL, img INT, gravity BOOL, gravityCoefficient REAL, boundToCamera BOOL)')
        connection.commit()
        i = 0
        for obj in particles:
            c.execute("INSERT INTO Particles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (i,
                       name,
                       weaponFK,
                       xTile,
                       yTile,
                       deltaX,
                       deltaY,
                       damage,
                       physicsIndicator,
                       physicsCounter,
                       width,
                       height,
                       character,
                       speed,
                       defaultSpeed,
                       img,
                       gravity,
                       gravityCoefficient,
                       boundToCamera))
            i = i + 1
        connection.commit()
        connection.close()

    def LoadParticles(self):
        particles = []
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute('SELECT * FROM Particles')
        for particle in c:
            particles.append({particle[0] : [particle[1], particle[2], particle[3], particle[4], particle[5], particle[6], particle[7], particle[8], particle[9], particle[10], particle[11], particle[12], particle[13], particle[14], particle[15], particle[16], particle[17], particle[18], particle[19]]})
        connection.close()
        return particles

    def SaveWeapons(self, weapons):
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute("DROP TABLE IF EXISTS Weapons")
        c.execute('CREATE TABLE Weapons (PK INT, name TEXT, damage INT, ammo INT, physIndic INT, physicsCount INT, generateBulletWidth INT, generateBulletHeight INT, generateBulletSpeed INT, gravityCoefficient REAL, generateParticleIndex INT, inventoryImageIndex TEXT, worldImageIndex TEXT)')
        connection.commit()
        i = 0
        for obj in weapons:
            c.execute("INSERT INTO Weapons VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (i,
                       obj.name,
                       obj.damage,
                       obj.ammo,
                       obj.physIndic,
                       obj.physicsCount,
                       obj.generateBulletWidth,
                       obj.generateBulletHeight,
                       obj.generateBulletSpeed,
                       obj.gravityCoefficient,
                       obj.generateParticleIndex,
                       obj.inventoryImageIndex,
                       obj.worldImageIndex
                       
                          ))
            i = i + 1
        connection.commit()
        connection.close()

    def LoadWeapons(self):
        weapons = []
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute('SELECT * FROM Weapons')
        i = 0
        for weapon in c:
            weapons.append(Weapon(weapon[0], weapon[1], weapon[2], weapon[3], weapon[4], weapon[5], weapon[6], weapon[7], weapon[8], 0, weapon[9], weapon[10], weapon[11]))
            i = i + 1
        connection.close()
        return weapons


    def SaveSpritesheetSettings(self, spriteSheet):
        #TODO: Save spritesheets as blobs in db
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute("DROP TABLE IF EXISTS Spritesheets")
        c.execute('CREATE TABLE Spritesheets (PK INT, Caption TEXT, FilePath TEXT, Blob BLOB, tileWidth INT, tileHeight INT, tileXPadding INT, tileYPadding INT)')

        connection.commit()
        c.execute("INSERT INTO SpriteSheets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (1,
                   "WallObjects",
                   spriteSheet["WallObjects"][0],
                   None,
                   spriteSheet["WallObjects"][1],
                   spriteSheet["WallObjects"][2],
                   spriteSheet["WallObjects"][3],
                   spriteSheet["WallObjects"][4] ))

        c.execute("INSERT INTO SpriteSheets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (2,
                   "WorldObjects",
                   spriteSheet["WorldObjects"][0],
                   None,
                   spriteSheet["WorldObjects"][1],
                   spriteSheet["WorldObjects"][2],
                   spriteSheet["WorldObjects"][3],
                   spriteSheet["WorldObjects"][4] ))

        c.execute("INSERT INTO SpriteSheets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (3,
                   "Particles",
                   spriteSheet["Particles"][0],
                   None,
                   spriteSheet["Particles"][1],
                   spriteSheet["Particles"][2],
                   spriteSheet["Particles"][3],
                   spriteSheet["Particles"][4] ))

        c.execute("INSERT INTO SpriteSheets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (4,
                   "Characters",
                   spriteSheet["Characters"][0],
                   None,
                   spriteSheet["Characters"][1],
                   spriteSheet["Characters"][2],
                   spriteSheet["Characters"][3],
                   spriteSheet["Characters"][4] ))
        connection.commit()
        connection.close()

    def LoadSpritesheetSettings(self):
        Spritesheets = {}
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        
        c.execute('SELECT * FROM Spritesheets')
        for Spritesheet in c:
            Spritesheets[Spritesheet[0]] = [Spritesheet[1], Spritesheet[2], Spritesheet[3], Spritesheet[4], Spritesheet[5], Spritesheet[6], Spritesheet[7]]
        connection.close()
        self.sprintesheetSettings = Spritesheets
        print(str(Spritesheets))
        return Spritesheets


    def AddLevel(self):
        prevLevel = self.activeLevel
        self.activeLevel = Level(index = self.GetNumberOfLevels())
        self.activeLevel.mapsToJSON()
        print(prevLevel.tileWidth)
        print(prevLevel.tileHeight)
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute("INSERT INTO Levels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (self.activeLevel.index,
                  self.activeLevel.name,
                  self.activeLevel.description,
                  self.activeLevel.weather,
                  self.activeLevel.sideScroller,
                   str(self.activeLevel.wallMapJSON),
                   str(self.activeLevel.objectMapJSON),

                  #sqlite3.Binary(str.encode(self.activeLevel.wallMapJSON)),
                  #sqlite3.Binary(str.encode(self.activeLevel.objectMapJSON)),
                  self.activeLevel.music,
                  self.activeLevel.loopMusic,
                  self.activeLevel.startX,
                  self.activeLevel.startY,
                  self.activeLevel.startXFacing,
                  self.activeLevel.startYFacing,
                  prevLevel.gravity,
                  prevLevel.stickToWallsOnCollision,
                  self.activeLevel.levelHeight,
                  self.activeLevel.levelWidth,
                  prevLevel.tileSheetRows,
                  prevLevel.tileSheetColumns,
                  prevLevel.tileWidth,
                  prevLevel.tileHeight,
                  prevLevel.tileXPadding,
                  prevLevel.tileYPadding))
        connection.commit()
        connection.close()
        self.LoadLevel(self.activeLevel.index)

    def Reset(self):
        try:
            #print self.fileName
            #print "reset 1"
            connection = sqlite3.connect(self.fileName)
            #print "reset 2"
            c = connection.cursor()
            #print "reset 3"
            c.execute("DROP TABLE IF EXISTS Levels")
            #print "reset 4"
            c.execute("CREATE TABLE Levels (IndexPK INT, Name TEXT, Description TEXT, Weather TEXT, SideScroller BOOL, WallMap TEXT, ObjectMap TEXT, music TEXT, loopMusic BOOL, startX INT, startY INT, startXFacing INT, startYFacing INT, gravity BOOL, stickToWallsOnCollision BOOL, levelHeight INT, levelWidth INT, tileSheetRows INT, tileSheetColumns INT, tileWidth INT, tileHeight INT, tileXPadding INT, tileYPadding INT)")
            #print "reset 5"
            c.execute("DROP TABLE IF EXISTS WallObjects")
            c.execute('CREATE TABLE WallObjects (PK INT, scoreChangeOnTouch INT, scoreChangeOnAttack INT, healthChangeOnTouch INT, healthChangeOnAttack INT, ID INT,  activeImage INT, walkThroughPossible BOOL, actionOnTouch TEXT, actionOnAttack TEXT, isAnimated BOOL, addsToCharacterInventoryOnTouch BOOL, destroyOnTouch BOOL, addsToCharacterInventoryOnAttack BOOL, destroyOnAttack BOOL)')
            
            c.execute("DROP TABLE IF EXISTS WorldObjects")
            c.execute('CREATE TABLE WorldObjects (PK INT, name TEXT, desc TEXT, columns INT, walkThroughPossible BOOL, actionOnTouch TEXT , actionOnAttack TEXT, timeBetweenAnimFrame INT, addsToCharacterInventoryOnTouch INT, destroyOnTouch INT, addsToCharacterInventoryOnAttack INT, destroyOnAttack INT, ID TEXT, scoreChangeOnTouch INT, scoreChangeOnAttack INT, healthChangeOnTouch INT, healthChangeOnAttack INT, timeElapsedSinceLastFrame INT)')

##            c.execute("DROP TABLE IF EXISTS Spritesheets")
##            c.execute('CREATE TABLE Spritesheets (PK INT, Caption TEXT, FilePath TEXT, Blob BLOB, tileWidth INT, tileHeight INT, tileXPadding INT, tileYPadding INT)')
##
##
##            c.execute("INSERT INTO SpriteSheets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
##                      (1,
##                       "WallObjects",
##                       spriteSheet["WallObjects"][1],
##                       spriteSheet["WallObjects"][2],
##                       spriteSheet["WallObjects"][3],
##                       spriteSheet["WallObjects"][4],
##                       spriteSheet["WallObjects"][5],
##                       spriteSheet["WallObjects"][6] ))
##
##            c.execute("INSERT INTO SpriteSheets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
##                      (2,
##                       "WorldObjects",
##                       spriteSheet["WorldObjects"][1],
##                       spriteSheet["WorldObjects"][2],
##                       spriteSheet["WorldObjects"][3],
##                       spriteSheet["WorldObjects"][4],
##                       spriteSheet["WorldObjects"][5],
##                       spriteSheet["WorldObjects"][6] ))
##
##            c.execute("INSERT INTO SpriteSheets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
##                      (3,
##                       "Particles",
##                       spriteSheet["Particles"][1],
##                       spriteSheet["Particles"][2],
##                       spriteSheet["Particles"][3],
##                       spriteSheet["Particles"][4],
##                       spriteSheet["Particles"][5],
##                       spriteSheet["Particles"][6] ))
##
##            c.execute("INSERT INTO SpriteSheets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
##                      (4,
##                       "Characters",
##                       spriteSheet["Characters"][1],
##                       spriteSheet["Characters"][2],
##                       spriteSheet["Characters"][3],
##                       spriteSheet["Characters"][4],
##                       spriteSheet["Characters"][5],
##                       spriteSheet["Characters"][6] ))

        except:
            print("THERE WAS AN ERROR RESETTING")

        finally:
            connection.commit()
            #print "reset 6"
            connection.close()
            del c, connection

    def GetNumberOfLevels(self):
        #print "Get number of levels: 0"
        connex = sqlite3.connect(self.fileName)
        #print "Get number of levels: 1"
        cursor = connex.cursor()
        #print "Get number of levels: 2"
        try:
            cursor.execute("SELECT COUNT(*) FROM Levels")
            self.numberOfLevels = cursor.fetchone()[0]
            #print "Get number of levels: 3"
        except:
            self.numberOfLevels = 0
            #print "Get number of levels: -1"
        finally:
            connex.commit()
            connex.close()
            #print "Get number of levels: 4"
            del connex, cursor
            #print "I've counted " + str(self.numberOfLevels) + " levels"
            return self.numberOfLevels

    def RemoveLevel(self, index):
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute("DELETE FROM Levels WHERE IndexPK = ?", str(index))
        self.LoadLevel(self.activeLevel.index - 1)
        connection.commit()
        connection.close()

    def LevelExists(self, index):
        #print "Level exists index: " + str(index)
        retVal = 0
        try:
            #print "Level exists: 0"
            connex = sqlite3.connect(self.fileName)
            #print "Level exists: 1"
            cursor = connex.cursor()
            #print "Level exists: 2"
            cursor.execute("SELECT COUNT(*) FROM Levels WHERE IndexPK = ?", str(index))
            #print "Level exists: 3"
            retVal = cursor.fetchone()[0]
        except:
            retVal = 0
        finally:
            #print "Level exists progress: " + str(retVal)
            connex.commit()
            connex.close()
            del connex, cursor
            return retVal

    def LoadLevel(self, index):
        if self.LevelExists(index) > 0:
            connection = sqlite3.connect(self.fileName)
            c = connection.cursor()
            c.execute('SELECT * FROM Levels WHERE IndexPK =?', str(index))
            levelData = c.fetchone()
            self.activeLevel.index = index
            self.activeLevel.name = levelData[1]
            self.activeLevel.description = levelData[2]
            self.activeLevel.weather = levelData[3]
            self.activeLevel.sideScroller = levelData[4]

            #with open(StringIO(levelData[5]).read(), 'r') as f:
                #with open(StringIO(levelData[6]).read(), 'r') as g:
                    #level.JSONToMaps(f , g)
            self.activeLevel.JSONToMaps(levelData[5], levelData[6])
            for y in range(len(self.activeLevel.wallMap)):
                for x in range(len(self.activeLevel.wallMap[0])):
                    #print(self.activeLevel.wallMap[y][x])
                    self.activeLevel.wallMap[y][x] = self.activeLevel.wallMap[y][x]

            for y in range(len(self.activeLevel.objectMap)):
                for x in range(len(self.activeLevel.objectMap[0])):
                    self.activeLevel.objectMap[y][x] = self.activeLevel.objectMap[y][x]
            
            #level.wallMap = levelData[4]
            #level.objectMap = levelData[5]
            #print StringIO(levelData[6]).read()
            self.activeLevel.music = levelData[7]
            self.activeLevel.loopMusic = levelData[8]
            self.activeLevel.startX = levelData[9]
            self.activeLevel.startY = levelData[10]
            self.activeLevel.startXFacing = levelData[11]
            self.activeLevel.startYFacing = levelData[12]
            self.activeLevel.gravity = levelData[13]
            self.activeLevel.stickToWallsOnCollision = levelData[14]
            self.activeLevel.levelHeight = levelData[15]
            self.activeLevel.levelWidth = levelData[16]
            self.activeLevel.tileSheetRows = levelData[17]
            self.activeLevel.tileSheetColumns = levelData[18]
            self.activeLevel.tileWidth = levelData[19]
            print("1 " + str(self.activeLevel.tileWidth))
            self.activeLevel.tileHeight = levelData[20]
            self.activeLevel.tileXPadding = levelData[21]
            self.activeLevel.tileYPadding = levelData[22]
            #return Level(index, name, description, weather, sideScroller, wallMap, objectMap, music, loopMusic, startX, startY, startXFacing, startYFacing, xSize, ySize, gravity, stickToWallsOnCollision, tileSheetRows, tileSheetColumns, tileWidth, tileHeight, tileXPadding, tileYPadding)
            connection.close()
        else:
            self.activeLevel = Level()
        

    def SaveActiveLevel(self):
        self.activeLevel.mapsToJSON()
        if self.LevelExists(self.activeLevel.index) == 1:
            connection = sqlite3.connect(self.fileName)
            c = connection.cursor()
            c.execute("UPDATE Levels SET IndexPK = ?, Name = ?, Description = ?, Weather = ?, SideScroller = ?, WallMap = ?, ObjectMap = ?, music = ?, loopMusic = ?, startX = ?, startY = ?, startXFacing = ?, startYFacing = ?, gravity = ?, stickToWallsOnCollision = ?, levelHeight = ?, levelWidth = ?, tileSheetRows = ?, tileSheetColumns = ?, tileWidth = ?, tileHeight = ?, tileXPadding = ?, tileYPadding = ? WHERE IndexPK = ?",
                      (self.activeLevel.index,
                      self.activeLevel.name,
                      self.activeLevel.description,
                      self.activeLevel.weather,
                      self.activeLevel.sideScroller,
                       str(self.activeLevel.wallMapJSON),
                       str(self.activeLevel.objectMapJSON),
                       #This breaks in Python 3.5.2
                      #sqlite3.Binary(str.encode(self.activeLevel.wallMapJSON)),
                      #sqlite3.Binary(str.encode(self.activeLevel.objectMapJSON)),
                       
                      self.activeLevel.music,
                      self.activeLevel.loopMusic,
                      self.activeLevel.startX,
                      self.activeLevel.startY,
                      self.activeLevel.startXFacing,
                      self.activeLevel.startYFacing,
                      self.activeLevel.gravity,
                      self.activeLevel.stickToWallsOnCollision,
                      self.activeLevel.levelHeight,
                      self.activeLevel.levelWidth,
                      self.activeLevel.tileSheetRows,
                      self.activeLevel.tileSheetColumns,
                      self.activeLevel.tileWidth,
                      self.activeLevel.tileHeight,
                      self.activeLevel.tileXPadding,
                      self.activeLevel.tileYPadding,
                      self.activeLevel.index))
            print("Saving tileWidth: " + str(self.activeLevel.tileWidth))
        else:
            connection = sqlite3.connect(self.fileName)
            c = connection.cursor()
            c.execute("INSERT INTO Levels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (self.activeLevel.index,
                      self.activeLevel.name,
                      self.activeLevel.description,
                      self.activeLevel.weather,
                      self.activeLevel.sideScroller,
                       str(self.activeLevel.wallMapJSON),
                       str(self.activeLevel.objectMapJSON),
                      #sqlite3.Binary(str.encode(self.activeLevel.wallMapJSON)),
                      #sqlite3.Binary(str.encode(self.activeLevel.objectMapJSON)),
                      self.activeLevel.music,
                      self.activeLevel.loopMusic,
                      self.activeLevel.startX,
                      self.activeLevel.startY,
                      self.activeLevel.startXFacing,
                      self.activeLevel.startYFacing,
                      self.activeLevel.gravity,
                      self.activeLevel.stickToWallsOnCollision,
                      self.activeLevel.levelHeight,
                      self.activeLevel.levelWidth,
                      self.activeLevel.tileSheetRows,
                      self.activeLevel.tileSheetColumns,
                      self.activeLevel.tileWidth,
                      self.activeLevel.tileHeight,
                      self.activeLevel.tileXPadding,
                      self.activeLevel.tileYPadding))
            print("Saving tileWidth: " + str(self.activeLevel.tileWidth))
        connection.commit()
        connection.close()

    def SaveWallObjects(self, WallObjectData):
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        #c.execute('TRUNCATE TABLE WallObjects')
        c.execute("DROP TABLE IF EXISTS WallObjects")
        
        c.execute('CREATE TABLE WallObjects (PK INT, scoreChangeOnTouch INT, scoreChangeOnAttack INT, healthChangeOnTouch INT, healthChangeOnAttack INT, ID INT,  activeImage INT, walkThroughPossible BOOL, actionOnTouch TEXT, actionOnAttack TEXT, isAnimated BOOL, addsToCharacterInventoryOnTouch BOOL, destroyOnTouch BOOL, addsToCharacterInventoryOnAttack BOOL, destroyOnAttack BOOL)')

        connection.commit()
        for i in WallObjectData:
            c.execute('INSERT INTO WallObjects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                      (
                        i.PK,
                        i.scoreChangeOnTouch,
                        i.scoreChangeOnAttack,
                        i.healthChangeOnTouch,
                        i.healthChangeOnAttack,
                        i.ID,
                        i.activeImage,
                        i.walkThroughPossible,
                        i.actionOnTouch,
                        i.actionOnAttack,
                        i.isAnimated,
                        i.addsToCharacterInventoryOnTouch,
                        i.destroyOnTouch,
                        i.addsToCharacterInventoryOnAttack,
                        i.destroyOnAttack
                      ))
            connection.commit()
        connection.close()

    def SaveWorldObjects(self, WorldObjectData):
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        #c.execute('TRUNCATE TABLE WorldObjects')
        c.execute("DROP TABLE IF EXISTS WorldObjects")
        c.execute('CREATE TABLE WorldObjects (PK INT, name TEXT, desc TEXT, columns INT, activeImage INT, walkThroughPossible BOOL, actionOnTouch TEXT , actionOnAttack TEXT, timeBetweenAnimFrame INT, addsToCharacterInventoryOnTouch INT, destroyOnTouch INT, addsToCharacterInventoryOnAttack INT, destroyOnAttack INT, ID INT, scoreChangeOnTouch INT, scoreChangeOnAttack INT, healthChangeOnTouch INT, healthChangeOnAttack INT, timeElapsedSinceLastFrame INT, maxColumns INT)')

        connection.commit()
        for i in WorldObjectData:
            c.execute('INSERT INTO WorldObjects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                      (
                        i.PK,
                        i.name,
                        i.desc,
                        i.columns,
                        0,
                        i.walkThroughPossible,
                        i.actionOnTouch,
                        i.actionOnAttack,
                        i.timeBetweenAnimFrame,
                        i.addsToCharacterInventoryOnTouch,
                        i.destroyOnTouch,
                        i.addsToCharacterInventoryOnAttack,
                        i.destroyOnAttack,
                        i.ID,
                        i.scoreChangeOnTouch,
                        i.scoreChangeOnAttack,
                        i.healthChangeOnTouch,
                        i.healthChangeOnAttack,
                        i.timeElapsedSinceLastFrame,
                        i.maxColumns
                      ))
            connection.commit()
        c.execute('SELECT * FROM WorldObjects')
        connection.close()

    def LoadWallObjects(self):
        WallObjectData = []
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute('SELECT * FROM WallObjects')
        for wall in c:
            WallObjectData.append(WallObject(wall[0], wall[1], wall[2], wall[3], wall[4], wall[5], wall[6], wall[7], wall[8], wall[9], wall[10], wall[11], wall[12], wall[13], wall[14]))
        connection.close()
        self.wallObjects = WallObjectData
        if self.wallObjects == []:
            self.wallObjects = [WallObject()]
        return self.wallObjects

    def LoadWorldObjects(self):
        WorldObjectData = []
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute('SELECT * FROM WorldObjects')
        for obj in c:
            WorldObjectData.append(WorldObject(obj[0], None, None, obj[1], obj[2], obj[3], obj[4], obj[5], obj[6], obj[7], obj[8], obj[9], obj[10], obj[11], obj[12], obj[13], obj[14], obj[15], obj[16], obj[17], obj[18], obj[19]))
        connection.close()
        self.worldObjects = WorldObjectData
        if self.worldObjects == []:
            self.worldObjects = [WorldObject()]
        return self.worldObjects

class Game(object):
    def __init__(self, screenResSelection, fullScreen, worldDB, worldDBFilePath, startingLevel):
        #self.world = World("./", worldDB)
        self.world = World(worldDBFilePath, worldDB)
        #self.world.Reset()
        self.world.LoadWorldObjects()
        self.world.LoadWallObjects()
        self.world.LoadLevel(startingLevel)
        self.world.activeLevel.startX = 19
        self.world.activeLevel.tileHeight = 64
        self.world.activeLevel.tileWidth = 64
        
##
##        self.world.worldObjects = [WorldObject(PK = 0, name = "Diamond", desc = "Diamond Flicker Example", columns = 4, actionOnTouch = 0, actionOnAttack = 0, timeBetweenAnimFrame = 250, timeElapsedSinceLastFrame = 0, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0, ID = 0, walkThroughPossible = True),
##                                   WorldObject(PK = 1, name = "Ball",    desc = "Red Ball Example",        columns = 4, actionOnTouch = 0, actionOnAttack = 0, timeBetweenAnimFrame = 250, timeElapsedSinceLastFrame = 0, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0, ID = 1, walkThroughPossible = False)]
##        
##        self.world.wallObjects = [WallObject(PK = 1, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID =1,  activeImage = 0, walkThroughPossible = True, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 1, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 2,  activeImage = 1, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 2, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 3,  activeImage = 2, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 3, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 4,  activeImage = 3, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 4, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 5,  activeImage = 4, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 5, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 6,  activeImage = 5, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 6, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 7,  activeImage = 6, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 7, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 8,  activeImage = 7, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 8, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 9,  activeImage = 8, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 9, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 10,  activeImage = 9, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 10, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 11,  activeImage = 10, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 11, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 12,  activeImage = 11, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 12, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 13,  activeImage = 12, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 13, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 14,  activeImage = 13, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 14, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 15,  activeImage = 14, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 15, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 16,  activeImage = 15, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 16, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 17,  activeImage = 16, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 17, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 18,  activeImage = 17, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 18, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 19,  activeImage = 18, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 19, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 20,  activeImage = 19, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 20, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 21,  activeImage = 20, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 21, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 22,  activeImage = 21, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 22, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 23,  activeImage = 22, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 23, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 24,  activeImage = 23, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 24, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 25,  activeImage = 24, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 25, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 26,  activeImage = 25, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 26, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 27,  activeImage = 26, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 27, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 28,  activeImage = 27, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 28, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 29,  activeImage = 28, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 29, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 30,  activeImage = 29, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 31, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 31,  activeImage = 30, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 32, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 32,  activeImage = 31, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 33, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 33,  activeImage = 32, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 34, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 34,  activeImage = 33, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 35, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 35,  activeImage = 34, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 36, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 36,  activeImage = 35, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 37, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 37,  activeImage = 36, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 38, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 38,  activeImage = 37, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 39, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 39,  activeImage = 38, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 40, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 40,  activeImage = 39, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 41, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 41,  activeImage = 40, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 42, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 42,  activeImage = 41, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 43, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 43,  activeImage = 42, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 44, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 44,  activeImage = 43, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 45, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 45,  activeImage = 44, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 46, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 46,  activeImage = 45, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 47, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 47,  activeImage = 46, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 48, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 48,  activeImage = 47, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 49, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 49,  activeImage = 48, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 50, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 50,  activeImage = 49, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 51, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 51,  activeImage = 50, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##                WallObject(PK = 52, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 52,  activeImage = 51, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0),
##
##                WallObject(PK = 52, scoreChangeOnTouch = 0, scoreChangeOnAttack = 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 53,  activeImage = 52, walkThroughPossible = False, actionOnTouch = "", actionOnAttack = "", isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0)]
        
                                  
##        self.world.activeLevel = Level(0, "Demo", "This is a demonstration level", "Clear", 0,
##                        [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
##                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,8,0,0,0,7,8,0,0,0,7,8,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,6,0,0,0,5,6,0,0,0,5,6,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,0,0,0,3,4,0,0,0,3,4,0,0,0,0,0,0,0,0,0,1,1],
##                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
##                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]],
##
##                            [[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[], WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, actionOnTouch = 0, actionOnAttack = 0, timeElapsedSinceLastFrame = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThroughPossible = True),[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, actionOnTouch = 0, actionOnAttack = 0, timeElapsedSinceLastFrame = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThroughPossible = True),[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, actionOnTouch = 0, actionOnAttack = 0, timeElapsedSinceLastFrame = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThroughPossible = True),[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, actionOnTouch = 0, actionOnAttack = 0, timeElapsedSinceLastFrame = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThroughPossible = True),[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, actionOnTouch = 0, actionOnAttack = 0, timeElapsedSinceLastFrame = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThroughPossible = True),[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],WorldObject(name = "Diamond", desc = "Diamond Flicker Example", columns = 4, actionOnTouch = 0, actionOnAttack = 0, timeElapsedSinceLastFrame = 1000, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, ID = 0, walkThroughPossible = True)]],
##                            "", True, 22, 2, 1, 0, 127, 127, False, False, 9, 1, 64, 64, 0, 0)
##                            #music = "", loopMusic = False, startX = 0, startY = 0, startXFacing = 0, startYFacing = 0, levelWidth = 127, levelHeight = 127, gravity = False, stickToWallsOnCollision = False, tileSheetRows = 0, tileSheetColumns = 0, tileWidth = 0, tileHeight = 0, tileXPadding = 0, tileYPadding = 0
##
##        self.world.SaveActiveLevel()



##
##        self.world.activeLevel = Level(0, "Demo", "This is a demonstration level", "Clear", None,
##                        [[None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
##                        [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]],
##                            [[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
##                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]],
##                            "", True, 2, 2, 1, 0, 127, 127, False, False, 8, 1, 64, 64, 0, 0)
##                            #music = "", loopMusic = False, startX = 0, startY = 0, startXFacing = 0, startYFacing = 0, levelWidth = 127, levelHeight = 127, gravity = False, stickToWallsOnCollision = False, tileSheetRows = 0, tileSheetColumns = 0, tileWidth = 0, tileHeight = 0, tileXPadding = 0, tileYPadding = 0
##
##        self.world.SaveActiveLevel()





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
        
        self.mouseWidth = self.world.activeLevel.tileWidth
        self.personHeight = self.world.activeLevel.tileHeight

        #xFacing = self.world.activeLevel.startXFacing, yFacing = self.world.activeLevel.startYFacing, 
        self.userCharacter = Character(name = "User", boundToCamera = True, xTile = self.world.activeLevel.startX, yTile = self.world.activeLevel.startY, deltaX = 0, deltaY = 0) #particles: [NAME, X1, Y1, DX, DY, R, G, B, SPEED, 0])
        self.userCharacter.InitializeScreenPosition(self.camera, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)
        for i in range (4):
            self.userCharacter.weapons.append(Weapon(i, str(i), (i+1) * 10, 1000, 2, 2, 16, 16, (i+1)/float(100), 0, 0))
        self.characters = [self.userCharacter]
        ###for character in self.characters:
            ###self.gfx.LoadGfxDictionary(character.imagesGFXName, character.imagesGFXNameDesc, character.numberOfDirectionsFacingToDisplay, character.numberOfFramesAnimPerWalk, character.width, character.height, 0, 0)
        self.gfx.LoadGfxDictionary("../Images/spritesheet.png", "World Tiles", 8, 1, 64, 64, 0, 0)
        self.gfx.LoadGfxDictionary("../Images/bullets.png", "Particles", 4, 1, 16, 16, 0, 0)
        self.gfx.LoadGfxDictionary("../Images/world objects.png", "World Objects", 4, 4, 64, 64, 0, 0)
        self.gfx.LoadGfxDictionary("../Images/level editor frame.png", "Level Editor Frame", 2, 4, self.mouseWidth, self.personHeight, 0, 0)
        self.displayFrame = LevelEditorFrame(self.gfx, self.camera, self.world.activeLevel.tileHeight, self.world.activeLevel.tileWidth, "World Tiles", 4, {'World Tiles' : self.world.wallObjects, 'World Objects': self.world.worldObjects})
        self.FPSLimit = 240
        
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
            self.paused, self.lost, self.userCharacter, self.enterPressed, self.userMouse.coords, self.userMouse.btn, self.savePressed, self.displayFrame.objectType = self.logic.HandleHeyPressAndGameEvents(self.paused, self.lost, self.userCharacter, self.world, self.displayFrame.objectType)
            #Select the correct image for all characters based on direction facing
            self.userCharacter.DetermineCharPicBasedOnDirectionFacing()
            #Select the correct image for all characters based on what leg they are standing on
            self.userCharacter.DetermineCharPicBasedOnWalkOrMovement(self.timeElapsedSinceLastFrame)
            #FIGURE OUT HOW MUCH timeElapsedSinceLastFrame HAS ELAPSED SINCE LAST FRAME WAS DRAWN
            self.timeElapsedSinceLastFrame = self.logic.ManageTimeAndFrameRate(self.lastTick, self.clock, self.FPSLimit)
            #NOW THAT KEY PRESSES HAVE BEEN HANDLED, ADJUST THE SPEED OF EVERYTHING BASED ON HOW MUCH timeElapsedSinceLastFrame ELAPSED SINCE LAST FRAME DRAW, AND PREVENT DIAGONAL SPEED UP ISSUE
            self.particles, self.userCharacter = self.logic.AdjustSpeedBasedOnFrameRate(self.timeElapsedSinceLastFrame, self.particles, self.userCharacter)

            self.camera.TestIfAtWorldEdgeCollision(self.world.activeLevel.wallMap, self.userCharacter, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.displayFrame)
            #self.userCharacter.ApplyGravity()
            #CHECK FOR CHARACTER-WALL COLLISIONS
            ###self.userCharacter.UpdateDirectionBasedOnWallCollisionTest(self.world.activeLevel.wallMap, self.camera, self.tileHeight, self.tileWidth, self.world.activeLevel.gravity, self.world.activeLevel.stickToWallsOnCollision)
            #ADJUST DIAGONAL SPEED IF USER PRESSES 2 ARROW KEYS
            self.userCharacter.deltaX, self.userCharacter.deltaY = self.logic.FixDiagSpeed(self.userCharacter.deltaX, self.userCharacter.deltaY, self.userCharacter.speed)

            #TODO: generateBadGuys()
            #TODO: badGuysMoveOrAttack()
            
            #TEST IF USER CHARACTER MoveS OUTSIDE OF INNER NINTH OF SCREEN
            self.userCharacter = self.camera.MoveBasedOnCharacterMove(self.userCharacter, self.world.activeLevel.tileHeight, self.world.activeLevel.tileWidth, self.world.activeLevel.levelWidth, self.world.activeLevel.levelHeight)
            #Move THE USER CHARACTER IN THE WORLD, AND ON THE SCREEN
            self.userCharacter.Move(self.camera, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.userCharacter.deltaX, self.userCharacter.deltaY)

            #I THINK I NEED TO DELETE THIS
            ###if self.world.activeLevel.gravity == True:
            ###    self.userCharacter.gravityYDelta, self.userCharacter.timeSpentFalling = self.userCharacter.CalculateNextGravityVelocity(self.world.activeLevel.tileHeight)

            #Move PARTICLES
            self.particles = self.logic.MoveParticlesAndHandleParticleCollision(self.particles, self.world.activeLevel.wallMap)
            #GENERATE PARTICLES
            self.particles, self.userCharacter = self.logic.GenerateParticles(self.particles, self.userCharacter, self.world.activeLevel.tileHeight, self.world.activeLevel.tileWidth, self.gfx)# (self.bullets, rain drops, snowflakes, etc...)
            #DRAW THE WORLD IN TILES BASED ON THE THE NUMBERS IN THE thisLevelMap ARRAY
            self.gfx.DrawWorldInCameraView("World Tiles", self.camera, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.world.activeLevel.wallMap, self.gameDisplay)
            #DRAW THE WORLD IN OBJECTS BASED ON THE THE NUMBERS IN THE self.thisLevelObjects ARRAY
            self.world.activeLevel.objectMap = self.gfx.DrawWorldInCameraView("World Objects", self.camera, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.world.activeLevel.objectMap, self.gameDisplay, self.timeElapsedSinceLastFrame)
            #DRAW PEOPLE, ENEMIES, OBJECTS AND PARTICLES
            ###self.gfx.DrawObjectsAndParticles(self.particles, self.gameDisplay, self.camera, self.tileHeight, self.tileWidth, self.userCharacter)

            #DRAW THE LEVEL EDITOR FRAME AND FRAME OBJECTS
            self.displayFrame.DrawLevelEditorFrame(self.camera, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.world.activeLevel.wallMap, self.gfx, self.gameDisplay)
            self.displayFrame.DrawTileAndObjectPalette(self.camera, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.gfx, self.gameDisplay, self.displayFrame.objectType)
            #CONVERT MOUSE COORDS -> WORLD TILES
            self.userMouse.xTile, self.userMouse.yTile = self.gfx.ConvertScreenCoordsToTileCoords(self.userMouse.coords, self.camera, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)

            self.displayFrame, self.world.activeLevel.wallMap, self.world.activeLevel.objectMap = self.logic.HandleMouseEvents(self.userMouse, self.camera, self.displayFrame, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.world.activeLevel.wallMap, self.world.activeLevel.objectMap, self.gfx, self.displayFrame.objectType, self.world.wallObjects, self.world.worldObjects)

            #DRAW GAME STATS
            #self.gfx.DrawSmallMessage("Health: " + str(self.myHealth), 0, self.gameDisplay, white, self.displayWidth)
            #self.gfx.DrawSmallMessage("Ammo: " + str(self.userCharacter.ammo), 1, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.DrawSmallMessage("Level: " + str(self.world.activeLevel), 2, self.gameDisplay, white, self.displayWidth)
            #self.gfx.DrawSmallMessage("Score: " + str(self.score), 3, self.gameDisplay, white, self.displayWidth)
            #self.gfx.DrawSmallMessage("Player wX: " + str(self.userCharacter.GetLocationInWorld()[0]), 4, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.DrawSmallMessage("Player wY: " + str(self.userCharacter.GetLocationInWorld()[1]), 5, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.DrawSmallMessage("Player sX: " + str(self.userCharacter.GetLocationOnScreen()[0]), 6, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.DrawSmallMessage("Player sY: " + str(self.userCharacter.GetLocationOnScreen()[1]), 7, self.gameDisplay, white, self.camera.displayWidth)

            ##self.gfx.DrawSmallMessage("X Offset: " + str(self.camera.viewToScreenPxlOffsetX), 6, self.gameDisplay, white, self.camera.displayWidth)
            ##self.gfx.DrawSmallMessage("Y Offset: " + str(self.camera.viewToScreenPxlOffsetY), 7, self.gameDisplay, white, self.camera.displayWidth)
            
            self.gfx.DrawSmallMessage("Cam X: " + str(self.camera.GetLocationInWorld(self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)[0]), 1, self.gameDisplay, white, self.camera.displayWidth)
            self.gfx.DrawSmallMessage("Cam Y: " + str(self.camera.GetLocationInWorld(self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)[1]), 2, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.DrawSmallMessage("FPS: " + str(int(1000/max(1, self.timeElapsedSinceLastFrame))), 3, self.gameDisplay, white, self.camera.displayWidth)
            self.gfx.DrawSmallMessage("Level: " + str(self.world.activeLevel.index), 3, self.gameDisplay, white, self.camera.displayWidth)
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
    def __init__(self, title, windowWidth, windowHeight, context):
        wx.Frame.__init__(self, None, title=title, size=(windowWidth, windowHeight))#, style=wx.NO_BORDER)# | wx.STAY_ON_TOP)
        self.world = context
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight

        p = wx.Panel(self)
        nb = wx.Notebook(p)

        tab1 = GameTab(nb)
        tab2 = SpriteSheetTab(nb, self.world)
        tab3 = WorldTab(nb)
        tab4 = LevelsTab(nb)
        tab5 = WallObjectsTab(nb, self.world)
        tab6 = WorldObjectsTab(nb, self.world)
        tab7 = ParticlesTab(nb, self.world)
        tab8 = CharactersTab(nb)
        tab9 = WeaponsTab(nb, self.world)        
        tab10 = SoundsTab(nb)
 
        # Add the windows to tabs and name them.
        nb.AddPage(tab1, tab1.caption)
        nb.AddPage(tab2, tab2.caption)
        nb.AddPage(tab3, tab3.caption)
        nb.AddPage(tab4, tab4.caption)
        nb.AddPage(tab5, tab5.caption)
        nb.AddPage(tab6, tab6.caption)
        nb.AddPage(tab7, tab7.caption)
        nb.AddPage(tab8, tab8.caption)
        nb.AddPage(tab9, tab9.caption)
        nb.AddPage(tab10, tab10.caption)
 
        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        sizer.Layout()


class GameTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #TODO: License settings, main menu settings,
        self.caption = "Game Settings"

class SpriteSheetTab(wx.Panel):
    def __init__(self, parent, context):
        wx.Panel.__init__(self, parent)
        self.context = context
        #self.context.Save SpritesheetSettings({"WallObjects" : ['', 0, 0, 0, 0], "WorldObjects" : ['', 0, 0, 0, 0], "Particles" : ['', 0, 0, 0, 0], "Characters" : ['', 0, 0, 0, 0]})
        self.spritesheets = self.context.LoadSpritesheetSettings()
        t = wx.StaticText(self, -1, "Wall Objects Spritesheet:", (20,20))
        t = wx.StaticText(self, -1, "Filepath: ", (40,40))
        t = wx.StaticText(self, -1, "tileWidth: ", (40,70))
        t = wx.StaticText(self, -1, "tileHeight: ", (40,100))
        t = wx.StaticText(self, -1, "tileXPadding: ", (40,130))
        t = wx.StaticText(self, -1, "tileYPadding: ", (40,160))

        t = wx.StaticText(self, -1, "World Objects Spritesheet:", (20,200))
        t = wx.StaticText(self, -1, "Filepath: ", (40,230))
        t = wx.StaticText(self, -1, "tileWidth: ", (40,260))
        t = wx.StaticText(self, -1, "tileHeight: ", (40,290))
        t = wx.StaticText(self, -1, "tileXPadding: ", (40,320))
        t = wx.StaticText(self, -1, "tileYPadding: ", (40,350))

        t = wx.StaticText(self, -1, "Particles Spritesheet:", (20,390))
        t = wx.StaticText(self, -1, "Filepath: ", (40,420))
        t = wx.StaticText(self, -1, "tileWidth: ", (40,450))
        t = wx.StaticText(self, -1, "tileHeight: ", (40,480))
        t = wx.StaticText(self, -1, "tileXPadding: ", (40,510))
        t = wx.StaticText(self, -1, "tileYPadding: ", (40,540))

        t = wx.StaticText(self, -1, "Characters Spritesheet:", (20,580))
        t = wx.StaticText(self, -1, "Filepath: ", (40,610))
        t = wx.StaticText(self, -1, "tileWidth: ", (40,640))
        t = wx.StaticText(self, -1, "tileHeight: ", (40,670))
        t = wx.StaticText(self, -1, "tileXPadding: ", (40,700))
        t = wx.StaticText(self, -1, "tileYPadding: ", (40,730))

        self.wallObjectFilePathTC = wx.TextCtrl(self, -1, pos=(160, 40), size=(320, 20))
        self.wallObjectTileWidthTC = wx.TextCtrl(self, -1, pos=(160, 70), size=(320, 20))
        self.wallObjectTileHeightTC = wx.TextCtrl(self, -1, pos=(160, 100), size=(320, 20))
        self.wallObjectTileXPaddingTC = wx.TextCtrl(self, -1, pos=(160, 130), size=(320, 20))
        self.wallObjectTileYPaddingTC = wx.TextCtrl(self, -1, pos=(160, 160), size=(320, 20))

        self.worldObjectFilePathTC = wx.TextCtrl(self, -1, pos=(160, 230), size=(320, 20))
        self.worldObjectTileWidthTC = wx.TextCtrl(self, -1, pos=(160, 260), size=(320, 20))
        self.worldObjectTileHeightTC = wx.TextCtrl(self, -1, pos=(160, 290), size=(320, 20))
        self.worldObjectTileXPaddingTC = wx.TextCtrl(self, -1, pos=(160, 320), size=(320, 20))
        self.worldObjectTileYPaddingTC = wx.TextCtrl(self, -1, pos=(160, 350), size=(320, 20))

        self.particleFilePathTC = wx.TextCtrl(self, -1, pos=(160, 420), size=(320, 20))
        self.particleTileWidthTC = wx.TextCtrl(self, -1, pos=(160, 450), size=(320, 20))
        self.particleTileHeightTC = wx.TextCtrl(self, -1, pos=(160, 480), size=(320, 20))
        self.particleTileXPaddingTC = wx.TextCtrl(self, -1, pos=(160, 510), size=(320, 20))
        self.particleTileYPaddingTC = wx.TextCtrl(self, -1, pos=(160, 540), size=(320, 20))

        self.characterFilePathTC = wx.TextCtrl(self, -1, pos=(160, 610), size=(320, 20))
        self.characterTileWidthTC = wx.TextCtrl(self, -1, pos=(160, 640), size=(320, 20))
        self.characterTileHeightTC = wx.TextCtrl(self, -1, pos=(160, 670), size=(320, 20))
        self.characterTileXPaddingTC = wx.TextCtrl(self, -1, pos=(160, 700), size=(320, 20))
        self.characterTileYPaddingTC = wx.TextCtrl(self, -1, pos=(160, 730), size=(320, 20))


        saveButton = wx.Button(self, -1, "Save", (700, 20))
        saveButton.Bind(wx.EVT_BUTTON, self.Save)

        self.caption = "Spritesheet Settings"
        self.Load()

    def Load(self):        
        try:
            self.wallObjectFilePathTC.SetValue(str(self.spritesheets[1][1]))
            self.wallObjectTileWidthTC.SetValue(str(self.spritesheets[1][3]))
            self.wallObjectTileHeightTC.SetValue(str(self.spritesheets[1][4]))
            self.wallObjectTileXPaddingTC.SetValue(str(self.spritesheets[1][5]))
            self.wallObjectTileYPaddingTC.SetValue(str(self.spritesheets[1][6]))

            self.worldObjectFilePathTC.SetValue(str(self.spritesheets[2][1]))
            self.worldObjectTileWidthTC.SetValue(str(self.spritesheets[2][3]))
            self.worldObjectTileHeightTC.SetValue(str(self.spritesheets[2][4]))
            self.worldObjectTileXPaddingTC.SetValue(str(self.spritesheets[2][5]))
            self.worldObjectTileYPaddingTC.SetValue(str(self.spritesheets[2][6]))

            self.particleFilePathTC.SetValue(str(self.spritesheets[3][1]))
            self.particleTileWidthTC.SetValue(str(self.spritesheets[3][3]))
            self.particleTileHeightTC.SetValue(str(self.spritesheets[3][4]))
            self.particleTileXPaddingTC.SetValue(str(self.spritesheets[3][5]))
            self.particleTileYPaddingTC.SetValue(str(self.spritesheets[3][6]))

            self.characterFilePathTC.SetValue(str(self.spritesheets[4][1]))
            self.characterTileWidthTC.SetValue(str(self.spritesheets[4][3]))
            self.characterTileHeightTC.SetValue(str(self.spritesheets[4][4]))
            self.characterTileXPaddingTC.SetValue(str(self.spritesheets[4][5]))
            self.characterTileYPaddingTC.SetValue(str(self.spritesheets[4][6]))
        except:
            pass

    def Save(self, e):
        self.context.SaveSpritesheetSettings({"WallObjects" : [self.wallObjectFilePathTC.GetValue(), self.wallObjectTileWidthTC.GetValue(), self.wallObjectTileHeightTC.GetValue(), self.wallObjectTileXPaddingTC.GetValue(), self.wallObjectTileYPaddingTC.GetValue()],
                                       "WorldObjects" : [self.worldObjectFilePathTC.GetValue(), self.worldObjectTileWidthTC.GetValue(), self.worldObjectTileHeightTC.GetValue(), self.worldObjectTileXPaddingTC.GetValue(), self.worldObjectTileYPaddingTC.GetValue()],
                                       "Particles" : [self.particleFilePathTC.GetValue(), self.particleTileWidthTC.GetValue(), self.particleTileHeightTC.GetValue(), self.particleTileXPaddingTC.GetValue(), self.particleTileYPaddingTC.GetValue()],
                                       "Characters" : [self.characterFilePathTC.GetValue(), self.characterTileWidthTC.GetValue(), self.characterTileHeightTC.GetValue(), self.characterTileXPaddingTC.GetValue(), self.characterTileYPaddingTC.GetValue()]})

class WallObjectsTab(wx.Panel):
    def __init__(self, parent, context):
        wx.Panel.__init__(self, parent)
        self.context = context
        self.activeWallObject = 0
        self.spritesheets = self.context.LoadSpritesheetSettings()
        self.wallObjects = self.context.LoadWallObjects()
        #print(str(self.spritesheets))
        #PK, scoreChangeOnTouch, scoreChangeOnAttack, healthChangeOnTouch, healthChangeOnAttack, ID,  activeImage, walkThroughPossible, actionOnTouch, actionOnAttack, isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0):
        t = wx.StaticText(self, -1, "Wall Objects: ", (20,20))
        t = wx.StaticText(self, -1, "PK: ", (40,40))
        t = wx.StaticText(self, -1, "Score Change On Touch: ", (40,70))
        t = wx.StaticText(self, -1, "Score Change On Attack: ", (40,100))
        t = wx.StaticText(self, -1, "Health Change On Touch: ", (40,130))
        t = wx.StaticText(self, -1, "Health Change On Attack: ", (40,160))
        t = wx.StaticText(self, -1, "ID: ", (40,190))
        t = wx.StaticText(self, -1, "Image: ", (40,220))
        t = wx.StaticText(self, -1, "Walk-through Possible: ", (40,250))
        t = wx.StaticText(self, -1, "Action On Touch: ", (40,280))
        t = wx.StaticText(self, -1, "Action On Attack: ", (40,310))
        t = wx.StaticText(self, -1, "Is Animated: ", (40,340))
        t = wx.StaticText(self, -1, "Adds To Character Inventory On Touch: ", (40,370))
        t = wx.StaticText(self, -1, "Adds To Character Inventory On Attack: ", (40,400))
        t = wx.StaticText(self, -1, "Destroy On Touch: ", (40,430))
        t = wx.StaticText(self, -1, "Destroy On Attack: ", (40,460))

        self.PKTC = wx.TextCtrl(self, -1, pos=(260, 40), size=(320, 20))
        self.scoreChangeOnTouchTC = wx.TextCtrl(self, -1, pos=(260, 70), size=(320, 20))
        self.scoreChangeOnAttackTC = wx.TextCtrl(self, -1, pos=(260, 100), size=(320, 20))
        self.healthChangeOnTouchTC = wx.TextCtrl(self, -1, pos=(260, 130), size=(320, 20))
        self.healthChangeOnAttackTC = wx.TextCtrl(self, -1, pos=(260, 160), size=(320, 20))

        self.IDTC = wx.TextCtrl(self, -1, pos=(260, 190), size=(320, 20))
        self.imageTC = wx.TextCtrl(self, -1, pos=(260, 220), size=(320, 20))
        self.walkThroughPossibleTC = wx.TextCtrl(self, -1, pos=(260, 250), size=(320, 20))
        self.actionOnTouchTC = wx.TextCtrl(self, -1, pos=(260, 280), size=(320, 20))
        self.actionOnAttackTC = wx.TextCtrl(self, -1, pos=(260, 310), size=(320, 20))

        self.isAnimatedTC = wx.TextCtrl(self, -1, pos=(260, 340), size=(320, 20))
        self.addsToCharacterInventoryOnTouchTC = wx.TextCtrl(self, -1, pos=(260, 370), size=(320, 20))
        self.addsToCharacterInventoryOnAttackTC = wx.TextCtrl(self, -1, pos=(260, 400), size=(320, 20))
        self.DestroyOnTouchTC = wx.TextCtrl(self, -1, pos=(260, 430), size=(320, 20))
        self.DestroyOnAttackTC = wx.TextCtrl(self, -1, pos=(260, 460), size=(320, 20))

        prevObjectButton = wx.Button(self, -1, "<", pos=(672, 20), size=(30, 26))
        prevObjectButton.Bind(wx.EVT_BUTTON, self.Prev)

        saveButton = wx.Button(self, -1, "Save", pos=(700, 20))
        saveButton.Bind(wx.EVT_BUTTON, self.Save)

        nextObjectButton = wx.Button(self, -1, ">", pos=(786, 20), size=(30, 26))
        nextObjectButton.Bind(wx.EVT_BUTTON, self.Next)

        addObjectButton = wx.Button(self, -1, "+", pos=(816, 20), size=(30, 26))
        addObjectButton.Bind(wx.EVT_BUTTON, self.Add)
        
        self.sampleImage = self.WallImage(self, self.context, self.activeWallObject)
        
        self.caption = "Wall Objects Settings"
        self.Load()

    def Save(self, e):
        self.wallObjects[self.activeWallObject].PK = self.PKTC.GetValue()
        self.wallObjects[self.activeWallObject].scoreChangeOnTouch = self.scoreChangeOnTouchTC.GetValue()
        self.wallObjects[self.activeWallObject].scoreChangeOnAttack = self.scoreChangeOnAttackTC.GetValue()
        self.wallObjects[self.activeWallObject].healthChangeOnTouch = self.healthChangeOnTouchTC.GetValue()
        self.wallObjects[self.activeWallObject].healthChangeOnAttack = self.healthChangeOnAttackTC.GetValue()

        self.wallObjects[self.activeWallObject].ID = self.IDTC.GetValue()
        self.wallObjects[self.activeWallObject].activeImage = self.imageTC.GetValue()
        self.wallObjects[self.activeWallObject].walkThroughPossible = self.walkThroughPossibleTC.GetValue()
        self.wallObjects[self.activeWallObject].actionOnTouch = self.actionOnTouchTC.GetValue()
        self.wallObjects[self.activeWallObject].actionOnAttack = self.actionOnAttackTC.GetValue()

        self.wallObjects[self.activeWallObject].isAnimated = self.isAnimatedTC.GetValue()
        self.wallObjects[self.activeWallObject].addsToCharacterInventoryOnTouch = self.addsToCharacterInventoryOnTouchTC.GetValue()
        self.wallObjects[self.activeWallObject].addsToCharacterInventoryOnAttack = self.addsToCharacterInventoryOnAttackTC.GetValue()
        self.wallObjects[self.activeWallObject].destroyOnTouch = self.DestroyOnTouchTC.GetValue()
        self.wallObjects[self.activeWallObject].destroyOnAttack = self.DestroyOnAttackTC.GetValue()
        self.context.SaveWallObjects(self.wallObjects)

    def Load(self):
        #PK, scoreChangeOnTouch, scoreChangeOnAttack, healthChangeOnTouch, healthChangeOnAttack, ID,  activeImage, walkThroughPossible, actionOnTouch, actionOnAttack, isAnimated = False, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, addsToCharacterInventoryOnAttack = 0, destroyOnAttack = 0):
        try:
            self.PKTC.SetValue(str(self.wallObjects[self.activeWallObject].PK))
            self.scoreChangeOnTouchTC.SetValue(str(self.wallObjects[self.activeWallObject].scoreChangeOnTouch))
            self.scoreChangeOnAttackTC.SetValue(str(self.wallObjects[self.activeWallObject].scoreChangeOnAttack))
            self.healthChangeOnTouchTC.SetValue(str(self.wallObjects[self.activeWallObject].healthChangeOnTouch))
            self.healthChangeOnAttackTC.SetValue(str(self.wallObjects[self.activeWallObject].healthChangeOnAttack))

            self.IDTC.SetValue(str(self.wallObjects[self.activeWallObject].ID))
            self.imageTC.SetValue(str(self.wallObjects[self.activeWallObject].activeImage))
            self.walkThroughPossibleTC.SetValue(str(self.wallObjects[self.activeWallObject].walkThroughPossible))
            self.actionOnTouchTC.SetValue(str(self.wallObjects[self.activeWallObject].actionOnTouch))
            self.actionOnAttackTC.SetValue(str(self.wallObjects[self.activeWallObject].actionOnAttack))

            self.isAnimatedTC.SetValue(str(self.wallObjects[self.activeWallObject].isAnimated))
            self.addsToCharacterInventoryOnTouchTC.SetValue(str(self.wallObjects[self.activeWallObject].addsToCharacterInventoryOnTouch))
            self.addsToCharacterInventoryOnAttackTC.SetValue(str(self.wallObjects[self.activeWallObject].addsToCharacterInventoryOnAttack))
            self.DestroyOnTouchTC.SetValue(str(self.wallObjects[self.activeWallObject].destroyOnTouch))
            self.DestroyOnAttackTC.SetValue(str(self.wallObjects[self.activeWallObject].destroyOnAttack))

        except:
            pass
        
    def Prev(self, e):
        self.activeWallObject = max(self.activeWallObject - 1, 0)
        self.sampleImage.Refresh(self, self.activeWallObject)
        self.Load()

    def Add(self, e):
        add = copy.deepcopy(self.wallObjects[self.activeWallObject])
        add.PK = str(int(add.PK) + 1)
        self.wallObjects.append(add)
        self.Next(e)

    def Next(self, e):
        self.activeWallObject = min(self.activeWallObject + 1, len(self.wallObjects) - 1)
        self.sampleImage.Refresh(self, self.activeWallObject)
        self.Load()

    class WallImage(object):
        def __init__(self, parent, context, activeWallObject):
            self.context = context
            self.wallObjects = self.context.LoadWallObjects()
            self.gfx = GfxHandler()
            self.spritesheets = self.context.LoadSpritesheetSettings()
            try:
                self.gfx.LoadGfxDictionary(file_name=str(self.spritesheets[1][1]), imageIndicator="Wall Objects", rows=8, columns=1, width=self.spritesheets[1][3], height=self.spritesheets[1][4], pictureXPadding=self.spritesheets[1][5], pictureYPadding=self.spritesheets[1][6])
            except:
                pass
            self.Refresh(parent, activeWallObject)

        def Refresh(self, parent, activeWallObject):
            self.activeWallObject = activeWallObject
            try:
                surf = self.gfx.GetImage(self.gfx.GetCoords(self.wallObjects[self.activeWallObject].activeImage, self.spritesheets[1][3], self.spritesheets[1][4], self.spritesheets[1][5], self.spritesheets[1][6], 8, 1), False)
                data = pygame.image.tostring(surf, 'RGBA')
                #png = self.gfx.GetImage(self.gfx.GetCoords(self.wallObjects[self.activeWallObject].activeImage, spritesheets[1][3], spritesheets[1][4], spritesheets[1][5], spritesheets[1][6], 8, 1), False)
                wx.StaticBitmap(parent, -1, wx.Bitmap(wx.Image(self.spritesheets[1][3], self.spritesheets[1][4], data)), (650, 50))
            except:
                pass
            
 
class WorldObjectsTab(wx.Panel):
    def __init__(self, parent, context):
        wx.Panel.__init__(self, parent)
        self.context = context
        self.activeWorldObject = 0
        self.spritesheets = self.context.LoadSpritesheetSettings()
        self.worldObjects = self.context.LoadWorldObjects()
        self.caption = "World Objects Settings"
        t = wx.StaticText(self, -1, "World Objects: ", (20,20))
        t = wx.StaticText(self, -1, "Index: ", (40,40))
        t = wx.StaticText(self, -1, "Name: ", (40,70))
        t = wx.StaticText(self, -1, "Description: ", (40,100))
        t = wx.StaticText(self, -1, "Image: ", (40,130))
        t = wx.StaticText(self, -1, "Action On Touch: ", (40,160))
        t = wx.StaticText(self, -1, "Action On Attack: ", (40,190))
        t = wx.StaticText(self, -1, "Time Between Animation Frames: ", (40,220))
        t = wx.StaticText(self, -1, "Score Change On Touch: ", (40,250))
        t = wx.StaticText(self, -1, "Score Change On Attack: ", (40,280))
        t = wx.StaticText(self, -1, "Health Change On Touch: ", (40,310))
        t = wx.StaticText(self, -1, "Health Change On Attack: ", (40,340))
        t = wx.StaticText(self, -1, "Adds To Character Inventory On Touch: ", (40,370))
        t = wx.StaticText(self, -1, "Adds To Character Inventory On Attack: ", (40,400))
        t = wx.StaticText(self, -1, "Destroy On Touch: ", (40,430))
        t = wx.StaticText(self, -1, "Destroy On Attack: ", (40,460))
        t = wx.StaticText(self, -1, "Walk Through Possible: ", (40,490))
        t = wx.StaticText(self, -1, "ID: ", (40,520))
        t = wx.StaticText(self, -1, "Default Speed: ", (40,550))
        t = wx.StaticText(self, -1, "Is Animated: ", (40,580))
        t = wx.StaticText(self, -1, "Animation Frames\n(columns on spritesheet): ", (40,610))
        t = wx.StaticText(self, -1, "Max Columns: ", (40,640))
        
        
        self.indexTC = wx.TextCtrl(self, -1, pos=(260, 40), size=(320, 20))
        self.nameTC = wx.TextCtrl(self, -1, pos=(260, 70), size=(320, 20))
        self.descriptionTC = wx.TextCtrl(self, -1, pos=(260, 100), size=(320, 20))
        #self.imageTC = wx.TextCtrl(self, -1, pos=(260, 130), size=(320, 20))
        self.actionOnTouchTC = wx.TextCtrl(self, -1, pos=(260, 160), size=(320, 20))
        self.actionOnAttackTC = wx.TextCtrl(self, -1, pos=(260, 190), size=(320, 20))
        self.timeBetweenAnimFramesTC = wx.TextCtrl(self, -1, pos=(260, 220), size=(320, 20))

        self.scoreChangeOnTouchTC = wx.TextCtrl(self, -1, pos=(260, 250), size=(320, 20))
        self.scoreChangeOnAttackTC = wx.TextCtrl(self, -1, pos=(260, 280), size=(320, 20))
        self.healthChangeOnTouchTC = wx.TextCtrl(self, -1, pos=(260, 310), size=(320, 20))
        self.healthChangeOnAttackTC = wx.TextCtrl(self, -1, pos=(260, 340), size=(320, 20))        

        
        self.addsToCharacterInventoryOnTouchTC = wx.TextCtrl(self, -1, pos=(260, 370), size=(320, 20))
        self.addsToCharacterInventoryOnAttackTC = wx.TextCtrl(self, -1, pos=(260, 400), size=(320, 20))
        self.DestroyOnTouchTC = wx.TextCtrl(self, -1, pos=(260, 430), size=(320, 20))
        self.DestroyOnAttackTC = wx.TextCtrl(self, -1, pos=(260, 460), size=(320, 20))
        
        self.walkThroughPossibleTC = wx.TextCtrl(self, -1, pos=(260, 490), size=(320, 20))
        self.IDTC = wx.TextCtrl(self, -1, pos=(260, 520), size=(320, 20))


        self.defaultSpeedTC = wx.TextCtrl(self, -1, pos=(260, 550), size=(320, 20))

        self.isAnimatedTC = wx.TextCtrl(self, -1, pos=(260, 580), size=(320, 20))
        self.animationFramesTC = wx.TextCtrl(self, -1, pos=(260, 610), size=(320, 20))
        self.maxColumnsTC = wx.TextCtrl(self, -1, pos=(260, 640), size=(320, 20))
        prevObjectButton = wx.Button(self, -1, "<", pos=(672, 20), size=(30, 26))
        prevObjectButton.Bind(wx.EVT_BUTTON, self.Prev)

        saveButton = wx.Button(self, -1, "Save", pos=(700, 20))
        saveButton.Bind(wx.EVT_BUTTON, self.Save)

        nextObjectButton = wx.Button(self, -1, ">", pos=(786, 20), size=(30, 26))
        nextObjectButton.Bind(wx.EVT_BUTTON, self.Next)
        self.sampleImage = self.WorldImage(self, self.context, self.activeWorldObject)
        
        addObjectButton = wx.Button(self, -1, "+", pos=(816, 20), size=(30, 26))
        addObjectButton.Bind(wx.EVT_BUTTON, self.Add)
        self.Load()

    def Save(self, e):
        self.worldObjects[self.activeWorldObject].PK = self.indexTC.GetValue()
        self.worldObjects[self.activeWorldObject].name = self.nameTC.GetValue()
        self.worldObjects[self.activeWorldObject].desc = self.descriptionTC.GetValue()
        #self.worldObjects[self.activeWorldObject].activeImage = self.imageTC.GetValue()
        self.worldObjects[self.activeWorldObject].actionOnTouch = self.actionOnTouchTC.GetValue()
        self.worldObjects[self.activeWorldObject].actionOnAttack = self.actionOnAttackTC.GetValue()
        self.worldObjects[self.activeWorldObject].timeBetweenAnimFrame = self.timeBetweenAnimFramesTC.GetValue()

        self.worldObjects[self.activeWorldObject].scoreChangeOnTouch = self.scoreChangeOnTouchTC.GetValue()
        self.worldObjects[self.activeWorldObject].scoreChangeOnAttack = self.scoreChangeOnAttackTC.GetValue()
        self.worldObjects[self.activeWorldObject].healthChangeOnTouch = self.healthChangeOnTouchTC.GetValue()
        self.worldObjects[self.activeWorldObject].healthChangeOnAttack = self.healthChangeOnAttackTC.GetValue()

        self.worldObjects[self.activeWorldObject].addsToCharacterInventoryOnTouch = self.addsToCharacterInventoryOnTouchTC.GetValue()
        self.worldObjects[self.activeWorldObject].addsToCharacterInventoryOnAttack = self.addsToCharacterInventoryOnAttackTC.GetValue()
        self.worldObjects[self.activeWorldObject].destroyOnTouch = self.DestroyOnTouchTC.GetValue()
        self.worldObjects[self.activeWorldObject].destroyOnAttack = self.DestroyOnAttackTC.GetValue()
        self.worldObjects[self.activeWorldObject].walkThroughPossible = self.walkThroughPossibleTC.GetValue()


        self.worldObjects[self.activeWorldObject].ID = self.IDTC.GetValue()
        print("ID " + str(self.IDTC.GetValue()))
        self.worldObjects[self.activeWorldObject].defaultSpeed = self.defaultSpeedTC.GetValue()        
        self.worldObjects[self.activeWorldObject].isAnimated = self.isAnimatedTC.GetValue()
        self.worldObjects[self.activeWorldObject].columns = self.animationFramesTC.GetValue()
        self.worldObjects[self.activeWorldObject].maxColumns = self.maxColumnsTC.GetValue()
        print("MAX COLUMNS: " + str(self.maxColumnsTC.GetValue()))

        self.context.SaveWorldObjects(self.worldObjects)
        self.Load()

    def Load(self):
        self.indexTC.SetValue(str(self.worldObjects[self.activeWorldObject].PK))
        self.nameTC.SetValue(str(self.worldObjects[self.activeWorldObject].name))
        self.descriptionTC.SetValue(str(self.worldObjects[self.activeWorldObject].desc))
        #self.imageTC.SetValue(str(self.worldObjects[self.activeWorldObject].activeImage))
        self.actionOnTouchTC.SetValue(str(self.worldObjects[self.activeWorldObject].actionOnTouch))
        self.actionOnAttackTC.SetValue(str(self.worldObjects[self.activeWorldObject].actionOnAttack))
        self.timeBetweenAnimFramesTC.SetValue(str(self.worldObjects[self.activeWorldObject].timeBetweenAnimFrame))

        self.scoreChangeOnTouchTC.SetValue(str(self.worldObjects[self.activeWorldObject].scoreChangeOnTouch))
        self.scoreChangeOnAttackTC.SetValue(str(self.worldObjects[self.activeWorldObject].scoreChangeOnAttack))
        self.healthChangeOnTouchTC.SetValue(str(self.worldObjects[self.activeWorldObject].healthChangeOnTouch))
        self.healthChangeOnAttackTC.SetValue(str(self.worldObjects[self.activeWorldObject].healthChangeOnAttack))

        self.addsToCharacterInventoryOnTouchTC.SetValue(str(self.worldObjects[self.activeWorldObject].addsToCharacterInventoryOnTouch))
        self.addsToCharacterInventoryOnAttackTC.SetValue(str(self.worldObjects[self.activeWorldObject].addsToCharacterInventoryOnAttack))
        self.DestroyOnTouchTC.SetValue(str(self.worldObjects[self.activeWorldObject].destroyOnTouch))
        self.DestroyOnAttackTC.SetValue(str(self.worldObjects[self.activeWorldObject].destroyOnAttack))
        self.walkThroughPossibleTC.SetValue(str(self.worldObjects[self.activeWorldObject].walkThroughPossible))


        self.IDTC.SetValue(str(self.worldObjects[self.activeWorldObject].ID))
        self.defaultSpeedTC.SetValue(str(self.worldObjects[self.activeWorldObject].defaultSpeed))
        self.isAnimatedTC.SetValue(str(self.worldObjects[self.activeWorldObject].isAnimated))
        self.animationFramesTC.SetValue(str(self.worldObjects[self.activeWorldObject].columns))
        self.maxColumnsTC.SetValue(str(self.worldObjects[self.activeWorldObject].maxColumns))

    def Prev(self, e):
        self.activeWorldObject = max(self.activeWorldObject - 1, 0)
        self.sampleImage.Refresh(self, self.activeWorldObject)
        self.Load()

    def Add(self, e):
        add = copy.deepcopy(self.worldObjects[self.activeWorldObject])
        add.PK = add.PK + 1
        self.worldObjects.append(add)
        self.Next(e)

    def Next(self, e):
        self.activeWorldObject = min(self.activeWorldObject + 1, len(self.worldObjects) - 1)
        self.sampleImage.Refresh(self, self.activeWorldObject)
        self.Load()

    class WorldImage(object):
        def __init__(self, parent, context, activeWorldObject):
            self.context = context
            self.worldObjects = self.context.LoadWorldObjects()
            self.gfx = GfxHandler()
            self.spritesheets = self.context.LoadSpritesheetSettings()
            try:
                self.gfx.LoadGfxDictionary(file_name=str(self.spritesheets[2][1]), imageIndicator="World Objects", rows=8, columns=1, width=self.spritesheets[2][3], height=self.spritesheets[2][4], pictureXPadding=self.spritesheets[2][5], pictureYPadding=self.spritesheets[2][6])
            except:
                pass
            self.Refresh(parent, activeWorldObject)

        def Refresh(self, parent, activeWorldObject):
            self.activeWorldObject = activeWorldObject
            try:
                surf = self.gfx.GetImage(self.gfx.GetCoords(self.worldObjects[self.activeWorldObject].activeImage, self.spritesheets[2][3], self.spritesheets[2][4], self.spritesheets[2][5], self.spritesheets[2][6], 8, 1), False)
                data = pygame.image.tostring(surf, 'RGBA')

                #png = self.gfx.GetImage(self.gfx.GetCoords(self.wallObjects[self.activeWallObject].activeImage, spritesheets[1][3], spritesheets[1][4], spritesheets[1][5], spritesheets[1][6], 8, 1), False)
                wx.StaticBitmap(parent, -1, wx.Bitmap(wx.Image(self.spritesheets[2][3], self.spritesheets[2][4], data)), (650, 50))
        
            except:
                pass
class ParticlesTab(wx.Panel):
    def __init__(self, parent, context):
        wx.Panel.__init__(self, parent)
        self.caption = "Particles Settings"
        t = wx.StaticText(self, -1, "Particles: ", (20,20))
        t = wx.StaticText(self, -1, "Index: ", (40,50))
        t = wx.StaticText(self, -1, "Name: ", (40,80))
        t = wx.StaticText(self, -1, "Weapon: ", (40,110))
        t = wx.StaticText(self, -1, "Damage: ", (40,140))
        t = wx.StaticText(self, -1, "Physics Indicator: ", (40,170))
        t = wx.StaticText(self, -1, "Physics Counter: ", (40,200))
        t = wx.StaticText(self, -1, "Width: ", (40,230))
        t = wx.StaticText(self, -1, "Height: ", (40,260))
        t = wx.StaticText(self, -1, "Default Speed: ", (40,290))
        t = wx.StaticText(self, -1, "Image: ", (40,320))
        t = wx.StaticText(self, -1, "Affected By Gravity: ", (40,350))
        t = wx.StaticText(self, -1, "Gravity Coefficient: ", (40,380))
        t = wx.StaticText(self, -1, "Bound To Camera: ", (40,410))

class CharactersTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.caption = "Characters Settings"
        t = wx.StaticText(self, -1, "Characters: ", (20,20))
        t = wx.StaticText(self, -1, "Index: ", (40,50))
        t = wx.StaticText(self, -1, "Name: ", (40,80))
        t = wx.StaticText(self, -1, "Spritesheet: ", (40,110))
        t = wx.StaticText(self, -1, "Bound To Camera: ", (40,140))
        t = wx.StaticText(self, -1, "Milliseconds On Each Leg: ", (40,170))
        t = wx.StaticText(self, -1, "Number Of Animation Frames Per Walk: ", (40,200))
        t = wx.StaticText(self, -1, "Default Speed: ", (40,230))
        t = wx.StaticText(self, -1, "Ammo: ", (40,260))
        t = wx.StaticText(self, -1, "Active Weapon: ", (40,290))
        t = wx.StaticText(self, -1, "Score: ", (40,320))
        t = wx.StaticText(self, -1, "Weapons: ", (40,350))
        t = wx.StaticText(self, -1, "Inventory: ", (40,380))
        t = wx.StaticText(self, -1, "Width: ", (40,410))
        t = wx.StaticText(self, -1, "Height: ", (40,440))
        t = wx.StaticText(self, -1, "Affected By Gravity: ", (40,470))
        t = wx.StaticText(self, -1, "Gravity Coefficient: ", (40,500))
        t = wx.StaticText(self, -1, "ID: ", (40,530))
        t = wx.StaticText(self, -1, "Is User: ", (40,560))
        t = wx.StaticText(self, -1, "Default Aggression: ", (40,590))

class WorldTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "World Settings:", (20,20))
        self.caption = "World Settings"

class LevelsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "Levels Settings:", (20,20))
        t = wx.StaticText(self, -1, "Level Selection: ", (40,50))
        t = wx.StaticText(self, -1, "Index: ", (40,80))
        t = wx.StaticText(self, -1, "Name: ", (40,110))
        t = wx.StaticText(self, -1, "Description: ", (40,140))
        t = wx.StaticText(self, -1, "Weather: ", (40,170))
        t = wx.StaticText(self, -1, "Sidescroller: ", (40,200))
        t = wx.StaticText(self, -1, "Music: ", (40,230))
        t = wx.StaticText(self, -1, "Loop Music: ", (40,260))
        t = wx.StaticText(self, -1, "Player Start X: ", (40,290))
        t = wx.StaticText(self, -1, "Player Start Y: ", (40,320))
        t = wx.StaticText(self, -1, "Start Facing X-Axis: ", (40,350))
        t = wx.StaticText(self, -1, "Start Facing Y-Axis: ", (40,380))
        t = wx.StaticText(self, -1, "Gravity: ", (40,410))
        t = wx.StaticText(self, -1, "Stick To Walls On Collision: ", (40,440))
        t = wx.StaticText(self, -1, "Width (Tiles): ", (40,470))
        t = wx.StaticText(self, -1, "Height (Tiles): ", (40,500))
        btn = wx.Button(self, -1, "Level Editor", (700, 20))
        btn.Bind(wx.EVT_BUTTON, self.OpenLevelEditor)
        self.caption = "Level Settings"

    def OpenLevelEditor(self, parent):
        pygame.init()
        exiting = False
        while exiting == False:
            #myGame = Game(int(len(screenResChoices)/2), "Window", "world.db", "C:\Tech Academy\General Dev\Python\2D Game Engine\2D-Game-Engine\Src", 0)
            myGame = Game(int(len(screenResChoices)/2), "Window", "world.db", "", 0)
            exiting = myGame.ShowMenu("Main Menu", myGame.camera)
            while myGame.exiting == False and myGame.lost == False:
                myGame.Play()
                myGame.ShowMenu("Paused", myGame.camera)
                #menuSystem = menuScreen("Main Menu", screenResSelection, difficultySelection, displayType)
                #del menuSystem
        del myGame
        pygame.quit()
        #quit()


class WeaponsTab(wx.Panel):
    def __init__(self, parent, context):
        wx.Panel.__init__(self, parent)
        self.context = context
        self.activeWeapon = 0
        self.weapons = self.context.LoadWeapons()
        t = wx.StaticText(self, -1, "Weapons Settings:", (20,20))
        t = wx.StaticText(self, -1, "Weapon Selection: ", (40,50))
        t = wx.StaticText(self, -1, "Index: ", (40,80))
        t = wx.StaticText(self, -1, "Name: ", (40,110))
        t = wx.StaticText(self, -1, "Damage: ", (40,140))
        t = wx.StaticText(self, -1, "Physics Indicator: ", (40,170))
        t = wx.StaticText(self, -1, "Pysics Count: ", (40,200))
        t = wx.StaticText(self, -1, "Width: ", (40,230))
        t = wx.StaticText(self, -1, "Height: ", (40,260))
        t = wx.StaticText(self, -1, "Speed: ", (40,290))
        t = wx.StaticText(self, -1, "Gravity Coefficient: ", (40,320))
        t = wx.StaticText(self, -1, "Generated Particle Index: ", (40,350))
        t = wx.StaticText(self, -1, "Starting Ammo: ", (40,380))
        t = wx.StaticText(self, -1, "Inventory Image Index: ", (40,410))
        t = wx.StaticText(self, -1, "World Image Index", (40,440))

        self.indexTC = wx.TextCtrl(self, -1, pos=(260, 80), size=(320, 20))
        self.nameTC = wx.TextCtrl(self, -1, pos=(260, 110), size=(320, 20))
        self.damageTC = wx.TextCtrl(self, -1, pos=(260, 140), size=(320, 20))
        self.physIndicTC = wx.TextCtrl(self, -1, pos=(260, 170), size=(320, 20))
        self.physCountTC = wx.TextCtrl(self, -1, pos=(260, 200), size=(320, 20))
        self.widthTC = wx.TextCtrl(self, -1, pos=(260, 230), size=(320, 20))
        self.heightTC = wx.TextCtrl(self, -1, pos=(260, 260), size=(320, 20))
        self.speedTC = wx.TextCtrl(self, -1, pos=(260, 290), size=(320, 20))
        self.gravityCoeffTC = wx.TextCtrl(self, -1, pos=(260, 320), size=(320, 20))
        self.genParticleIndexTC = wx.TextCtrl(self, -1, pos=(260, 350), size=(320, 20))
        self.startingAmmoTC = wx.TextCtrl(self, -1, pos=(260, 380), size=(320, 20))
        self.inventoryImageIndexTC = wx.TextCtrl(self, -1, pos=(260, 410), size=(320, 20))
        self.worldImageIndexTC = wx.TextCtrl(self, -1, pos=(260, 440), size=(320, 20))
        self.caption = "Weapons Settings"

        prevObjectButton = wx.Button(self, -1, "<", pos=(672, 20), size=(30, 26))
        prevObjectButton.Bind(wx.EVT_BUTTON, self.Prev)

        saveButton = wx.Button(self, -1, "Save", pos=(700, 20))
        saveButton.Bind(wx.EVT_BUTTON, self.Save)

        nextObjectButton = wx.Button(self, -1, ">", pos=(786, 20), size=(30, 26))
        nextObjectButton.Bind(wx.EVT_BUTTON, self.Next)
        #self.sampleImage = self.WorldImage(self, self.context, self.activeWeapon)
        if self.weapons != []:
            self.Load()

    def Save(self, e):
        if self.weapons == []:
            self.weapons = [Weapon(0, self.nameTC.GetValue(), self.damageTC.GetValue(), self.startingAmmoTC.GetValue(), self.physIndicTC.GetValue(), self.physCountTC.GetValue(), self.widthTC.GetValue(), self.heightTC.GetValue(), self.speedTC.GetValue(), 0, self.genParticleIndexTC.GetValue(), self.genParticleIndexTC.GetValue(), self.inventoryImageIndexTC.GetValue(), self.worldImageIndexTC.GetValue())]
        else:
            self.weapons[self.activeWeapon].index = self.indexTC.GetValue()
            self.weapons[self.activeWeapon].name = self.nameTC.GetValue()
            self.weapons[self.activeWeapon].damage = self.damageTC.GetValue()
            self.weapons[self.activeWeapon].physIndic = self.physIndicTC.GetValue()
            self.weapons[self.activeWeapon].phsyicsCount = self.physCountTC.GetValue()
            self.weapons[self.activeWeapon].generateBulletWidth = self.widthTC.GetValue()
            self.weapons[self.activeWeapon].generateBulletHeight = self.heightTC.GetValue()
            self.weapons[self.activeWeapon].generateBulletSpeed = self.speedTC.GetValue()
            self.weapons[self.activeWeapon].gravityCoefficient = self.gravityCoeffTC.GetValue()
            self.weapons[self.activeWeapon].generateParticleIndex = self.genParticleIndexTC.GetValue()
            self.weapons[self.activeWeapon].ammo = self.startingAmmoTC.GetValue()
            self.weapons[self.activeWeapon].inventoryImageIndex = self.inventoryImageIndexTC.GetValue()
            self.weapons[self.activeWeapon].worldImageIndex = self.worldImageIndexTC.GetValue()
        self.context.SaveWeapons(self.weapons)
        self.Load()

    def Load(self):
        self.indexTC.SetValue(str(self.weapons[self.activeWeapon].PK))
        self.nameTC.SetValue(str(self.weapons[self.activeWeapon].name))
        self.damageTC.SetValue(str(self.weapons[self.activeWeapon].damage))
        self.physIndicTC.SetValue(str(self.weapons[self.activeWeapon].physIndic))
        self.physCountTC.SetValue(str(self.weapons[self.activeWeapon].physicsCount))
        self.widthTC.SetValue(str(self.weapons[self.activeWeapon].generateBulletWidth))
        self.heightTC.SetValue(str(self.weapons[self.activeWeapon].generateBulletHeight))
        self.speedTC.SetValue(str(self.weapons[self.activeWeapon].generateBulletSpeed))
        self.gravityCoeffTC.SetValue(str(self.weapons[self.activeWeapon].gravityCoefficient))
        self.genParticleIndexTC.SetValue(str(self.weapons[self.activeWeapon].generateParticleIndex))
        self.startingAmmoTC.SetValue(str(self.weapons[self.activeWeapon].ammo))
        self.inventoryImageIndexTC.SetValue(str(self.weapons[self.activeWeapon].inventoryImageIndex))
        self.worldImageIndexTC.SetValue(str(self.weapons[self.activeWeapon].worldImageIndex))

    def Prev(self, e):
        self.activeWeapon =  self.activeWeapon - 1
        #self.sampleImage.Refresh(self, self.activeWeapon)
        self.Load()

    def Next(self, e):
        self.activeWeapon =  self.activeWeapon + 1
        #self.sampleImage.Refresh(self, self.activeWeapon)
        self.Load()

    class WorldImage(object):
        def __init__(self, parent, context, activeWorldObject):
            self.context = context
            self.worldObjects = self.context.LoadWorldObjects()
            self.gfx = GfxHandler()
            self.spritesheets = self.context.LoadSpritesheetSettings()
            self.gfx.LoadGfxDictionary(file_name=str(self.spritesheets[2][1]), imageIndicator="World Objects", rows=8, columns=1, width=self.spritesheets[2][3], height=self.spritesheets[2][4], pictureXPadding=self.spritesheets[2][5], pictureYPadding=self.spritesheets[2][6])
            self.Refresh(parent, activeWorldObject)

        def Refresh(self, parent, activeWorldObject):
            self.activeWorldObject = activeWorldObject
            surf = self.gfx.GetImage(self.gfx.GetCoords(self.worldObjects[self.activeWorldObject].activeImage, self.spritesheets[2][3], self.spritesheets[2][4], self.spritesheets[2][5], self.spritesheets[2][6], 8, 1), False)
            data = pygame.image.tostring(surf, 'RGBA')

            #png = self.gfx.GetImage(self.gfx.GetCoords(self.wallObjects[self.activeWallObject].activeImage, spritesheets[1][3], spritesheets[1][4], spritesheets[1][5], spritesheets[1][6], 8, 1), False)
            wx.StaticBitmap(parent, -1, wx.Bitmap(wx.Image(self.spritesheets[2][3], self.spritesheets[2][4], data)), (650, 50))


class SoundsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #TODO: License settings, main menu settings,
        self.caption = "Sound Settings"


if __name__ == "__main__":
    app = wx.App()
    WorldEditorWindow("Game Studio", 1080, 852, World("", "world.db") ).Show()
    app.MainLoop()
