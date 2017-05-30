import pygame

class GfxHandler(object):
    #GAME RUNTIME:
    #DrawStaticObjects PASS Level. Foreach x, y in Level ->
        #GetImageForLevelLocation PASS Level array(x, y) RETURNS Image ->
        #DrawImageToScreen PASS Image, coordinates DRAWS Image on the screen at given coordinates

    def __init__(self):
        self.gfxDictionary = {}

    def LoadGfxDictionary(self, file_name="", imageIndicator="", rows=0, columns=0, width=0, height=0, pictureXPadding=0, pictureYPadding=0, sheetXOffset = 0, sheetYOffset = 0):
        #Load collection of images into dictionary
        self.spriteSheet = pygame.image.load(file_name)
        imgTransparency = True
        
        if imageIndicator == "World Tiles":
            imgTransparency = False
        self.gfxDictionary.update({imageIndicator:{}}) #NESTED HASHTABLE

        for j in range(rows):
            for k in range(columns):
                self.gfxDictionary[imageIndicator].update(
                    {(j*columns) + k:
                     self.GetImageFromSpritesheet(
                         self.GetImageCoordsInSpritesheet(
                             (j*columns) + k, width, height, pictureXPadding, pictureYPadding, rows, columns, sheetXOffset, sheetYOffset), imgTransparency
                         )
                     }
                )

    def GetImageFromSpritesheet(self, Coords, requiresTransparency):
        #Gets requested image out of the GfxDictionary.
        #Requires coordinates
        image = pygame.Surface([Coords[2], Coords[3]])
        image.blit(self.spriteSheet, (0,0), Coords)
        if requiresTransparency == True:
            image.set_colorkey((0,0,0))
        return image

    def GetImageCoordsInSpritesheet(self, tileRequested, tileWidth, tileHeight, pictureXPadding, pictureYPadding, spritesheetRows, spritesheetColumns, sheetXOffset, sheetYOffset):
        #Gets coordinates of requested image's location within the spritesheet
        return (tileRequested - (int(tileRequested/spritesheetColumns) * spritesheetColumns)) * (tileWidth + pictureXPadding) + sheetXOffset, int(tileRequested/spritesheetColumns) * (tileHeight + pictureYPadding) + sheetYOffset,  tileWidth, tileHeight

    def CreateTextObject(self, text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def DrawLargeMessage(self, text, myGameDisplay, myColor):
        largeText = pygame.font.Font("freesansbold.ttf", 135)
        textSurf, textRect = self.CreateTextObject(text, largeText, myColor)
        textRect.center = ((DisplayWidth/2), (DisplayHeight/2))
        myGameDisplay.blit(textSurf, textRect)
        pygame.display.update()
        time.sleep(2)

    def DrawSmallMessage(self, text, lineNumber, myGameDisplay, myColor, DisplayWidth):
        smallText = pygame.font.Font("freesansbold.ttf", 16)
        textSurf, textRect = self.CreateTextObject(text, smallText, myColor)
        textRect.center = ((DisplayWidth-60), 15 + (15*lineNumber))
        myGameDisplay.blit(textSurf, textRect)

    def DrawImageToScreen(self, myImage, myCoords, myGameDisplay):
        #Draws a given image to the screen
         myGameDisplay.blit(myImage, (myCoords[0], myCoords[1]))

##    def DrawDialogs(self, conversationArray, (backR, backG, backB, backA), (foreR, foreG, foreB, foreA), (borderR, borderG, borderB, borderA), borderSize = 5):
##        #Not working yet
##        conversationSelections = []
##        return conversationSelections

    def DrawCharacter(self, character, gameDisplay):
        self.DrawImageToScreen(self.gfxDictionary[character.imagesGFXNameDesc][(character.imgDirectionIndex * character.numberOfFramesAnimPerWalk ) + character.imgLegIndex], character.GetLocationOnScreen(), gameDisplay)

    def DrawParticle(self, particle, gameDisplay, camera, tileHeight, tileWidth):
        #Draws objects, particles, and anything else that is animated or non-static part of the level
        if particle.name == "User Bullet":
            if ((1 + camera.xTile + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particle.xTile) * -tileWidth) + particle.width > 0 and (1 + camera.xTile + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particle.xTile) * -tileWidth < camera.DisplayWidth:
                self.DrawImageToScreen(particle.img, ((1 + camera.xTile + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) - particle.xTile) * -tileWidth, (1 + camera.yTile + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) - particle.yTile) * -tileHeight), gameDisplay)

    def DrawStaticObjects(self, tileSet, camera, tileWidth, tileHeight, wallMap, gameDisplay, timeElapsedSinceLastFrame=0):
        #Draw static world objects in camera view
        for i in range(int(camera.DisplayWidth/float(tileWidth))+2):
            for j in range(int(camera.DisplayHeight/float(tileHeight))+2):
                try:
                    imgToDraw, wallMap = self.GetImageForLevelLocation(wallMap, i, j, camera.xTile, camera.yTile, tileSet, timeElapsedSinceLastFrame)
                    if imgToDraw != "":
                        self.DrawImageToScreen(imgToDraw,
                          (((i-1)*tileWidth)+camera.viewToScreenPxlOffsetX,
                          ((j-1)*tileHeight)+camera.viewToScreenPxlOffsetY,
                          (((i-1)*tileWidth)+camera.viewToScreenPxlOffsetX)+ tileWidth,
                          (((j-1)*tileHeight)+camera.viewToScreenPxlOffsetY) + tileHeight), gameDisplay)
                except:
                    pass
        return wallMap

    def GetImageForLevelLocation(self, wallMap, i, j, viewX, viewY, tileSet, timeElapsedSinceLastFrame):
        imgToDraw = ""
        #print(wallMap[j+viewY][i+viewX])
        if wallMap[j+viewY][i+viewX] != None:
            #If it's a static world object
            if wallMap[j+viewY][i+viewX].isAnimated == False:
                #imgToDraw = self.gfxDictionary[tileSet][wallMap[j+viewY][i+viewX]]
                imgToDraw = self.gfxDictionary[tileSet][wallMap[j+viewY][i+viewX].activeImage]

            #Otherwise, if it's a non-static world object (flame animation, water flowing animation, etc...)
            else:
                self.UpdateObjectAnimation(wallMap, i, j, viewX, viewY, tileSet, timeElapsedSinceLastFrame)
                imgToDraw = self.gfxDictionary[tileSet][wallMap[j+viewY][i+viewX].activeImage + int(wallMap[j+viewY][i+viewX].ID)]
        return imgToDraw, wallMap

    def UpdateObjectAnimation(self, wallMap, i, j, viewX, viewY, tileSet, timeElapsedSinceLastFrame):
        wallMap[j+viewY][i+viewX].timeElapsedSinceLastFrame = wallMap[j+viewY][i+viewX].timeElapsedSinceLastFrame + timeElapsedSinceLastFrame
        while wallMap[j+viewY][i+viewX].timeElapsedSinceLastFrame > wallMap[j+viewY][i+viewX].timeBetweenAnimFrame:
            wallMap[j+viewY][i+viewX].timeElapsedSinceLastFrame = wallMap[j+viewY][i+viewX].timeElapsedSinceLastFrame - wallMap[j+viewY][i+viewX].timeBetweenAnimFrame
            wallMap[j+viewY][i+viewX].activeImage = wallMap[j+viewY][i+viewX].activeImage + 1
            if wallMap[j+viewY][i+viewX].activeImage >= ((wallMap[j+viewY][i+viewX].ID + 1) * wallMap[j+viewY][i+viewX].columns - wallMap[j+viewY][i+viewX].ID):
                wallMap[j+viewY][i+viewX].activeImage = wallMap[j+viewY][i+viewX].activeImage - wallMap[j+viewY][i+viewX].columns

class View(object):
    def __init__(self, gfx, camera, activeLevel, gameDisplay):
        self.gfx = gfx
        self.camera = camera
        self.activeLevel = activeLevel
        self.gameDisplay = gameDisplay

    def RefreshScreen(self, timeElapsedSinceLastFrame, characters, particles):
        self.DrawLevelObjects(timeElapsedSinceLastFrame)
        self.DrawCharacters(characters)
        self.DrawParticles(particles)

    def DrawLevelObjects(self, timeElapsedSinceLastFrame):
        self.gfx.DrawStaticObjects("World Tiles", self.camera, self.activeLevel.tileWidth, self.activeLevel.tileHeight, self.activeLevel.wallMap, self.gameDisplay)  #DRAW THE WORLD IN TILES BASED ON THE THE NUMBERS IN THE wallMap ARRAY
        self.activeLevel.objectMap = self.gfx.DrawStaticObjects("World Objects", self.camera, self.activeLevel.tileWidth, self.activeLevel.tileHeight, self.activeLevel.objectMap, self.gameDisplay, timeElapsedSinceLastFrame) #DRAW THE WORLD IN OBJECTS BASED ON THE THE NUMBERS IN THE self.objectMap ARRAY

    def DrawCharacters(self, characters):
        for i in range(len(characters)):
            self.gfx.DrawCharacter(characters[i], self.gameDisplay)

    def DrawParticles(self, particles):
        for j in range(len(particles)):
            self.gfx.DrawParticle(particles[j], self.gameDisplay, self.camera, self.activeLevel.tileHeight, self.activeLevel.tileWidth)
