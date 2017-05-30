import pygame
import math
from Models import *

PI = math.pi

class Controller(object):
    def __init__(self):
        pass

class GameController(Controller):
    def __init__(self): #, cameraController, characterController, View, levelController, particleController, Hardware, worldController):
        self.clock = pygame.time.Clock()
        self.lastTick = 0
        self.timeElapsedSinceLastFrame = 0

    def HandleGameEvents(self, gameEvents):
        if gameEvents["saved"] == True:
            pass #TODO: Implement save functionality

    def ManageTimeAndFrameRate(self, FPSLimit):
        self.timeElapsedSinceLastFrame = self.clock.get_time()
        self.lastTick = self.clock.tick(FPSLimit)
        return self.timeElapsedSinceLastFrame

class CameraController(Controller):
    def __init__(self, camera, activeLevel):
        self.camera = camera
        self.activeLevel = activeLevel

    def HandleWorldEdgeCollision(self):
        self.camera.TestIfAtWorldEdgeCollision(self.activeLevel.wallMap, self.activeLevel.tileWidth, self.activeLevel.tileHeight)

    def MoveCamera(self):
        self.camera.MoveBasedOnBoundCharacterMovement(self.activeLevel.tileHeight, self.activeLevel.tileWidth, self.activeLevel.levelWidth, self.activeLevel.levelHeight )#TEST IF USER CHARACTER MOVES OUTSIDE OF INNER NINTH OF SCREEN <<ISSUE

class CharacterController(Controller):
    def __init__(self, characters, camera, activeLevel):
        self.characters = characters
        self.camera = camera
        self.activeLevel = activeLevel

    def CreateCharacters(self):
        pass
        #TODO: generateBadGuys()

    def ApplyUserInputToCharacter(self, characterEvents):        
        tempDeltaX = 0
        tempDeltaY = 0
        if characterEvents["activeWeapon"] != None:
            self.characters[0].activeWeapon = characterEvents["activeWeapon"]
        self.characters[0].shotsFiredFromMe = characterEvents["shotsFiredFromMe"]
        self.characters[0].deltaX = 0
        self.characters[0].deltaY = 0 #Set deltaX/Y to 0, without changing the angle. Angle will still be used for character facing image and bullet direction even when character is no longer moving.
        if characterEvents["right"] == True:
            tempDeltaX = self.characters[0].speed
        if characterEvents["left"] == True:
            tempDeltaX = -self.characters[0].speed
        if characterEvents["up"] == True:
            tempDeltaY = -self.characters[0].speed
        if characterEvents["down"] == True:
            tempDeltaY = self.characters[0].speed
        if tempDeltaX != 0 or tempDeltaY != 0:
            self.characters[0].SetDeltaXDeltaY(tempDeltaX, tempDeltaY)

        #TODO: Add joystick handling

##        if self.characters[0].deltaX != 0 or self.characters[0].deltaY != 0:
##            self.characters[0].xFacing = 0
##            self.characters[0].yFacing = 0
##            if self.characters[0].deltaX != 0:
##                self.characters[0].xFacing = self.characters[0].deltaX/abs(self.characters[0].deltaX)
##            if self.characters[0].deltaY != 0:
##                self.characters[0].yFacing = self.characters[0].deltaY/abs(self.characters[0].deltaY)

    def CalculateCharacterPlacement(self, timeElapsedSinceLastFrame):
        for i in range(len(self.characters)):
            self.characters[i].DetermineCharPicBasedOnDirectionFacing(self.activeLevel.gravity) #Select the correct image for all characters based on direction facing
            self.characters[i].DetermineCharPicBasedOnWalkOrMovement(timeElapsedSinceLastFrame) #Select the correct image for all characters based on what leg they are standing on
            self.characters[i].AdjustSpeedBasedOnFrameRate(timeElapsedSinceLastFrame) #NOW THAT KEY PRESSES HAVE BEEN HANDLED, ADJUST THE SPEED OF EVERYTHING BASED ON HOW MUCH TIME ELAPSED SINCE LAST FRAME DRAW, AND PREVENT DIAGONAL SPEED UP ISSUE
            self.characters[i].FixDiagSpeed()
            if self.activeLevel.gravity == True:
                self.characters[i].ApplyGravity()
                self.characters[i].CalculateNextGravityVelocity(self.activeLevel.tileHeight)
            self.characters[i].TestWorldObjectCollision({"WallMap" : self.activeLevel.wallMap, "ObjectMap" : self.activeLevel.objectMap}, self.activeLevel.tileHeight, self.activeLevel.tileWidth, self.activeLevel.gravity, self.activeLevel.stickToWallsOnCollision) #CHECK FOR CHARACTER-WALL COLLISIONS
            self.characters[i].TestIfAtWorldEdgeCollision(self.activeLevel.wallMap, self.activeLevel.tileWidth, self.activeLevel.tileHeight)
            self.characters[i].HandleWorldObjectOrEdgeCollision(self.activeLevel.stickToWallsOnCollision, self.activeLevel.gravity) #Prevent character from moving through world objects or beyond boundaries of the level

    def MoveCharacters(self):
        #TODO: badGuysMoveOrAttack()
        for i in range(len(self.characters)):
            self.characters[i].Move(self.camera, self.activeLevel.tileWidth, self.activeLevel.tileHeight) #MOVE THE USER CHARACTER IN THE WORLD, AND ON THE SCREEN
            self.characters[i].UpdateFireAngle(self.activeLevel.gravity)

    def DeleteCharacters(self):
        pass

class LevelController(Controller):
    def __init__(self, character):
        self.character = character

class ParticleController(Controller):
    def __init__(self, particles, characters, activeLevel, gfx):
        self.myDeletedParticles = []
        self.particles = particles
        self.characters = characters
        self.activeLevel = activeLevel
        self.gfx = gfx

    def CreateParticles(self):
        for character in self.characters:
            #self.particles, self.characters[i] = self.logic.GenerateParticles(self.particles, self.characters[i], self.world.activeLevel.tileHeight, self.world.activeLevel.tileWidth, self.gfx) #GENERATE PARTICLES (self.bullets, rain drops, snowflakes, etc...)
            #def GenerateParticles(self, particles, character, tileHeight, tileWidth, gfx):
            if character.shotsFiredFromMe == True: #and not(character.yFacing == 0 and character.xFacing == 0) and character.activeWeapon < len(character.weapons):
                thisBullet = Bullet("User Bullet", character.weapons[character.activeWeapon].name, character.xTile, character.yTile, 0, 0, character.weapons[character.activeWeapon].damage, character.weapons[character.activeWeapon].physicsIndicator, character.weapons[character.activeWeapon].physicsCounter, character.weapons[character.activeWeapon].generateBulletWidth, character.weapons[character.activeWeapon].generateBulletHeight, character.ID, character.weapons[character.activeWeapon].generateBulletSpeed, character.weapons[character.activeWeapon].generateBulletSpeed, None, character.weapons[character.activeWeapon].gravityApplies, character.weapons[character.activeWeapon].gravityCoefficient, False) #putting multiple instances of the image itself in the array because they could be rotated at different directions and putting a pointer to one image and then rotating many many times severly impacts FPS due to slow rotate method
                thisBullet.speed = thisBullet.defaultSpeed
                thisBullet.SetDeltaAngle(character.fireAngle)
                
##                        if character.xFacing == 0:
##                            tempDX = 0 #THIS AVOIDS THE DIVIDE BY 0 ERROR
##                            if character.yFacing == 0:
##                                tempDY = 0
##                                #img = pygame.transform.rotate(self.gfx.gfxDictionary["Particles"][int(thisBullet.weapon)], (180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
##                                #img = self.GetParticleImage(self.gfx.gfxDictionary["Particles"][int(thisBullet.weapon)], (180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
##                            else:
##                                tempDY = (character.yFacing/float(abs(character.yFacing))) * thisBullet.speed
##                                #img = pygame.transform.rotate(self.gfx.gfxDictionary["Particles"][int(thisBullet.weapon)], ((-character.yFacing/float(abs(character.yFacing))) * 180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
##                                #img = self.GetParticleImage(self.gfx.gfxDictionary["Particles"][int(thisBullet.weapon)], ((-character.yFacing/float(abs(character.yFacing))) * 180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
##                        else:
##                            if character.yFacing == 0:
##                                tempDX = (character.xFacing/float(abs(character.xFacing))) * thisBullet.speed
##                                tempDY = 0
##                                #img = pygame.transform.rotate(self.gfx.gfxDictionary["Particles"][int(thisBullet.weapon)], (180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
##                                #img = self.GetParticleImage(self.gfx.gfxDictionary["Particles"][int(thisBullet.weapon)],  (180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
##                            else:
##                                tempDX = (character.xFacing/float(abs(character.xFacing))) * (math.cos(math.atan(abs(character.yFacing/float(character.xFacing)))) * thisBullet.speed)
##                                tempDY = (character.yFacing/float(abs(character.yFacing))) * (math.sin(math.atan(abs(character.yFacing/float(character.xFacing)))) * thisBullet.speed)
##                                #img = pygame.transform.rotate(self.gfx.gfxDictionary["Particles"][int(thisBullet.weapon)], ((-character.yFacing/float(abs(character.yFacing))) * 180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
##                                #img = self.GetParticleImage(self.gfx.gfxDictionary["Particles"][int(thisBullet.weapon)],  ((-character.yFacing/float(abs(character.yFacing))) * 180*math.acos(tempDX/float((tempDX**2 + tempDY**2)**.5)))/PI)
##                                       #Name, weapon, world X Loc, world Y Loc,  dx,    dy, damage, bounces remaining, bullet width px, bullet height px, frame speed, default speed, image
##                        thisBullet.SetDeltaXDeltaY(tempDX, tempDY)
                thisBullet.img = self.GetParticleImage(self.gfx.gfxDictionary["Particles"][int(thisBullet.weapon)], thisBullet.angle)
                self.particles.append(thisBullet)
                character.shotsFiredFromMe = False

    def GetParticleImage(self, baseImage, angle):
        return pygame.transform.rotate(baseImage, angle)

    def CalculateParticlePlacement(self, timeElapsedSinceLastFrame):
        for j in range(len(self.particles)):
            self.particles[j].AdjustSpeedBasedOnFrameRate(timeElapsedSinceLastFrame) #ADJUST THE SPEED OF EVERYTHING BASED ON HOW MUCH TIME ELAPSED SINCE LAST FRAME DRAW, AND PREVENT DIAGONAL SPEED UP ISSUE        
            self.particles[j].FixDiagSpeed()
            if self.activeLevel.gravity == True and self.particles[j].gravityApplies == True: #HANDLE GRAVITY WHERE APPLICABLE
                print("Applying gravity to this particle")
                self.particles[j].ApplyGravity()
                self.particles[j].CalculateNextGravityVelocity(self.activeLevel.tileHeight)

    def MoveParticles(self):
        for j in range(len(self.particles)):
            self.particles[j].Move(self.activeLevel.wallMap, self.activeLevel.tileWidth, self.activeLevel.tileHeight)

    def HandleCollisions(self):
        for k in range(len(self.particles)):
            self.particles[k].TestIfAtWorldEdgeCollision(self.activeLevel.wallMap, self.activeLevel.tileWidth, self.activeLevel.tileHeight)
            self.particles[k].TestWorldObjectCollision({"WallMap" : self.activeLevel.wallMap, "ObjectMap" : self.activeLevel.objectMap}, self.activeLevel.tileHeight, self.activeLevel.tileWidth, self.activeLevel.gravity, 0)
            self.particles[k].HandleWorldObjectCollision(0, self.activeLevel.gravity)
            if self.particles[k].atWorldEdgeX == 1 or self.particles[k].atWorldEdgeY == 1 or self.particles[k].needToDelete == True:
                self.myDeletedParticles.append(k)
            self.particles[k].img = self.GetParticleImage(self.gfx.gfxDictionary["Particles"][int(self.particles[k].weapon)], self.particles[k].angle)

    def DeleteParticles(self):
        numberDeleted = 0
        for k in range(len(self.myDeletedParticles)):
            del self.particles[self.myDeletedParticles[k] - numberDeleted]
            numberDeleted = numberDeleted + 1
        self.myDeletedParticles = []


class WorldController(Controller):
    def __init__(self):
        pass
