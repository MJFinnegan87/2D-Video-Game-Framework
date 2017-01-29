import pygame
import time
import random

from DataAccessLayer import *
from HardwareAccessLayer import *
from GraphicsPresentationLayer import *
from Models import *
from Controllers import *

#Python 3.6
#https://github.com/Microsoft/PTVS/wiki/Selecting-and-Installing-Python-Interpreters#hey-i-already-have-an-interpreter-on-my-machine-but-ptvs-doesnt-seem-to-know-about-it
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
PI = math.pi

class Menu(object):
    def __init__(self, name, titleText, titleFont, contentText, contentFont, itemMargin, unselectedTextColor, selectedTextColorLowPulsate, selectedTextColorHighPulsate, pulsateSpeed):
        self.name = name
        self.titleText = titleText
        self.titleFont = titleFont
        self.itemMargin = itemMargin
        self.contentText = contentText
        self.contentFont = contentFont
        self.unselectedTextColor = unselectedTextColor
        self.selectedTextColorLowPulsate = selectedTextColorLowPulsate
        self.selectedTextColorHighPulsate = selectedTextColorHighPulsate
        self.pulsateSpeed = pulsateSpeed
        #self.HWController = Hardware()

    def DisplayMenu(self):
        pass        

class MenuManager(object):
    def __init__(self, menuType, screenResSelection, difficultySelection, DisplayType, gameDisplay):
        self.gameDisplay = gameDisplay
        self.menuType = menuType
        self.screenResSelection = screenResSelection
        self.difficultySelection = difficultySelection
        self.DisplayType = DisplayType
        self.menuDirectory = "Main"
        self.menuJustOpened = True
        #self.score = 0
        self.highScoreDifficulty = 0
        #self.myHealth = 100
        self.menuSelectionIndex = 6
        #self.ammo = 0
        self.DisplayWidth = screenResChoices[screenResSelection][0]
        self.DisplayHeight = screenResChoices[screenResSelection][1]
        if self.DisplayType == "Full Screen":
            self.gameDisplay = pygame.display.set_mode((self.DisplayWidth, self.DisplayHeight), pygame.FULLSCREEN)
        else:
            self.gameDisplay = pygame.display.set_mode((self.DisplayWidth, self.DisplayHeight))
        self.colorIntensity = 255
        self.colorIntensityDirection = 5
        self.startPlay = False
        self.gfx = GfxHandler()
        #self.HWController = Hardware()
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
        
    def DisplayMenuAndHandleUserInput(self):
        while self.exiting == False and self.startPlay == False:
            self.DisplayTitle()
            self.PulsateSelection()
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

            if self.upKey == True:
                self.personYDeltaWas = self.userCharacter.deltaY
            self.personXDeltaWas = self.userCharacter.deltaX
            self.UpdateScreenAndLimitFPS(self.menuFPSLimit)
            self.gameDisplay.fill(black)
        del self.clock
        return self.difficultySelection, self.screenResSelection, self.DisplayType, self.exiting
    
    def DisplayTitle(self):
        gameTitle = "2d Game Framework"
        self.smallText = pygame.font.Font("freesansbold.ttf", 24)
        self.largeText = pygame.font.Font("freesansbold.ttf", 48)
        self.textSurf, self.textRect = self.gfx.CreateTextObject(gameTitle, self.largeText, white)
        self.textRect.center = ((self.DisplayWidth/2.0), (self.screenMoveCounter + 25))
        self.gameDisplay.blit(self.textSurf, self.textRect)
        if self.menuType == "Paused":
            self.textSurf, self.textRect = self.gfx.CreateTextObject("-Paused-", self.smallText, white)
            self.textRect.center = ((self.DisplayWidth/2.0), (self.screenMoveCounter + 60))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def PulsateSelection(self):
        if self.colorIntensity + self.colorIntensityDirection > 255:
            self.colorIntensityDirection = -5
        elif self.colorIntensity + self.colorIntensityDirection < 65:
            self.colorIntensityDirection = 5
        self.colorIntensity = self.colorIntensity + self.colorIntensityDirection

    def HandleMenuBackground(self):
        pass
        #self.world.activeLevel, self.activeWeapon, self.enemiesAlive, self.myEnemies, self.myProjectiles = self.menuGameEventHandler.addGameObjects(
            #self.enemiesAlive, self.world.activeLevel, self.activeWeapon, self.myEnemies, self.starProbabilitySpace, self.starDensity, self.starMoveSpeed, self.myProjectiles, self.DisplayWidth)
        #self.starMoveSpeed = self.menuGameEventHandler.adjustStarMoveSpeed(self.maximumStarMoveSpeed, self.numberOfStarSpeeds)
        #self.myProjectiles, self.myEnemies, self.myHealth, self.score, self.enemiesAlive, self.y, self.ammo = self.menuGameEventHandler.moveAndDrawProjectilesAndEnemies(
            #self.myProjectiles, self.myEnemies, self.myHealth, self.score, self.enemiesAlive, self.x, self.y, self.rocketWidth, self.rocketHeight, self.difficultySelection, self.DisplayWidth, self.DisplayHeight, self.ammo, self.starMoveSpeed)
        #self.menuGameEventHandler.drawObject(myCharacter, self.x, self.y)

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
            self.textSurf, self.textRect = self.gfx.CreateTextObject(self.text, self.smallText, self.rgb)
            self.textRect.center = ((self.DisplayWidth/2.0), (self.DisplayHeight/2.0 - self.i*(self.mainMenuItemMargin) + self.screenMoveCounter))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def DisplaySettingsMenu(self):
        self.fullScreenWindowChanged = False
        for self.i in range(5):
            self.rgb = (255, 255, 255)
            if self.i == 4:
                self.text = "Screen Size: " + str(screenResChoices[self.screenResSelection][0]) + "x" + str(screenResChoices[self.screenResSelection][1])
            if self.i == 3:
                self.text = "Screen: " + self.DisplayType
            if self.i == 2:
                self.text = "Music Volume: 100"
            if self.i == 1:
                self.text = "SFX Volume: 100"
            if self.i == 0:
                self.text = "Go Back"
            if self.i == self.menuSelectionIndex:
                self.rgb = (self.colorIntensity, 0, 0)
            self.textSurf, self.textRect = self.gfx.CreateTextObject(self.text, self.smallText, self.rgb)
            self.textRect.center = ((self.DisplayWidth/2.0), (self.DisplayHeight/2.0 - self.i*(self.mainMenuItemMargin)))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def DisplayCreditsMenu(self):
        creditsMoveSpeed = 5
        if self.screenMoveCounter < self.DisplayHeight:
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
            self.textSurf, self.textRect = self.gfx.CreateTextObject(self.text, self.smallText, self.rgb)
            #self.textRect.center = ((self.DisplayWidth/2), (self.DisplayHeight/2 - self.i*(self.character.speed)))
            self.textRect.center = ((self.DisplayWidth/2.0), ((self.i * self.mainMenuItemMargin) + self.screenMoveCounter - self.DisplayHeight/2.0))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def DisplayHowToMenu(self):
        howToSpeed = 5
        if self.screenMoveCounter < self.DisplayHeight:
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
            self.textSurf, self.textRect = self.gfx.CreateTextObject(self.text, self.smallText, self.rgb)
            #self.textRect.center = ((self.DisplayWidth/2), (self.DisplayHeight/2 - self.i*(self.character.speed)))
            self.textRect.center = ((self.DisplayWidth/2.0), ((self.i * self.mainMenuItemMargin) + self.screenMoveCounter - self.DisplayHeight/2.0))
            self.gameDisplay.blit(self.textSurf, self.textRect)

    def DisplayHighScoresMenu(self):
        if self.menuSelectionIndex == 0:
            self.rgb = (self.colorIntensity, 0, 0)
        else:
            self.rgb = (255, 255, 255)
        self.textSurf, self.textRect = self.gfx.CreateTextObject("<<  " + self.difficultyChoices[self.highScoreDifficulty] + " High Scores  >>", self.smallText, self.rgb)
        self.textRect.center = ((self.DisplayWidth/2.0), (self.screenMoveCounter + 90))
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
                    self.textSurf, self.textRect = self.gfx.CreateTextObject(self.text, self.smallText, self.rgb)
                    #self.textRect.center = ((self.DisplayWidth/2), (self.DisplayHeight/2 - self.i*(self.character.speed)))
                    self.textRect.center = ((self.DisplayWidth*((self.j+1)/6.0)), ((self.i * self.mainMenuItemMargin) + self.DisplayHeight/2.0))
                elif self.i == self.myHighScoreDatabase.numberOfRecordsPerDifficulty:
                    if self.menuSelectionIndex == 1:
                        self.rgb = (self.colorIntensity, 0, 0)
                    else:
                        self.rgb = (255, 255, 255)
                    self.text = "Go Back"
                    self.textSurf, self.textRect = self.gfx.CreateTextObject(self.text, self.smallText, self.rgb)
                    self.textRect.center = ((self.DisplayWidth*.8), (self.DisplayHeight * .95))
                else:
                    self.rgb = (255, 255, 255)
                    #print str(self.highScoreDifficulty)
                    self.text = str(self.myHighScores[self.highScoreDifficulty][self.i][self.j])
                    self.textSurf, self.textRect = self.gfx.CreateTextObject(self.text, self.smallText, self.rgb)
                    #self.textRect.center = ((self.DisplayWidth/2), (self.DisplayHeight/2 - self.i*(self.character.speed)))
                    self.textRect.center = ((self.DisplayWidth*((self.j+1)/6.0)), ((self.i * self.mainMenuItemMargin) + self.DisplayHeight/2.0))
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
            if self.DisplayType == "Window":
                self.DisplayType = "Full Screen"
            else:
                self.DisplayType = "Window"
            self.fullScreenWindowChanged = True
        if ((((self.userCharacter.deltaX == self.userCharacter.speed and self.personXDeltaWas == 0) or (self.enterPressed == True)) and self.menuSelectionIndex == 4) or ((self.userCharacter.deltaX == -self.userCharacter.speed and self.personXDeltaWas == 0) and self.menuSelectionIndex == 4)) or self.fullScreenWindowChanged == True:
            self.DisplayWidth = screenResChoices[self.screenResSelection][0]
            self.DisplayHeight = screenResChoices[self.screenResSelection][1]
            if self.DisplayType == "Window":
                gameDisplay = pygame.display.set_mode((self.DisplayWidth, self.DisplayHeight))
            else:
                gameDisplay = pygame.display.set_mode((self.DisplayWidth, self.DisplayHeight), pygame.FULLSCREEN)
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

class Game(object):
    def __init__(self, screenResSelection, fullScreen, worldDB, worldDBFilePath, startingLevel, calculationsPerFrame):
        self.calculationsPerFrame = calculationsPerFrame #Tradeoff: increasing calculations per frame, reduces the probability of incorrect object pass-through, but can reduce frame rate.
        
        self.world = World(worldDBFilePath, worldDB)
        #self.world.Reset()
        self.world.LoadWallObjects()
        self.world.LoadWorldObjects()
        self.world.LoadLevel(startingLevel)
        #self.world.activeLevel.gravity = True
        self.clock = pygame.time.Clock()
        self.gfx = GfxHandler()
        
        pygame.display.set_caption("2D Game Framework")
        
        self.lastTick = 0
        self.timeElapsedSinceLastFrame = 0

        self.exiting = False
        self.paused = False
        self.lost = False
        self.difficultySelection = 0
        self.enterPressed = False


        self.particles = []

        self.gfx.LoadGfxDictionary("../Images/spritesheet.png", "World Tiles", self.world.activeLevel.tileSheetRows, self.world.activeLevel.tileSheetColumns, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.world.activeLevel.tileXPadding, self.world.activeLevel.tileYPadding)
        self.userCharacter = Character(name = "User", imagesGFXName = "../Images/userPlayer TEST.png", boundToCamera = True, xTile = self.world.activeLevel.startX, yTile = self.world.activeLevel.startY, deltaX = 0, deltaY = 0, width = 42, height = 43, pictureXPadding = 1, pictureYPadding = 1, gravity = True, gravityCoefficient = .0000005)
        self.camera = Camera(screenResSelection, fullScreen, 14, 0, self.userCharacter, 1/2.0, 1/2.0)
        self.gameDisplay = self.camera.UpdateScreenSettings()
        self.userCharacter.InitializeScreenPosition(self.camera, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)
        for i in range (4):
            #self.userCharacter.weapons.append(Weapon(str(i), (i+1) * 10, 1000, "Bounce", 5 ,16, 16, (i+1)/2, True, .000005))
            self.userCharacter.weapons.append(Weapon(str(i), (i+1) * 10, 1000, "Bounce", 4*(i+1) ,16, 16, (i+1)/2, False))
        self.characters = [self.userCharacter]
        for character in self.characters:
            self.gfx.LoadGfxDictionary(character.imagesGFXName, character.imagesGFXNameDesc, character.numberOfDirectionsFacingToDisplay, character.numberOfFramesAnimPerWalk, character.width, character.height, character.pictureXPadding, character.pictureYPadding)
        self.gfx.LoadGfxDictionary("../Images/bullets.png", "Particles", 4, 1, 16, 16, 0, 0)
        self.gfx.LoadGfxDictionary("../Images/world objects.png", "World Objects", 4, 4, 16, 16, 0, 0)

        self.cameraController = CameraController(self.camera, self.world.activeLevel)
        self.characterController = CharacterController(self.characters, self.camera, self.world.activeLevel)
        self.View = View(self.gfx, self.camera, self.world.activeLevel, self.gameDisplay)
        #self.levelController = LevelController()
        self.FPSLimit = 120
        self.gameController = GameController()
        self.hardwareAccessLayer = Hardware()
        self.particleController = ParticleController(self.particles, self.characters, self.world.activeLevel, self.gfx)
        #self.worldController = WorldController(self.world)
        
    def ShowMenu(self, DisplayMenu, camera):
        menuSystem = MenuManager(DisplayMenu, self.camera.screenResSelection , self.difficultySelection, self.camera.DisplayType, self.gameDisplay)
        self.difficultySelection, self.camera.screenResSelection, self.camera.DisplayType, self.exiting = menuSystem.DisplayMenuAndHandleUserInput()
        self.paused = False
        del menuSystem
        self.camera.UpdateScreenSettings()

    def Play(self):
        # GAME LOOP
        while not self.paused:
            timeElapsedSinceLastFrame = self.gameController.ManageTimeAndFrameRate(self.FPSLimit)
            for calcIteration in range(self.calculationsPerFrame): #TODO: maybe have this be based on the user's framerate? That way if user is maxing out FPS, the game can perform more calculations, but not too much more so as to completely use up all CPU cycles?
                self.hardwareAccessLayer.PollHardware()
                self.gameController.HandleGameEvents(self.hardwareAccessLayer.gameEvents)
                self.characterController.ApplyUserInputToCharacter(self.hardwareAccessLayer.characterEvents)
                self.characterController.CalculateCharacterPlacement(timeElapsedSinceLastFrame/float(self.calculationsPerFrame))
                self.cameraController.HandleWorldEdgeCollision()
                self.characterController.MoveCharacters()
                self.cameraController.MoveCamera()
                self.particleController.CreateParticles()
                self.particleController.CalculateParticlePlacement(timeElapsedSinceLastFrame/float(self.calculationsPerFrame))
                self.particleController.MoveParticles()
                self.particleController.HandleCollisions()
                self.particleController.DeleteParticles()
            self.View.RefreshScreen(timeElapsedSinceLastFrame, self.characters, self.particles)
            
            #DRAW GAME STATS
            #self.gfx.DrawSmallMessage("Health: " + str(self.myHealth), 0, self.gameDisplay, white, self.DisplayWidth)
            #self.gfx.DrawSmallMessage("Ammo: " + str(self.characters[i].ammo), 1, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Level: " + str(self.world.activeLevel), 2, self.gameDisplay, white, self.DisplayWidth)
            #self.gfx.DrawSmallMessage("Score: " + str(self.score), 3, self.gameDisplay, white, self.DisplayWidth)
            #self.gfx.DrawSmallMessage("Player wX: " + str(self.characters[0].GetLocationInWorld()[0]), 4, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Player wY: " + str(self.characters[0].GetLocationInWorld()[1]), 5, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Player sX: " + str(self.characters[0].GetLocationOnScreen()[0]), 6, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Player sY: " + str(self.characters[0].GetLocationOnScreen()[1]), 7, self.gameDisplay, white, self.camera.DisplayWidth)

            #self.gfx.DrawSmallMessage("X Offset: " + str(self.camera.viewToScreenPxlOffsetX), 8, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Y Offset: " + str(self.camera.viewToScreenPxlOffsetY), 9, self.gameDisplay, white, self.camera.DisplayWidth)

            #self.gfx.DrawSmallMessage("Player dxO: " + str(self.characters[0].deltaXScreenOffset), 8, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Player dyO: " + str(self.characters[0].deltaYScreenOffset), 9, self.gameDisplay, white, self.camera.DisplayWidth)

            #self.gfx.DrawSmallMessage("Cam X: " + str(self.camera.GetLocationInWorld(self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)[0]), 10, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Cam Y: " + str(self.camera.GetLocationInWorld(self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)[1]), 11, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("person dx: " + str(self.characters[0].deltaX), 12, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("person dy: " + str(self.characters[0].deltaY), 13, self.gameDisplay, white, self.camera.DisplayWidth)
            self.gfx.DrawSmallMessage("FPS: " + str(int(1000/max(1, timeElapsedSinceLastFrame))), 14, self.gameDisplay, white, self.camera.DisplayWidth)
            pygame.display.update()
            if self.characters[0].health <= 0:
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

pygame.init()
allResolutionsAvail = pygame.display.list_modes()
#ADD IN GAME-SPECIFIC LOGIC IF CERTAIN RESOLUTIONS ARE TO BE EXCLUDED FROM USER SELECTION
screenResChoices = allResolutionsAvail
del allResolutionsAvail
screenResChoices.sort()
exiting = False
while exiting == False:
    #myGame = Game(int(len(screenResChoices)/2), "Window", "world.db", "", 0, 2)
    myGame = Game(int(len(screenResChoices)/2), "Window", "world.db", "", 0, 4)
    #exiting = myGame.ShowMenu("Main Menu", myGame.camera)
    while myGame.exiting == False and myGame.lost == False:
        myGame.Play()
        myGame.ShowMenu("Paused", myGame.camera)
del myGame
pygame.quit()
quit()
