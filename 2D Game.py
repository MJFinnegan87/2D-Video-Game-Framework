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
PI = math.pi


class GfxHandler(object):
    def __init__(self):
        self.gfxDictionary = {}

    def loadGfxDictionary(self, file_name="", imageIndicator="", rows=0, columns=0, width=0, height=0, pictureXPadding=0, pictureYPadding=0):
        self.spriteSheet = pygame.image.load(file_name)
        imgTransparency = True
        
        if imageIndicator == "World Tiles":
            imgTransparency = False
        self.gfxDictionary.update({imageIndicator:{}}) #NESTED HASHTABLE

        for j in xrange(rows):
            for k in xrange(columns):
                #self.gfxDictionary[(j*k) + j] = self.getImage(self.getCoords((j*k) + j, width, height, pictureXPadding, pictureYPadding, rows, columns))
                self.gfxDictionary[imageIndicator].update({(j*columns) + k:self.getImage(self.getCoords((j*columns) + k, width, height, pictureXPadding, pictureYPadding, rows, columns), imgTransparency)})

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

    def drawLargeMessage(self, text, myGameDisplay, myColor):
        largeText = pygame.font.Font("freesansbold.ttf", 135)
        textSurf, textRect = self.textObjects(text, largeText, myColor)
        textRect.center = ((displayWidth/2), (displayHeight/2))
        myGameDisplay.blit(textSurf, textRect)
        pygame.display.update()
        time.sleep(2)

    def drawSmallMessage(self, text, lineNumber, myGameDisplay, myColor, displayWidth):
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
    
    def drawObjectsAndParticles(self, particles, gameDisplay, camera, tileHeight, tileWidth, character):
        self.drawImg(self.gfxDictionary[character.imagesGFXNameDesc][character.imgDirectionIndex+(character.numberOfDirectionsFacingToDisplay*character.imgLegIndex)], (character.x, character.y), gameDisplay)
        for i in xrange(len(particles)):
            if particles[i].name == "User Bullet":
                #print "x: " + str((1 + cameraViewX + (-cameraViewToScreenPxlOffsetX/float(tileWidth)) - particles[i][2]) * -tileWidth)
                #print "y: " + str((1 + cameraViewY + (-cameraViewToScreenPxlOffsetY/float(tileHeight)) - particles[i][3]) * -tileHeight)
                if ((1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particles[i].xTile) * -tileWidth) + particles[i].width > 0 and (1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particles[i].xTile) * -tileWidth < camera.displayWidth:
                    #self.drawObject("bullet" + str(particles[i][1]) + ".png", (1 + cameraViewX + (-cameraViewToScreenPxlOffsetX/float(tileWidth)) - particles[i][2]) * -tileWidth, (1 + cameraViewY + (-cameraViewToScreenPxlOffsetY/float(tileHeight)) - particles[i][3]) * -tileHeight, gameDisplay)
                    #print math.acos(particles[i][4]/float((particles[i][4]**2 + particles[i][5]**2)**.5))
                    #img = pygame.transform.rotate(gfx.gfxDictionary["Particles"][particles[i][1]], (180*math.acos(particles[i][4]/float((particles[i][4]**2 + particles[i][5]**2)**.5)))/PI)
                    self.drawImg(particles[i].img, ((1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particles[i].xTile) * -tileWidth, (1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) - particles[i].yTile) * -tileHeight), gameDisplay)

    def drawWorldInCameraView(self, tileSet, camera, tileWidth, tileHeight, thisLevelMap, gameDisplay, timeElapsedSinceLastFrame=0):
        for i in xrange(int(camera.displayWidth/float(tileWidth))+2):
            for j in xrange(int(camera.displayHeight/float(tileHeight))+2):
                try:
                    imgToDraw, thisLevelMap = self.determineLocationImg(thisLevelMap, i, j, camera.viewX, camera.viewY, tileSet, timeElapsedSinceLastFrame)
                    if imgToDraw != "":
                        self.drawImg(imgToDraw,
                          (((i-1)*tileWidth)+camera.viewToScreenPxlOffsetX,
                          ((j-1)*tileHeight)+camera.viewToScreenPxlOffsetY,
                          (((i-1)*tileWidth)+camera.viewToScreenPxlOffsetX)+ tileWidth,
                          (((j-1)*tileHeight)+camera.viewToScreenPxlOffsetY) + tileHeight), gameDisplay)
                except:
                    pass
        return thisLevelMap

    def determineLocationImg(self, thisLevelMap, i, j, viewX, viewY, tileSet, timeElapsedSinceLastFrame):
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

class LogicHandler(object):
    def handleHeyPressAndGameEvents(self, exiting, lost, character):
        #HANDLE KEY PRESS/RELEASE/USER ACTIONS
        enterPressed = False
        keys = pygame.key.get_pressed()
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

        return exiting, lost, character, enterPressed

    def cameraWorldEdgeCollisionCheck(self, thisLevelMap, camera, character, tileWidth, tileHeight):
        #SNAP CAMERA TO THE EDGE OF THE WORLD IF PAST IT
        camera.atWorldEdgeX = False
        camera.atWorldEdgeY = False
            #camera X  +      tiles on screen              +        frac. person next move         +   frac camera X                                         
        if (1 + camera.viewX + (camera.displayWidth/float(tileWidth)) + (character.deltaX/float(tileWidth)) - (camera.viewToScreenPxlOffsetX/float(tileWidth)) >= len(thisLevelMap[0])) and character.deltaX > 0:
            camera.viewToScreenPxlOffsetX = (float(float(camera.displayWidth/float(tileWidth)) - int(camera.displayWidth/float(tileWidth))))*tileWidth
            camera.viewX = int(len(thisLevelMap[0]) - int(camera.displayWidth/float(tileWidth))) - 1
            camera.atWorldEdgeX = True
        else:
            if (1 + camera.viewX - camera.viewToScreenPxlOffsetX/float(tileWidth) + (character.deltaX/float(tileWidth)) <= 0 and character.deltaX <0):
                camera.viewX = -1
                camera.viewToScreenPxlOffsetX = 0
                camera.atWorldEdgeX = True
        
        if (1 + camera.viewY + (camera.displayHeight/float(tileHeight)) + (character.deltaY/float(tileHeight)) - (camera.viewToScreenPxlOffsetY/float(tileHeight)) >= len(thisLevelMap)) and character.deltaY > 0:
            camera.viewToScreenPxlOffsetY = (float(float(camera.displayHeight/float(tileHeight)) - int(camera.displayHeight/float(tileHeight))))*tileHeight
            camera.viewY = int(len(thisLevelMap) - int(camera.displayHeight/float(tileHeight))) - 1
            camera.atWorldEdgeY = True
        else:
            if (1 + camera.viewY - camera.viewToScreenPxlOffsetY/float(tileHeight) + (character.deltaY/float(tileHeight)) <= 0 and character.deltaY < 0):
                camera.viewY = -1
                camera.viewToScreenPxlOffsetY = 0
                camera.atWorldEdgeY = True
        return camera

    def characterWallCollisionTest(self, thisLevelMap, camera, character, tileHeight, tileWidth, gravityAppliesToWorld):
        character.deltaY = character.deltaY + character.gravityYDelta

        #This acts as a buffer to allow user to not get up against floor/ceiling
        #because the distance the user will travel over the next frame cannot
        #be known with absolute certainty because it is a function of the speed
        #at which the next frame is drawn. This prevents clipping by making
        #a judgement call that the next frame won't likely be drawn twice as slow as,
        #or longer, than this frame was drawn.

        #character.speed = character.speed*2

        
        #CHARACTER<->WALL COLLISION DETECTION:
        #COLLISION DETECTION ACTUALLY HAS TO CHECK 2 DIRECTIONS FOR EACH OF THE 4 CORNERS FOR 2D MOVEMENT:
        #EACH OF THESE 2x4 CHECKS ARE LABLED BELOW AND CODE IS MARKED INDICATING WHICH
        #CORNER CHECK IS OCCURRING. THIS WOULD BE GOOD ENOUGH IF WE JUST STOPPED THE CHARACTER
        #ON COLLISION. FOR A BETTER USER EXPERIENCE, IF USER IS MOVING IN 2 DIRECTIONS (FOR EX LEFT + DOWN),
        #BUT ONLY ONE DIRECTION (FOR EX: LEFT) COLLIDES, THEN WE WANT TO KEEP THE USER MOVING
        #IN THE 1 GOOD DIRECTION ONLY. THIS REQUIRES 2 COLLISION CHECKS @ EACH OF THE 8 POINTS BECAUSE
        #THE OUTCOME AND REMEDIATION OF A COLLISION CHECK ON ONE SIDE AFFECTS BY THE OUTCOME AND REMEDIATION
        #OF THE NEXT COLLISION CHECK @ 90deg/270deg DIFFERENT DIRECTION AND BECAUSE PLAYER'S CHARACTER IS SMALLER
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


        character.yok = 1
        character.xok = 1
        needToRevert = 0
        #COLLISION CHECK @ C or @ D or @ H or @ G
        if (character.deltaX > 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + character.deltaY + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (character.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+(-character.personXDeltaButScreenOffset + character.deltaX)+ character.personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (character.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + character.deltaY + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (character.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+(-character.personXDeltaButScreenOffset + character.deltaX)+ character.personXDeltaButScreenOffset)/float(tileWidth)))])) or ((character.deltaX)< 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + character.deltaY + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+(-character.personXDeltaButScreenOffset + character.deltaX)+ character.personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (character.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + character.deltaY + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+(-character.personXDeltaButScreenOffset + character.deltaX)+ character.personXDeltaButScreenOffset)/float(tileWidth)))])):
            tempxok = character.xok #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
            temppersonXDeltaButScreenOffset = character.personXDeltaButScreenOffset #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
            temppersonXDelta = character.deltaX #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
            character.xok = 0
            character.personXDeltaButScreenOffset = 0
            character.deltaX = 0
            needToRevert = 1

        #COLLISION CHECK @ A or @ B or @ F or @ E 
        #IF WE HANDLED A COLLISION @ C, D, H, OR G OR NO COLLISION @ C, D, H, OR G OCCURED,
        #WOULD A COLLISION OCCUR @ A, B, F, OR E ??? (NOTE HOW THIS FORMULA IS DEPENDENT ON VARS ABOVE THAT WERE CHANGED!)
        
        #if (character.deltaY < 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y - (character.personYDeltaButScreenOffset + character.speed) + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+character.deltaX + character.personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y - (character.personYDeltaButScreenOffset + character.speed) + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (character.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+character.deltaX + character.personXDeltaButScreenOffset)/float(tileWidth)))])) or (character.deltaY > 0 and (thisLevelMap[int(1 + (character.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + (-character.personYDeltaButScreenOffset + character.speed + self.getNextGravityApplicationToWorld(character.gravityYDelta, character.timeSpentFalling, tileHeight)) + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+character.deltaX + character.personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (character.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + (-character.personYDeltaButScreenOffset + character.speed + self.getNextGravityApplicationToWorld(character.gravityYDelta, character.timeSpentFalling, tileHeight)) + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (character.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+character.deltaX + character.personXDeltaButScreenOffset)/float(tileWidth)))])):
        if (character.deltaY < 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y - (character.personYDeltaButScreenOffset - character.deltaY) + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+character.deltaX + character.personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y - (character.personYDeltaButScreenOffset - character.deltaY) + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (character.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+character.deltaX + character.personXDeltaButScreenOffset)/float(tileWidth)))])) or (character.deltaY > 0 and (thisLevelMap[int(1 + (character.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + (-character.personYDeltaButScreenOffset + character.deltaY + self.getNextGravityApplicationToWorld(character.gravityYDelta, character.timeSpentFalling, tileHeight)) + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+character.deltaX + character.personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (character.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + (-character.personYDeltaButScreenOffset + character.deltaY + self.getNextGravityApplicationToWorld(character.gravityYDelta, character.timeSpentFalling, tileHeight)) + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (character.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+character.deltaX + character.personXDeltaButScreenOffset)/float(tileWidth)))])):
            character.yok = 0
            character.personYDeltaButScreenOffset = 0
            character.deltaY = 0
            if gravityAppliesToWorld == True and character.gravityYDelta != 0 and character.deltaY + self.getNextGravityApplicationToWorld(character.gravityYDelta, character.timeSpentFalling, tileHeight) > 0:
                character.gravityYDelta = 0
                character.timeSpentFalling = 0
                character.deltaY = -1
                
        #RESET 1ST COLLISION CHECK PARAMATERS B/C NOW,
        #WE DON'T KNOW IF A COLLISION @ C or @ D or @ H or @ G WILL OCCUR
        #BECAUSE WE MAY HAVE HANDLED A COLLISION @ A, B, F, OR E.
        #KNOWING THIS BEFOREHAND AFFECTS THE OUTCOME OF COLLISION TEST.
        if needToRevert == 1:
            character.xok = tempxok
            character.personXDeltaButScreenOffset = temppersonXDeltaButScreenOffset
            character.deltaX = temppersonXDelta

        #COLLISION CHECK @ C or @ D or @ H or @ G
        #NOW TEST FOR COLLISION @ C, D, H, OR G NOW KNOWING THAT WE HANDLED MAY HAVE HANDLED A COLLISION @ C, D, H, OR G
        #LIKEWISE, THIS FORMULA IS DEPENDENT ON VARS IN 2ND SECTION THAT CHANGED
        if ((character.deltaX)> 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + character.deltaY + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (character.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+(-character.personXDeltaButScreenOffset + character.deltaX)+ character.personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (character.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + character.deltaY + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + (character.width/float(tileWidth)) + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+(-character.personXDeltaButScreenOffset + character.deltaX)+ character.personXDeltaButScreenOffset)/float(tileWidth)))])) or ((character.deltaX)< 0 and (thisLevelMap[int(1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + character.deltaY + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+(-character.personXDeltaButScreenOffset + character.deltaX)+ character.personXDeltaButScreenOffset)/float(tileWidth)))] or thisLevelMap[int(1 + (character.height/float(tileHeight)) + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + ((character.y + character.deltaY + character.personYDeltaButScreenOffset)/float(tileHeight)))][int(1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + ((character.x+(-character.personXDeltaButScreenOffset + character.deltaX)+ character.personXDeltaButScreenOffset)/float(tileWidth)))])):
            character.xok = 0
            character.personXDeltaButScreenOffset = 0
            character.deltaX = 0

        return character


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

    def screenSynchWithCharacterMovement(self, character, camera, tileHeight, tileWidth, thisLevelMapWidth, thisLevelMapHeight):

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
        if character.xok == 1 and camera.atWorldEdgeX == False and ((character.deltaX < 0 and character.x + character.deltaX < (1*camera.displayWidth)/3.0) or (character.deltaX >0 and character.x + character.deltaX > (2*camera.displayWidth)/3.0)):
            camera.viewToScreenPxlOffsetX = camera.viewToScreenPxlOffsetX - character.deltaX #MOVE CAMERA ALONG X AXIS
            character.personXDeltaButScreenOffset = -character.deltaX #KEEP PLAYER'S CHARACTER FIXED @ MIDDLE 9TH EDGE
        else:
            character.personXDeltaButScreenOffset = 0

        if character.yok == 1 and camera.atWorldEdgeY == False and ((character.deltaY < 0 and character.y + character.deltaY < (1*camera.displayHeight)/3.0) or (character.deltaY >0 and character.y + character.deltaY > (2*camera.displayHeight)/3.0)):
            camera.viewToScreenPxlOffsetY = camera.viewToScreenPxlOffsetY - character.deltaY #MOVE CAMERA ALONG Y AXIS
            character.personYDeltaButScreenOffset = -character.deltaY #KEEP PLAYER'S CHARACTER FIXED @ MIDDLE 9TH EDGE
        else:
            character.personYDeltaButScreenOffset = 0

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
            
        if character.xok == 1:
            character.x = character.x + character.deltaX + character.personXDeltaButScreenOffset #MOVE USER'S CHARACTER, BUT DON'T MOVE HIM IN ONE DIRECTION IF THE SCREEN SCROLL IS ALSO MOVING IN THAT DIRECTION
            character.xTile = 1 + camera.viewX + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + (character.x/float(tileWidth)) #0 BASED, JUST LIKE THE ARRAY, THIS IS LEFT MOST POINT OF USER'S CHAR
        if character.yok == 1:
            character.y = character.y + character.deltaY + character.personYDeltaButScreenOffset #MOVE USER'S CHARACTER, BUT DON'T MOVE HIM IN ONE DIRECTION IF THE SCREEN SCROLL IS ALSO MOVING IN THAT DIRECTION
            character.yTile = 1 + camera.viewY + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + (character.y/float(tileHeight)) #0 BASED, JUST LIKE THE ARRAY, THIS IS TOP MOST POINT OF USER'S CHAR
        return character, camera

    def generateParticles(self, particles, character, tileHeight, tileWidth, gfx):
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

    def moveParticlesAndHandleParticleCollision(self, particles, thisLevelMap):
        #MOVE PARTICLES, OR DELETE THEM IF THEY REACH WORLD END
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

    def applyGravityToWorld(self, character, tileHeight):
        return (min(character.gravityYDelta + (.00005 * (character.timeSpentFalling**2)), tileHeight / 3.0)), character.timeSpentFalling + 1

    def getNextGravityApplicationToWorld(self, gravityYDelta, timeSpentFalling, tileHeight):
        character = Character("Temp")
        character.gravityYDelta = gravityYDelta
        character.timeSpentFalling = timeSpentFalling
        a, b = self.applyGravityToWorld(character, tileHeight)
        del character
        return a

    def manageTimeAndFrameRate(self, lastTick, clock, FPSLimit):
        timeElapsedSinceLastFrame = clock.get_time() - lastTick
        lastTick = clock.tick(FPSLimit)
        return timeElapsedSinceLastFrame

    def alterAllSpeeds(self, timeElapsedSinceLastFrame, particleList, character):
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
            particleList[i].dx, particleList[i].dy = self.diagSpeedFix(particleList[i].dx, particleList[i].dy, particleList[i].speed)
        if timeElapsedSinceLastFrame < 2000:
            character.speed = character.defaultSpeed * timeElapsedSinceLastFrame
            
        character.deltaX, character.deltaY = self.diagSpeedFix(character.deltaX, character.deltaY, character.speed)
        
        return particleList, character

    def determineCharPicBasedOnDirectionFacing(self, character):
        if character.xFacing == 0 and character.yFacing > 0:
            #down
            character.imgDirectionIndex = 0
        if character.xFacing == 0 and character.yFacing < 0:
            #up
            character.imgDirectionIndex = 1
        if character.xFacing > 0 and character.yFacing == 0:
            #right
            character.imgDirectionIndex = 2
        if character.xFacing < 0 and character.yFacing == 0:
            #left
            character.imgDirectionIndex = 3
        if character.xFacing > 0 and character.yFacing > 0:
            #down right
            character.imgDirectionIndex = 4
        if character.xFacing < 0 and character.yFacing < 0:
            #up left
            character.imgDirectionIndex = 5
        if character.xFacing > 0 and character.yFacing < 0:
            #up right
            character.imgDirectionIndex = 6
        if character.xFacing < 0 and character.yFacing > 0:
            #down left
            character.imgDirectionIndex = 7

        #for each enemy in enemies:
            #Determine this enemy's directionImgIndex
        
        return character

    def determineCharPicBasedOnWalkOrMovement(self, character, millisecondsSinceLastFrame):
        if character.deltaX == 0 and character.deltaY == 0:
            character.imgLegIndex = 0
            character.millisecondsOnThisLeg = 0
        else:
            if (character.millisecondsOnThisLeg >= character.millisecondsOnEachLeg):
                character.imgLegIndex = (character.imgLegIndex + 1) % character.numberOfFramesAnimPerWalk
                character.millisecondsOnThisLeg = 0
            else:
                character.millisecondsOnThisLeg = character.millisecondsOnThisLeg + millisecondsSinceLastFrame

            #for each enemy in enemies:
                #Determine this enemy's legImgIndex
        
        return character

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
        self.myHighScores = self.myHighScoreDatabase.loadHighScores()
        self.difficultyChoices = self.myHighScoreDatabase.difficulties

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
                
            self.personYDeltaWas = self.userCharacter.deltaY
            self.personXDeltaWas = self.userCharacter.deltaX
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
        #self.currentLevel, self.activeWeapon, self.enemiesAlive, self.myEnemies, self.myProjectiles = self.menuGameEventHandler.addGameObjects(
            #self.enemiesAlive, self.currentLevel, self.activeWeapon, self.myEnemies, self.starProbabilitySpace, self.starDensity, self.starMoveSpeed, self.myProjectiles, self.displayWidth)
        #self.starMoveSpeed = self.menuGameEventHandler.adjustStarMoveSpeed(self.maximumStarMoveSpeed, self.numberOfStarSpeeds)
        #self.myProjectiles, self.myEnemies, self.myHealth, self.score, self.enemiesAlive, self.y, self.ammo = self.menuGameEventHandler.moveAndDrawProjectilesAndEnemies(
            #self.myProjectiles, self.myEnemies, self.myHealth, self.score, self.enemiesAlive, self.x, self.y, self.rocketWidth, self.rocketHeight, self.difficultySelection, self.displayWidth, self.displayHeight, self.ammo, self.starMoveSpeed)
        #self.menuGameEventHandler.drawObject(myCharacter, self.x, self.y)

    def getKeyPress(self):
        self.exiting, self.lost, self.userCharacter, self.enterPressed = self.logic.handleHeyPressAndGameEvents(self.exiting, self.lost, self.userCharacter)

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
            #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.character.speed)))
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
            #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.character.speed)))
            self.textRect.center = ((self.displayWidth/2.0), ((self.i * self.mainMenuItemMargin) + self.screenMoveCounter - self.displayHeight/2.0))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def displayHighScoresMenu(self):
        if self.menuSelectionIndex == 0:
            self.rgb = (self.colorIntensity, 0, 0)
        else:
            self.rgb = (255, 255, 255)
        self.textSurf, self.textRect = self.gfx.textObjects("<<  " + self.difficultyChoices[self.highScoreDifficulty] + " High Scores  >>", self.smallText, self.rgb)
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
                    #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.character.speed)))
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
                    #print str(self.highScoreDifficulty)
                    self.text = str(self.myHighScores[self.highScoreDifficulty][self.i][self.j])
                    self.textSurf, self.textRect = self.gfx.textObjects(self.text, self.smallText, self.rgb)
                    #self.textRect.center = ((self.displayWidth/2), (self.displayHeight/2 - self.i*(self.character.speed)))
                    self.textRect.center = ((self.displayWidth*((self.j+1)/6.0)), ((self.i * self.mainMenuItemMargin) + self.displayHeight/2.0))
                self.gameDisplay.blit(self.textSurf, self.textRect)

    def handleUserInputMainMenu(self):
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

    def handleUserInputSettingsMenu(self):
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

    def handleUserInputCreditsMenu(self):
        if self.enterPressed == True:
            self.screenMoveCounter = 0
            self.menuDirectory = "Main"

    def handleUserInputHowToMenu(self):
        if self.enterPressed == True:
            self.screenMoveCounter = 0
            self.menuDirectory = "Main"

    def handleUserInputHighScoresMenu(self):
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
        self.databaseName = "High_Scores.db"
        
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
                #self.a = self.a.append(self.fillInBlankHighScores(self.a))
                #self.a.remove([])
                #print self.a
                self.highScoresArray.insert(self.loadCounter, self.a)
        except:
            self.initializeDatabase()
        
        self.connection.close()
        return self.highScoresArray

    def initializeDatabase(self):
        self.connection = sqlite3.connect(self.databaseName)
        self.c = self.connection.cursor()
        for difficulty in self.difficulties:
            self.c.execute("DROP TABLE IF EXISTS " + difficulty + "HighScoreTable")
            self.c.execute("CREATE TABLE " + difficulty + "HighScoreTable(scoreRecordPK INT, Name TEXT, Score INT, State TEXT, Country TEXT)")

        for self.loadCounter in xrange(len(self.difficulties)):
            #self.highScoresArray.append([])
            self.highScoresArray.insert(self.loadCounter, self.fillInBlankHighScores(self.highScoresArray[self.loadCounter]))
            #self.highScoresArray = self.fillInBlankHighScores(self.highScoresArray[self.loadCounter])
        self.highScoresArray.remove([])
        for self.loadCounter in xrange(len(self.difficulties)):
            self.updateHighScoresForThisDifficulty(self.highScoresArray[self.loadCounter], self.loadCounter)
        self.connection.close()
        return self.highScoresArray
                
    def updateHighScoresForThisDifficulty(self, workingArray, difficulty):
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
            self.initializeDatabase()
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

class Character(WorldObject):
    def __init__(self, name, xFacing = 0, yFacing = 0, xTile = 0, yTile = 0, x = 0, y = 0, deltaX = 0, deltaY = 0, timeSpentFalling = 0, gravityYDelta = 0,  imgDirectionIndex = 0, imgLegIndex = 0, millisecondsOnEachLeg = 250, numberOfFramesAnimPerWalk = 3, defaultSpeed = .5, ammo = 1000, activeWeapon = 0, score = 0, weapons = [], inventory = [], width = 32, height = 32, personXDeltaButScreenOffset = 0, personYDeltaButScreenOffset = 0, shotsFiredFromMe = False):
        self.name = name
        self.numberOfFramesAnimPerWalk = numberOfFramesAnimPerWalk #3
        self.numberOfDirectionsFacingToDisplay = 8
        self.imagesGFXName = "userplayer.png"
        self.imagesGFXNameDesc = "User Player"
        self.imagesGFXRows = self.numberOfDirectionsFacingToDisplay
        self.imagesGFXColumns = self.numberOfFramesAnimPerWalk
        self.xFacing = xFacing
        self.yFacing = yFacing
        self.xTile = xTile
        self.yTile = yTile
        self.x = x
        self.y = y
        self.xok = 0
        self.yok = 0 
        self.deltaX = deltaX
        self.deltaY = deltaY
        self.timeSpentFalling = timeSpentFalling #This is important to track because falling velocity due to gravity is non-linear
        self.gravityYDelta = 0
        self.imgDirectionIndex = imgDirectionIndex #IMAGE INDICIES REFERENCE IMAGE BECAUSE IMAGE WILL CHANGE THROUGHOUT LIFE OF THE OBJECT
        self.imgLegIndex = imgLegIndex
        self.millisecondsOnEachLeg = millisecondsOnEachLeg #250
        self.millisecondsOnThisLeg = 0
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
        self.personXDeltaButScreenOffset = personXDeltaButScreenOffset
        self.personYDeltaButScreenOffset = personYDeltaButScreenOffset
        self.shotsFiredFromMe = shotsFiredFromMe
        self.weapons = weapons


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
        self.imagesGFXName = "bullets.png"
        self.imagesGFXNameDesc = "Bullets"
        self.imagesGFXRows = 4
        self.imagesGFXColumns = 1
        self.weapon = weapon


class Camera(object):
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
        #TODO: Resolution/screen size can be larger than the world itself, 
        #   thus the world must be centered for attractive appearance

class Game(object):
    def __init__(self, screenResSelection, fullScreen):        
        self.clock = pygame.time.Clock()
        self.camera = Camera(screenResSelection, fullScreen)
        self.gameDisplay = self.camera.updateScreenSettings()
        
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

        #self.DEFAULTBULLETSPEED = .01 #BULLET SPEED IN WORLD TILES/MILLISECOND

        self.tileSheetRows = 9
        self.tileSheetColumns = 1
        self.tileWidth = 64 * self.camera.zoom
        self.tileHeight = 64 * self.camera.zoom
        self.tileXPadding = 0
        self.tileYPadding = 0
        self.enemiesAlive = 0
        self.currentLevel = 0
        
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

        #WORLD OBJECTS ARE STORED IN AN ARRAY THAT REPRESENTS X, Y COORDINATES OF THE LEVEL. LOCATIONS WITH NO WORLD OBJECTS ARE EMPTY.
        #THIS METHOD IS PREFERRED TO STORING AN ARRAY OF OBJECTS EACH CONTAINING AN X, Y PROPERTY BECAUSE THIS WAY ALLOWS MORE CODE REUSE,
        #AND ONLY ITERATING OVER SECTION OF THE LEVEL THAT IS VISIBLE TO THE CAMERA'S POINT OF VIEW, RATHER THAN ITERATING OVER EACH
        #LEVEL OBJECT AND TESTING IF ITS X, Y COORDINATES FALL WITHIN THE CAMERA'S POINT OF VIEW.
        self.thisLevelObjects = [[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
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
                            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]]                   

        #self.personImgDirectionIndex = 0
        #self.personImgLegIndex = 0
        #self.millisecondsOnEachLeg = 250
        #self.millisecondsOnThisLeg = 0
        #self.timeSpentFalling = 0 #This is important to track because falling velocity due to gravity is non-linear
        #self.personXDelta = 0
        #self.personYDelta = 0
        #self.gravityYDelta = 0
        #self.personXFacing = 0
        #self.personYFacing = 0
        #self.personXTile = 0 #Player world X-coord in tiles
        #self.personYTile = 0 #Player world Y-coord in tiles
        #self.x = (((self.camera.displayWidth/float(self.tileWidth))/2)*self.tileWidth) #Player screen X-coord in pixels
        #self.y = (((self.camera.displayHeight/float(self.tileHeight))/2)*self.tileHeight) #Player screen Y-coord in pixels
        #self.personXDeltaButScreenOffset = 0 #Offsets character screen velocity when camera moves with character
        #self.personYDeltaButScreenOffset = 0 #Offsets character screen velocity when camera moves with character
        #self.character.width = 32 #IN PIXELS
        #self.character.height = 32 #IN PIXELS
        #self.DEFAULTcharacter.speed = .5 #PLAYER SPEED IN PIXELS/MILLISECOND
        #self.character.speed = 0 #ACTUAL PLAYER MOVEMENT BASED ON COMPUTER'S FRAME RATE
        #self.numberOfFramesAnimPerWalk = 3
        #self.ammo = 50000
        #self.activeWeapon = 1
        #self.myHealth = 100
        #self.score = 0
        #self.shotsFiredFromMe = False

        self.enemies = [] #[species, weapon, health, aggression, speed, img, x, y, dx, dy, width, height]
        self.particles = []

        self.userCharacter = Character("User") #particles: [NAME, X1, Y1, DX, DY, R, G, B, SPEED, 0])
        for i in xrange (4):
            self.userCharacter.weapons.append(Weapon(str(i), (i+1) * 10, 1000, 2, 16, 16, (i+1)/float(100)))
        self.userCharacter.x = (((self.camera.displayWidth/float(self.tileWidth))/2)*self.tileWidth) #Player screen X-coord in pixels
        self.userCharacter.y = (((self.camera.displayHeight/float(self.tileHeight))/2)*self.tileHeight) #Player screen Y-coord in pixels

        self.gfx.loadGfxDictionary("spritesheet.png", "World Tiles", self.tileSheetRows, self.tileSheetColumns, self.tileWidth, self.tileHeight, self.tileXPadding, self.tileYPadding)
        self.gfx.loadGfxDictionary(self.userCharacter.imagesGFXName, self.userCharacter.imagesGFXNameDesc, self.userCharacter.numberOfDirectionsFacingToDisplay, self.userCharacter.numberOfFramesAnimPerWalk, self.userCharacter.width, self.userCharacter.height, 0, 0)
        self.gfx.loadGfxDictionary("bullets.png", "Particles", 4, 1, 16, 16, 0, 0)
        self.gfx.loadGfxDictionary("world objects.png", "World Objects", 4, 4, 16, 16, 0, 0)
        
        self.FPSLimit = 200
        
    def showMenu(self, displayMenu, camera):
        menuSystem = MenuScreen(displayMenu, self.camera.screenResSelection , self.difficultySelection, self.camera.displayType, self.gameDisplay)
        self.difficultySelection, self.camera.screenResSelection, self.camera.displayType, self.exiting = menuSystem.displayMenuScreenAndHandleUserInput()
        self.paused = False
        del menuSystem
        self.camera.updateScreenSettings()

    def play(self):
        # GAME LOOP
        while not self.paused:            
            #HANDLE KEY PRESSES AND PYGAME EVENTS
            self.paused, self.lost, self.userCharacter, self.enterPressed = self.logic.handleHeyPressAndGameEvents(self.paused, self.lost, self.userCharacter)
            #Select the correct image for all characters based on direction facing
            self.userCharacter = self.logic.determineCharPicBasedOnDirectionFacing(self.userCharacter)
            #Select the correct image for all characters based on what leg they are standing on
            self.userCharacter = self.logic.determineCharPicBasedOnWalkOrMovement(self.userCharacter, self.timeElapsedSinceLastFrame)
            #FIGURE OUT HOW MUCH TIME HAS ELAPSED SINCE LAST FRAME WAS DRAWN
            self.timeElapsedSinceLastFrame = self.logic.manageTimeAndFrameRate(self.lastTick, self.clock, self.FPSLimit)
            #NOW THAT KEY PRESSES HAVE BEEN HANDLED, ADJUST THE SPEED OF EVERYTHING BASED ON HOW MUCH TIME ELAPSED SINCE LAST FRAME DRAW, AND PREVENT DIAGONAL SPEED UP ISSUE
            self.particles, self.userCharacter = self.logic.alterAllSpeeds(self.timeElapsedSinceLastFrame, self.particles, self.userCharacter)
            
            self.camera = self.logic.cameraWorldEdgeCollisionCheck(self.thisLevelMap, self.camera, self.userCharacter, self.tileWidth, self.tileHeight)
            #MOVE CHARACTERS & CHECK FOR CHARACTER-WALL COLLISIONS
            self.userCharacter = self.logic.characterWallCollisionTest(self.thisLevelMap, self.camera, self.userCharacter, self.tileHeight, self.tileWidth, self.gravityAppliesToWorld)
            self.userCharacter.deltaX, self.userCharacter.deltaY = self.logic.diagSpeedFix(self.userCharacter.deltaX, self.userCharacter.deltaY, self.userCharacter.speed)

            #TODO: generateBadGuys()
            #TODO: badGuysMoveOrAttack()
            
            #SYNCH SCREEN WITH CHARACTER MOVEMENT
            self.userCharacter, self.camera = self.logic.screenSynchWithCharacterMovement(self.userCharacter, self.camera, self.tileHeight, self.tileWidth, self.thisLevelMapWidth, self.thisLevelMapHeight)
            if self.gravityAppliesToWorld == True:
                self.userCharacter.gravityYDelta, self.userCharacter.timeSpentFalling = self.logic.applyGravityToWorld(self.userCharacter, self.tileHeight)
            #MOVE PARTICLES
            self.particles = self.logic.moveParticlesAndHandleParticleCollision(self.particles, self.thisLevelMap)
            #GENERATE PARTICLES
            self.particles, self.userCharacter = self.logic.generateParticles(self.particles, self.userCharacter, self.tileHeight, self.tileWidth, self.gfx)# (self.bullets, rain drops, snowflakes, etc...)
            #DRAW THE WORLD IN TILES BASED ON THE THE NUMBERS IN THE thisLevelMap ARRAY
            self.gfx.drawWorldInCameraView("World Tiles", self.camera, self.tileWidth, self.tileHeight, self.thisLevelMap, self.gameDisplay)            
            #DRAW THE WORLD IN OBJECTS BASED ON THE THE NUMBERS IN THE self.thisLevelObjects ARRAY
            self.thisLevelObjects = self.gfx.drawWorldInCameraView("World Objects", self.camera, self.tileWidth, self.tileHeight, self.thisLevelObjects, self.gameDisplay, self.timeElapsedSinceLastFrame)
            #DRAW PEOPLE, ENEMIES, OBJECTS AND PARTICLES
            
            self.gfx.drawObjectsAndParticles(self.particles, self.gameDisplay, self.camera, self.tileHeight, self.tileWidth, self.userCharacter)
            
            #DRAW GAME STATS
            #self.gfx.drawSmallMessage("Health: " + str(self.myHealth), 0, self.gameDisplay, white, self.displayWidth)
            #self.gfx.drawSmallMessage("Ammo: " + str(self.userCharacter.ammo), 1, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.drawSmallMessage("Level: " + str(self.currentLevel), 2, self.gameDisplay, white, self.displayWidth)
            #self.gfx.drawSmallMessage("Score: " + str(self.score), 3, self.gameDisplay, white, self.displayWidth)
            #self.gfx.drawSmallMessage("Player X: " + str(self.userCharacter.xTile), 4, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.drawSmallMessage("Player Y: " + str(self.userCharacter.yTile), 5, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.drawSmallMessage("X Offset: " + str(self.camera.viewToScreenPxlOffsetX), 6, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.drawSmallMessage("Y Offset: " + str(self.camera.viewToScreenPxlOffsetY), 7, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.drawSmallMessage("View X: " + str(1 + self.camera.viewX - (self.camera.viewToScreenPxlOffsetX/float(self.tileWidth))), 8, self.gameDisplay, white, self.camera.displayWidth)
            #self.gfx.drawSmallMessage("View Y: " + str(1 + self.camera.viewY - (self.camera.viewToScreenPxlOffsetY/float(self.tileHeight))), 9, self.gameDisplay, white, self.camera.displayWidth)
            self.gfx.drawSmallMessage("FPS: " + str(1000/max(1, self.timeElapsedSinceLastFrame)), 11, self.gameDisplay, white, self.camera.displayWidth)
            pygame.display.update()
            if self.userCharacter.health <= 0:
                self.lost = True
                #self.exiting = True
                self.gfx.drawLargeMessage("YOU LOSE", self.gameDisplay, white)
                self.gameDisplay.fill(black)
                self.gfx.drawLargeMessage(str(self.score) + " pts", self.gameDisplay, white)

            
        #OUT OF THE GAME LOOP
        if self.lost == True:
            #LOST GAME ACTION HERE
            pass
            del self.clock
        else:
            pass

pygame.init()
allResolutionsAvail = pygame.display.list_modes()
#ADD IN GAME-SPECIFIC LOGIC IF CERTAIN RESOLUTIONS ARE TO BE EXCLUDED FROM USER SELECTION
screenResChoices = allResolutionsAvail
del allResolutionsAvail
screenResChoices.sort()
exiting = False
while exiting == False:
    myGame = Game(int(len(screenResChoices)/2), "Window")
    exiting = myGame.showMenu("Main Menu", myGame.camera)
    while myGame.exiting == False and myGame.lost == False:
        myGame.play()
        myGame.showMenu("Paused", myGame.camera)
        #menuSystem = menuScreen("Main Menu", screenResSelection, difficultySelection, displayType)
        #del menuSystem
del myGame
pygame.quit()
quit()
