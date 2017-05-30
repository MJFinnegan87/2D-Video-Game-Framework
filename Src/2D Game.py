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
        print(self.world.activeLevel.tileWidth)
        self.gfx.LoadGfxDictionary("../Images/spritesheet.png", "World Tiles", self.world.activeLevel.tileSheetRows, self.world.activeLevel.tileSheetColumns, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.world.activeLevel.tileXPadding, self.world.activeLevel.tileYPadding)
        #self.userCharacter = Character(name = "User", imagesGFXName = "../Images/userPlayer TEST.png", boundToCamera = True, xTile = self.world.activeLevel.startX, yTile = self.world.activeLevel.startY, deltaX = 0, deltaY = 0, width = 41, height = 42, pictureXPadding = 1, pictureYPadding = 1, gravity = True, gravityCoefficient = .0000005)
        self.userCharacter = Character(name = "User", imagesGFXName = "../Images/userPlayer 64.png", boundToCamera = True, xTile = self.world.activeLevel.startX, yTile = self.world.activeLevel.startY, deltaX = 0, deltaY = 0, width = 41, height = 42, pictureXPadding = 1, pictureYPadding = 1, gravity = True, gravityCoefficient = .0000005)
        self.camera = Camera(screenResSelection, fullScreen, 14, 0, self.userCharacter, 1/2.0, 1/2.0)
        #self.camera.SetLocation(0, 0, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)
        self.camera.InitializeLocation(self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.world.activeLevel.levelWidth, self.world.activeLevel.levelHeight)
        self.gameDisplay = self.camera.UpdateScreenSettings()
        self.userCharacter.InitializeScreenPosition(self.camera, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)
        for i in range (4):
            #self.userCharacter.weapons.append(Weapon(str(i), (i+1) * 10, 1000, "Bounce", 5 ,16, 16, (i+1)/2, True, .000005))
            self.userCharacter.weapons.append(Weapon(str(i), (i+1) * 10, 1000, "Bounce", 4*(i+1) ,16, 16, (i+1)/2, False))
        self.characters = [self.userCharacter]
        for character in self.characters:
            self.gfx.LoadGfxDictionary(character.imagesGFXName, character.imagesGFXNameDesc, character.numberOfDirectionsFacingToDisplay, character.numberOfFramesAnimPerWalk, character.width, character.height, character.pictureXPadding, character.pictureYPadding, 1, 1)
        self.gfx.LoadGfxDictionary("../Images/bullets.png", "Particles", 4, 1, 16, 16, 0, 0)
        self.gfx.LoadGfxDictionary("../Images/world objects.png", "World Objects", 4, 4, self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight, self.world.activeLevel.tileXPadding, self.world.activeLevel.tileYPadding)

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
            #self.gfx.DrawSmallMessage("Health: " + str(self.characters[0].myHealth), 0, self.gameDisplay, white, self.DisplayWidth)
            #self.gfx.DrawSmallMessage("Ammo: " + str(self.characters[0].ammo), 1, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Level: " + str(self.world.activeLevel), 2, self.gameDisplay, white, self.DisplayWidth)
            #self.gfx.DrawSmallMessage("Score: " + str(self.characters[0].score), 3, self.gameDisplay, white, self.DisplayWidth)
            self.gfx.DrawSmallMessage("Player wX: " + str(self.characters[0].GetLocation()[0]), 4, self.gameDisplay, white, self.camera.DisplayWidth)
            self.gfx.DrawSmallMessage("Player wY: " + str(self.characters[0].GetLocation()[1]), 5, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Player sX: " + str(self.characters[0].GetLocationOnScreen()[0]), 6, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Player sY: " + str(self.characters[0].GetLocationOnScreen()[1]), 7, self.gameDisplay, white, self.camera.DisplayWidth)

            #self.gfx.DrawSmallMessage("X Offset: " + str(self.camera.viewToScreenPxlOffsetX), 8, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Y Offset: " + str(self.camera.viewToScreenPxlOffsetY), 9, self.gameDisplay, white, self.camera.DisplayWidth)

            #self.gfx.DrawSmallMessage("Player dxO: " + str(self.characters[0].deltaXScreenOffset), 8, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Player dyO: " + str(self.characters[0].deltaYScreenOffset), 9, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Cam X: " + str(self.camera.GetLocation(self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)[0]), 10, self.gameDisplay, white, self.camera.DisplayWidth)
            #self.gfx.DrawSmallMessage("Cam Y: " + str(self.camera.GetLocation(self.world.activeLevel.tileWidth, self.world.activeLevel.tileHeight)[1]), 11, self.gameDisplay, white, self.camera.DisplayWidth)
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
    myGame = Game(int(len(screenResChoices)/2), "Window", "world.db", "", 0, 2)
    #exiting = myGame.ShowMenu("Main Menu", myGame.camera)
    while myGame.exiting == False and myGame.lost == False:
        myGame.Play()
        myGame.ShowMenu("Paused", myGame.camera)
del myGame
pygame.quit()
quit()
