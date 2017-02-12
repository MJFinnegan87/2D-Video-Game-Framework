import math
import pygame
import DataAccessLayer
import sys,os
class Level(object):
    def __init__(self, dataAccessLayer, index = 0, name = "", description = "", weather = "", sideScroller = 0, wallMap = [], objectMap = [], music = "", loopMusic = False, startX = 0, startY = 0, startXFacing = 0, startYFacing = 0, gravity = False, stickToWallsOnCollision = False, tileSheetRows = 0, tileSheetColumns = 0, tileWidth = 0, tileHeight = 0, tileXPadding = 0, tileYPadding = 0):
        self.dataAccessLayer = dataAccessLayer
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
        if len(objectMap) == 0:
            self.levelWidth = 0
        else:
            self.levelWidth = len(objectMap[0])

        self.tileSheetRows = tileSheetRows
        self.tileSheetColumns = tileSheetColumns
        self.tileWidth = tileWidth
        self.tileHeight = tileHeight
        self.tileXPadding = tileXPadding
        self.tileYPadding = tileYPadding

    def mapsToJSON(self):
        self.wallMapJSON, self.objectMapJSON = self.dataAccessLayer.ConvertMapsToJSON(self.wallMap, self.objectMap)

    def JSONToMaps(self, JSONWallData, JSONObjectData):        
        return self.dataAccessLayer.ConvertJSONToMaps(JSONWallData, JSONObjectData)

class World(object):
    def __init__(self, worldDBFilePath, worldDB):
        self.dataAccessLayer = DataAccessLayer.DataAccessLayer(os.path.join(worldDBFilePath, worldDB))
        self.ValidateDB()
        self.wallObjects = []
        self.worldObejcts = []

    def ValidateDB(self):
        if self.dataAccessLayer.ValidateDB() == 0:
            self.Reset()

    def Reset(self):
        self.dataAccessLayer.Reset()

    def GetNumberOfLevels(self):
        return self.dataAccessLayer.GetNumberOfLevels()

    def RemoveLevel(self, index):
        pass

    def LevelExists(self, world, index):
        return self.dataAccessLayer.VerifyLevelExists(world, index)

    def LoadWallObjects(self):
        self.wallObjects = self.dataAccessLayer.LoadWallObjects()

    def LoadWorldObjects(self):
        self.worldObejcts = self.dataAccessLayer.LoadWorldObjects()

    def LoadLevel(self, index):
        self.activeLevel = self.dataAccessLayer.Load(index, self.wallObjects, self.worldObejcts)

    def SaveActiveLevel(self):
        return self.dataAccessLayer.Save()
        #TODO: Save character data too!

class WallObject(object):
    def __init__(self, PK, scoreChangeOnTouch, scoreChangeOnAttack, healthChangeOnTouch, healthChangeOnAttack, ID,  activeImage, walkThroughPossible, actionOnTouch, actionOnAttack, isAnimated = False):
        self.PK = PK
        self.scoreChangeOnTouch = scoreChangeOnTouch
        self.scoreChangeOnAttack = scoreChangeOnAttack
        self.healthChangeOnTouch = healthChangeOnTouch
        self.healthChangeOnAttack = healthChangeOnAttack
        self.ID = ID
        self.activeImage = activeImage
        self.walkThroughPossible = walkThroughPossible
        self.actionOnTouch = actionOnTouch
        self.actionOnAttack = actionOnAttack
        self.isAnimated = False

class GamePlayObject(object):
    def __init__(self):
        self.atWorldEdgeX = False
        self.atWorldEdgeY = False
        self.xCollidingWall = False
        self.yCollidingWall = False
        #Parent object that includes WorldObjects like Characters and Bullets, but also other objects not in-game, like the Camera

    def TestIfAtWorldEdgeCollision(self, wallMap, tileWidth, tileHeight):
        self.atWorldEdgeX = False
        self.atWorldEdgeY = False
        if self.xTile + self.deltaX/float(tileWidth) + self.width/float(tileWidth) > len(wallMap[0]) or self.xTile + self.deltaX/float(tileWidth) < 0:
            self.atWorldEdgeX = 1
        if self.yTile + self.deltaY/float(tileWidth) + self.height/float(tileWidth) > len(wallMap) or self.yTile + self.deltaY/float(tileWidth) < 0:
            self.atWorldEdgeY = 1

    #Abstract
    def HandleWorldEdgeCollision(self):
        pass

class WorldObject(GamePlayObject):
    def __init__(self, PK, xTile, yTile, name = "", desc = "", columns = 0, activeImage = None, actionOnTouch = 0, actionOnAttack = 0, timeBetweenAnimFrame = 0, scoreChangeOnTouch = 0, scoreChangeOnAttack= 0, healthChangeOnTouch = 0, healthChangeOnAttack = 0, addsToCharacterInventoryOnTouch = 0, destroyOnTouch = 0, walkThroughPossible = False, ID = 0, timeElapsedSinceLastFrame = 0, speed = 0, defaultSpeed = 0, deltaX = 0, deltaY = 0, deltaXScreenOffset = 0, deltaYScreenOffset = 0, tileWidth = 0, tileHeight = 0, isAnimated = True):
        self.PK = PK
        self.deltaX = deltaX
        self.deltaY = deltaY
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
        self.activeImage = ID*(int(columns) - 1)
        self.timeBetweenAnimFrame = timeBetweenAnimFrame
        self.timeElapsedSinceLastFrame = 0
        self.ID = ID
        self.scoreChangeOnTouch = scoreChangeOnTouch
        self.scoreChangeOnAttack = scoreChangeOnAttack
        self.healthChangeOnTouch = healthChangeOnTouch
        self.healthChangeOnAttack = healthChangeOnAttack
        self.addsToCharacterInventoryOnTouch = addsToCharacterInventoryOnTouch
        self.destroyOnTouch = destroyOnTouch
        self.timeElapsedSinceLastFrame = timeElapsedSinceLastFrame
        self.deltaXScreenOffset = deltaXScreenOffset #THIS WILL ALWAYS BE CALCULATED BY THE GAME, ABSTRACTED AWAY
        self.deltaYScreenOffset = deltaYScreenOffset #THIS WILL ALWAYS BE CALCULATED BY THE GAME, ABSTRACTED AWAY
        self.isAnimated = isAnimated

    def FixDiagSpeed(self):
        #REDUCE PARTICLE SPEED SO IT DOESN'T TRAVEL FASTER WHEN DIAGONAL
        #  
        #      |\                                                                 |\
        #      | \                                                                | \
        # Y=5  |  \ Z>5  -> solve for X and Y, while keeping x:y the same ratio: Y|  \ 5
        #      |_  \                                                              |_  \
        #      |_|__\                                                             |_|__\
        #       X=5                                                                  X 
        #
        #PERSON/BULLET/ITEM SHOULD NOT TRAVEL FASTER JUST BECAUSE OF TRAVELING DIAGONALLY. THE CODE BELOW ADJUSTS FOR THIS:
        if self.deltaX != 0 and self.deltaY != 0:
            #adjustedSpeed = self.speed# + gravityYDelta
            #tempXDelta = (self.deltaX/abs(self.deltaX)) * (math.cos(math.atan(abs(self.deltaY/self.deltaX))) * adjustedSpeed)
            #self.deltaY = (self.deltaY/abs(self.deltaY)) * (math.sin(math.atan(abs(self.deltaY/self.deltaX))) * adjustedSpeed)
            #self.deltaX = tempXDelta

            #self.SetDeltaXDeltaY((self.deltaX/abs(self.deltaX)) * (math.cos(math.atan(abs(self.deltaY/self.deltaX))) * self.speed),
            #                     (self.deltaY/abs(self.deltaY)) * (math.sin(math.atan(abs(self.deltaY/self.deltaX))) * self.speed))

            #Simplified via:
            #https://www.wolframalpha.com/input/?i=(X%2Fabs(X))+*+(cos(atan(abs(Y%2FX)))+*S)+%3D+Z
            #https://www.wolframalpha.com/input/?i=(Y%2Fabs(Y))+*+(sin(atan(abs(Y%2FX)))+*+S))+%3D+Z
            #This is even better because it doesn't rely on costly trig functions!
            self.SetDeltaXDeltaY( (self.speed * self.deltaX)/((abs(self.deltaX)**2) + (abs(self.deltaY)**2))**.5,
                                 (self.speed * self.deltaY)/((abs(self.deltaX)**2) + (abs(self.deltaY)**2))**.5)


    def SetDeltaXDeltaY(self, deltaX, deltaY):
        self.deltaX = deltaX
        self.deltaY = deltaY
        self.UpdateAngle()

    def SetDeltaAngle(self, angle):
        self.angle = angle % 360
        self.deltaX = 0
        self.deltaY = 0
        if angle > 90 and angle < 270: #Because it cannot be inferred, which X or Y is negative, from the results of tan
            self.deltaX = -1
        elif angle < 90 or angle > 270:
            self.deltaX = 1

        if angle == 90: #Special case because tan is undefined
            self.deltaY = -1
        elif angle == 270: #Special case because tan is undefined
            self.deltaY = 1
        else:
            if angle > 180:
                self.deltaY = abs(math.tan(angle / (180/math.pi)))
            elif angle < 180:
                self.deltaY = -abs(math.tan(angle / (180/math.pi)))
        self.FixDiagSpeed()

    def CalculateNextGravityVelocity(self, tileHeight):
        self.gravityYDelta = (min(self.gravityYDelta + (self.gravityCoefficient * (self.timeSpentFalling**2)), tileHeight / 3.0))
        self.timeSpentFalling = self.timeSpentFalling + 1

    def ApplyGravity(self):
        self.SetDeltaXDeltaY(self.deltaX, self.deltaY + self.gravityYDelta)
        
    def UpdateAngle(self):
        angle = None
        self.deltaY = -self.deltaY #Because Cartesian Plane has Y increase as you go up the Y-axis, but screen drawing has Y decrease as you go up.
        if self.deltaX == 0:
            if self.deltaY > 0:
                angle = 90.0
            elif self.deltaY < 0:
                angle = 270.0
        else:
            angle = math.atan(self.deltaY/self.deltaX)*(180/math.pi)
            if self.deltaX < 0:
                angle = angle + 180
        if angle != None:
            self.angle = angle%360
        self.deltaY = -self.deltaY

    def AdjustSpeedBasedOnFrameRate(self, timeElapsedSinceLastFrame):
        #Determine the speed at which an object should move for this frame, based on the amount of time elapsed since the last frame
        tempDeltaX = 0
        tempDeltaY = 0
        self.speed = self.defaultSpeed * timeElapsedSinceLastFrame
        if self.deltaX < 0:
            tempDeltaX = -self.speed
        elif self.deltaX > 0:
            tempDeltaX = self.speed
        if self.deltaY < 0:
            tempDeltaY = -self.speed
        elif self.deltaY > 0:
            tempDeltaY = self.speed
        self.SetDeltaXDeltaY(tempDeltaX, tempDeltaY)

    def TestWorldObjectCollision(self, levelMap, tileHeight, tileWidth, gravity, stickToWallsOnCollision):
        #CHARACTER<->WALL/EDGE/OBJECT COLLISION DETECTION:
        #COLLISION DETECTION ACTUALLY HAS TO CHECK 2 DIRECTIONS FOR EACH OF THE 4 CORNERS FOR 2D MOVEMENT:
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
        #        v     v
        #        F     E

        self.xCollidingWall = False
        self.yCollidingWall = False
        self.xCollidingObject = False
        self.yCollidingObject = False
        objectTouchActions = {
            'scoreChangeOnTouch' : 0,
            'scoreChangeOnAttack' : 0,
            'healthChangeOnTouch' : 0,
            'healthChangeOnAttack' : 0,
            'addsToCharacterInventoryOnTouch' : 0,
            'destroyOnTouch' : 0}
        #TODO: Apply score, health, etc. changes to character who touches object
        #TODO: Apply actions to bullets and affect the owner of the bullet

        for thisMap in levelMap:
            mapType = thisMap
            wallMap = levelMap[thisMap]
            needToRevertX = 0
            needToRevertY = 0
            self.yok = 1
            self.xok = 1
            
            try:
                #COLLISION CHECK @ C or @ D or @ H or @ G
                H, D, C, G = self.GetCollisions(wallMap, tileWidth, tileHeight)
                if (self.deltaX > 0 and (C == False or D == False)) or (self.deltaX < 0 and (H == False or G == False)):
                    if mapType == 'WallMap':
                        self.xCollidingWall = True
                    elif mapType == 'ObjectMap':
                        self.xCollidingObject = True
                    tempxok = self.xok #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
                    tempdeltaXScreenOffset = self.deltaXScreenOffset #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
                    temppersonXDelta = self.deltaX #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
                    self.xok = 0
                    self.deltaXScreenOffset = 0
                    if stickToWallsOnCollision == False:
                        self.deltaX = 0
                    needToRevertX = 1

                #COLLISION CHECK @ A or @ B or @ F or @ E REGARDLESS OF IF RESULTS ABOVE
                #IF WE HANDLED A COLLISION @ C, D, H, OR G OR NO COLLISION @ C, D, H, OR G OCCURED,
                #WOULD A COLLISION OCCUR @ A, B, F, OR E ??? (NOTE HOW THIS FORMULA IS DEPENDENT ON VARS ABOVE THAT WERE CHANGED!)
                A, E, B, F = self.GetCollisions(wallMap, tileWidth, tileHeight)
                if (self.deltaY < 0 and (A == False or B == False)) or (self.deltaY > 0 and (F == False or E == False)):
                    if mapType == 'WallMap':
                        self.yCollidingWall = True
                    elif mapType == 'ObjectMap':
                        self.yCollidingObject = True

                #RESET 1ST COLLISION CHECK PARAMATERS B/C NOW,
                #WE DON'T KNOW IF A COLLISION @ C or @ D or @ H or @ G WILL OCCUR
                #BECAUSE WE MAY HAVE HANDLED A COLLISION @ A, B, F, OR E.
                #KNOWING THIS BEFOREHAND AFFECTS THE OUTCOME OF COLLISION TEST.
                if needToRevertX == 1:
                    self.xok = tempxok
                    self.deltaXScreenOffset = tempdeltaXScreenOffset
                    self.deltaX = temppersonXDelta

                if self.yCollidingWall == True or self.yCollidingObject == True:
                    needToRevertY = 1
                    tempyok = self.yok #WE NEED TO REVERT BACK, STORE IN TEMPVAR
                    tempdeltaYScreenOffset = self.deltaYScreenOffset #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
                    temppersonYDelta = self.deltaY #WE MAY NEED TO REVERT BACK, STORE IN TEMPVAR
                    self.yok = 0
                    self.deltaYScreenOffset = 0
                    if stickToWallsOnCollision == False:
                        self.deltaY = 0

                    #COLLISION CHECK @ C or @ D or @ H or @ G REGARDLESS OF RESULTS OF COLLISION CHECK @ A or @ B or @ F or @ E
                    H, D, C, G = self.GetCollisions(wallMap, tileWidth, tileHeight)
                    if not((self.deltaX > 0 and (C == False or D == False)) or ((self.deltaX)< 0 and (H == False or G == False))):
                        if mapType == 'WallMap':
                            self.xCollidingWall = False
                        elif mapType == 'ObjectMap':
                            self.xCollidingObject = False                        
                    self.yok = tempyok
                    self.deltaYScreenOffset = tempdeltaYScreenOffset
                    self.deltaY = temppersonYDelta

            except: #This will happen when character or particle comes in contact with a part of the world that the dev forgot to design
                if needToRevertX == 1:
                    self.xok = tempxok
                    self.deltaXScreenOffset = tempdeltaXScreenOffset
                    self.deltaX = temppersonXDelta

                if needToRevertY == 1:
                    self.yok = tempyok
                    self.deltaYScreenOffset = tempdeltaYScreenOffset
                    self.deltaY = temppersonYDelta

    def GetCollisions(self, wallMap, tileWidth, tileHeight):
        NW = wallMap[int(self.yTile + ((self.yok * self.deltaY)/float(tileHeight)))][int(self.xTile + ((self.xok * self.deltaX)/float(tileWidth)))]
        SE = wallMap[int((self.height/float(tileHeight)) + self.yTile + ((self.yok * self.deltaY)/float(tileHeight)))][int((self.width/float(tileWidth)) + self.xTile + ((self.xok * self.deltaX)/float(tileWidth)))]
        NE = wallMap[int(self.yTile + ((self.yok * self.deltaY)/float(tileHeight)))][int((self.width/float(tileWidth)) + self.xTile + ((self.xok * self.deltaX)/float(tileWidth)))]
        SW = wallMap[int((self.height/float(tileHeight)) + self.yTile + ((self.yok * self.deltaY)/float(tileHeight)))][int(self.xTile + ((self.xok * self.deltaX)/float(tileWidth)))]

        if NW == None:
            NW = True
        else:
            NW = NW.walkThroughPossible
        if NE == None:
            NE = True
        else:
            NE = NE.walkThroughPossible
        if SE == None:
            SE = True
        else:
            SE = SE.walkThroughPossible
        if SW == None:
            SW = True
        else:
            SW = SW.walkThroughPossible
        return NW, SE, NE, SW

    #Abstract Method
    def HandleWorldObjectCollision(self, stickToWallsOnCollision, gravity):
        pass

    def TestCharacterCollision(self):
        pass

    def HandleCharacterCollision(self):
        pass

class Weapon(WorldObject):
    def __init__(self, name, damage, ammo, physIndic, physicsCount, generateBulletWidth, generateBulletHeight, generateBulletSpeed, gravity, gravityCoefficient = .00005):
        self.name = name
        self.damage = damage
        self.ammo = ammo
        self.physicsIndicator = physIndic
        self.physicsCounter = physicsCount
        self.generateBulletWidth = generateBulletWidth
        self.generateBulletHeight = generateBulletHeight
        self.generateBulletSpeed = generateBulletSpeed
        self.gravityApplies = gravity
        self.gravityCoefficient = gravityCoefficient

class Bullet(WorldObject):
    #Name, weapon, world X Loc, world Y Loc,  deltaX,    deltaY, damage, physics actions remaining, particle width px, particle height px, frame speed, default speed, image, particlePhysicsLevel
    #if particlePhysicsLevel >= wallPhysicsLevel + 3 then particle pushes the wall
    #if particlePhysicsLevel = wallPhysicsLevel + 2 then particle goes through wall
    #if particlePhysicsLevel = wallPhysicsLevel + 1 then particle bounces off wall
    #if particlePhysicsLevel <= wallPhysicsLevel then particle absorbs into wall

    #physics actions represent the number of remaining times the particle can push/go through/bounce off walls

    #Name, weapon, world X Loc, world Y Loc,  deltaX,    deltaY, damage, bounces remaining, bullet width px, bullet height px, frame speed, default speed, image
    
    def __init__(self, name, weapon, xTile, yTile, deltaX, deltaY, damage, physicsIndicator, physicsCounter, width, height, character, speed = .01, defaultSpeed = .01, img=None, gravity = False, gravityCoefficient = .00005, boundToCamera = False):
        self.name = name
        self.defaultSpeed = defaultSpeed
        self.speed = speed
        self.xTile = xTile
        self.yTile = yTile
        self.angle = 0
        self.SetDeltaXDeltaY(deltaX, deltaY)
        self.width = width
        self.height = height
        self.damage = damage
        self.physicsIndicator = physicsIndicator
        self.physicsCounter = physicsCounter
        self.cameFromObjectName = weapon
        self.cameFromCharacter = character #To handle scenarios when you don't want your own bullets to injure you.
        self.img = img
        self.imagesGFXName = "../Images/bullets.png"
        self.imagesGFXNameDesc = "Bullets"
        self.imagesGFXRows = 4
        self.imagesGFXColumns = 1
        self.weapon = weapon
        self.gravityApplies = gravity
        self.gravityYDelta = 0
        self.timeSpentFalling = 0
        self.needToDelete = False
        self.boundToCamera = boundToCamera
        self.deltaXScreenOffset = 0
        self.deltaYScreenOffset = 0
        self.UpdateAngle()
        self.gravityCoefficient = gravityCoefficient

    def Move(self, wallMap, tileWidth, tileHeight):
        #MOVE PARTICLES
        self.xTile = self.xTile + (self.deltaX/tileWidth)
        self.yTile = self.yTile + (self.deltaY/tileHeight)

        #TODO: COLLISION DETECT IF WALL HIT, AND BOUNCE/PERFORM ACTION IF NECESSARY

    def HandleWorldObjectCollision(self, stickToWallsOnCollision, gravity):
        tempDeltaX = self.deltaX
        tempDeltaY = self.deltaY
        if self.xCollidingWall == 1 or self.yCollidingWall == 1:
            if self.physicsIndicator == "Bounce":
                self.physicsCounter = max(self.physicsCounter - 1, -2)
                if self.physicsCounter != -1:
                    if self.xCollidingWall == 1:
                        tempDeltaX = -self.deltaX
                    if self.yCollidingWall == 1:
                        tempDeltaY = -self.deltaY
                    self.SetDeltaXDeltaY(tempDeltaX, tempDeltaY)
                else:
                    self.needToDelete = True

            if self.physicsIndicator == "Absorb":
                self.needToDelete = True

            if self.physicsIndicator == "Pass Through":
                pass

class AI(object):
    pass

class Character(WorldObject):
    def __init__(self, name = "", imagesGFXName = "../Images/userPlayer.png", boundToCamera = False, xTile = 18, yTile = 18, deltaX = 0, deltaY = 0, timeSpentFalling = 0, gravityYDelta = 0, imgDirectionIndex = 0, imgLegIndex = 0, millisecondsOnEachLeg = 250, numberOfFramesAnimPerWalk = 3, pictureXPadding = 0, pictureYPadding = 0, defaultSpeed = .5, ammo = 1000, activeWeapon = 0, score = 0, weapons = [], inventory = [], width = 32, height = 32, shotsFiredFromMe = False, gravity = False, gravityCoefficient = .00005, ID = 0):
        #GENERAL
        self.name = name
        self.numberOfFramesAnimPerWalk = numberOfFramesAnimPerWalk #3
        self.numberOfDirectionsFacingToDisplay = 8
        self.imagesGFXName = imagesGFXName
        self.imagesGFXNameDesc = "User Player"
        self.imagesGFXRows = self.numberOfDirectionsFacingToDisplay
        self.imagesGFXColumns = self.numberOfFramesAnimPerWalk
        self.pictureXPadding = pictureXPadding
        self.pictureYPadding = pictureYPadding
        self.ID = ID

        #LOCATION/APPEARANCE
        self.xTile = xTile
        self.yTile = yTile
        self.x = 0 #THIS WILL ALWAYS BE CALCULATED BY THE GAME
        self.y = 0 #THIS WILL ALWAYS BE CALCULATED BY THE GAME
        self.xok = 1
        self.yok = 1
        self.angle = 0 #TODO: add this property to database
        #self.deltaX = deltaX #specifies the change in xTile on the next frame
        #self.deltaY = deltaY #specifies the change in yTile on the next frame
        self.SetDeltaXDeltaY(deltaX, deltaY) #specifies the change in xTile on the next frame
        self.fireAngle = self.angle
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
        self.shotsFiredFromMe = shotsFiredFromMe
        self.weapons = weapons
        self.gravityApplies = gravity
        self.gravityCoefficient = gravityCoefficient
        

    def InitializeScreenPosition(self, camera, tileWidth, tileHeight):
        #self.x = ((self.xTile - 1) - camera.xTile) * tileWidth
        #self.y = ((self.yTile - 1) - camera.yTile) * tileHeight
        pass

    def Move(self, camera, tileWidth, tileHeight): #TODO: Make this inherit from WorldObjects, and support bullets being bound to camera
        #if self.xok == 1: # and self.deltaX != 0:
        #print("old: " + str(1 + camera.xTile + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + (self.x/float(tileWidth))) + " new: " + str(self.xTile + (self.deltaX/float(tileWidth))) + " delta: " + str(((1 + camera.xTile + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + (self.x/float(tileWidth)))  - (self.xTile + (self.deltaX/float(tileWidth)))) * tileWidth) + " verf: " + str((self.deltaX/tileWidth) * tileWidth))
        #print("Camera xTile: " + str(camera.xTile) + " + self.x: " + str((self.x)/float(tileWidth)) + " xTile: " + str(self.xTile) + " deltax: " + str(self.deltaX/float(tileWidth)))
        #self.x = self.x + self.deltaX + self.deltaXScreenOffset #MOVE USER'S CHARACTER, BUT DON'T MOVE HIM IN ONE DIRECTION IF THE SCREEN SCROLL IS ALSO MOVING IN THAT DIRECTION
        self.x = -((1*tileWidth) + (camera.xTile*tileWidth) - (camera.viewToScreenPxlOffsetX) - (self.xTile*tileWidth))
        #self.xTile = 1 + camera.xTile + (-camera.viewToScreenPxlOffsetX/float(tileWidth)) + (self.x/float(tileWidth)) #0 BASED, JUST LIKE THE ARRAY, THIS IS LEFT MOST POINT OF USER'S CHAR)
        self.xTile = self.xTile + (self.deltaX/float(tileWidth))
        #if self.yok == 1 and self.deltaY != 0:
        #self.y = self.y + self.deltaY + self.deltaYScreenOffset #MOVE USER'S CHARACTER, BUT DON'T MOVE HIM IN ONE DIRECTION IF THE SCREEN SCROLL IS ALSO MOVING IN THAT DIRECTION
        self.y = -((1*tileHeight) + (camera.yTile*tileHeight) - (camera.viewToScreenPxlOffsetY) - (self.yTile*tileHeight))
        #self.yTile = 1 + camera.yTile + (-camera.viewToScreenPxlOffsetY/float(tileHeight)) + (self.y/float(tileHeight)) #0 BASED, JUST LIKE THE ARRAY, THIS IS TOP MOST POINT OF USER'S CHAR
        self.yTile = self.yTile + (self.deltaY/float(tileHeight))

    def UpdateFireAngle(self, levelGravity):
        if levelGravity == True and self.gravityApplies == True:
            if self.deltaX < 0:
                self.fireAngle = 180
            elif self.deltaX > 0:
                self.fireAngle = 0            
        else:
            self.fireAngle = self.angle

    def GetLocationInWorld(self):
        return [self.xTile + 1, self.yTile + 1] #UNITS IN WORLD TILES

    def GetLocationOnScreen(self):
        return [self.x, self.y] #UNITS IN SCREEN PIXELS

    def TestIfLocationVisibleOnScreen(self):
        pass

    #Overrides parent method
    def HandleWorldObjectOrEdgeCollision(self, stickToWallsOnCollision, gravity):
        self.xok = 1
        self.yok = 1
        tempDeltaX = self.deltaX
        tempDeltaY = self.deltaY
        #Walls/Objects/World Edge:
        if self.yCollidingWall == True or self.atWorldEdgeY == 1 or self.yCollidingObject == 1:
            self.yok = 0
            self.deltaYScreenOffset = 0
            if stickToWallsOnCollision == False:
                tempDeltaY = 0
            if gravity == True and self.gravityYDelta != 0 and self.deltaY + self.gravityYDelta > 0:
                self.gravityYDelta = 0
                self.timeSpentFalling = 0
                tempDeltaY = 0
        if self.xCollidingWall == True or self.atWorldEdgeX == 1 or self.xCollidingObject == 1:
            self.xok = 0
            self.deltaXScreenOffset = 0
            if stickToWallsOnCollision == False:
                tempDeltaX = 0
        self.SetDeltaXDeltaY(tempDeltaX, tempDeltaY)

    def DetermineCharPicBasedOnDirectionFacing(self, levelGravity):
        if levelGravity == True and self.gravityApplies == True:
            angleToDeterminPic = self.fireAngle
        else:
            angleToDeterminPic = self.angle
        self.imgDirectionIndex = int(((angleToDeterminPic + (360 / (self.numberOfDirectionsFacingToDisplay * 2))) % 360) / (360 / self.numberOfDirectionsFacingToDisplay))

    def DetermineCharPicBasedOnWalkOrMovement(self, millisecondsSinceLastFrame):
        if self.deltaX == 0 and self.deltaY == 0:
            #self.imgLegIndex = 0
            #self.millisecondsOnThisLeg = 0
            pass
        else:
            if (self.millisecondsOnThisLeg >= self.millisecondsOnEachLeg):
                self.imgLegIndex = (self.imgLegIndex + 1) % self.numberOfFramesAnimPerWalk
                self.millisecondsOnThisLeg = self.millisecondsOnThisLeg % self.millisecondsOnEachLeg
            else:
                self.millisecondsOnThisLeg = self.millisecondsOnThisLeg + millisecondsSinceLastFrame

    def Attack(self):
        pass

class Camera(GamePlayObject):
    def __init__(self, screenResSelection, DisplayType, x, y, bindingCharacter, xPercentBound, yPercentBound):
        self.screenResSelection = screenResSelection
        self.DisplayType = DisplayType
        self.xTile = x #Camera view X-coord measured in tiles
        self.yTile = y - 1#Camera view Y-coord measured in tiles
        self.viewToScreenPxlOffsetX = 0 #Offset the camera view X-coord to the screen based on Player fractional tile movement, in pixels
        self.viewToScreenPxlOffsetY = 0 #Offset the camera view Y-coord to the screen based on Player fractional tile movement, in pixels
        self.zoom = 1
        self.xPercentBound = xPercentBound
        self.yPercentBound = yPercentBound
        self.boundCharacter = bindingCharacter
        self.screenResChoices = pygame.display.list_modes()
        bindingCharacter.boundToCamera = True

    def UpdateScreenSettings(self):
        self.DisplayWidth = self.screenResChoices[self.screenResSelection][0]
        self.DisplayHeight = self.screenResChoices[self.screenResSelection][1]
        #self.DisplayWidth = DisplayWidth #1280 #960
        #self.DisplayHeight = DisplayHeight #720 #54
        if self.DisplayType == "Full Screen":
            gameDisplay = pygame.display.set_mode((self.DisplayWidth, self.DisplayHeight), pygame.FULLSCREEN)
        else:
            gameDisplay = pygame.display.set_mode((self.DisplayWidth, self.DisplayHeight))
        return gameDisplay
        #TODO: Resolution/screen size change can put character outside of camera view
        #TODO: Resolution/screen size change can put camera view outside of world
        #TODO: Resolution/screen size can be larger than the world itself, 
        #   thus the world must be centered for attractive appearance

    #Overrides inherited method
    def TestIfAtWorldEdgeCollision(self, wallMap, tileWidth, tileHeight):
        #SNAP TO THE EDGE OF THE WORLD IF PAST IT
        self.atWorldEdgeX = False
        self.atWorldEdgeY = False
            #camera X  +      tiles on screen              +        frac. person next move         +   frac camera X                                         
        if (1 + self.xTile + (self.DisplayWidth/float(tileWidth)) + (self.boundCharacter.deltaX/float(tileWidth)) - (self.viewToScreenPxlOffsetX/float(tileWidth)) >= len(wallMap[0])) and self.boundCharacter.deltaX > 0:
            self.viewToScreenPxlOffsetX = (float(float(self.DisplayWidth/float(tileWidth)) - int(self.DisplayWidth/float(tileWidth))))*tileWidth
            self.xTile = int(len(wallMap[0]) - int(self.DisplayWidth/float(tileWidth))) - 1
            self.atWorldEdgeX = True
        if (1 + self.xTile - self.viewToScreenPxlOffsetX/float(tileWidth) + (self.boundCharacter.deltaX/float(tileWidth)) <= 0 and self.boundCharacter.deltaX <0):
            self.xTile = -1
            self.viewToScreenPxlOffsetX = 0
            self.atWorldEdgeX = True
        if (1 + self.yTile + (self.DisplayHeight/float(tileHeight)) + (self.boundCharacter.deltaY/float(tileHeight)) - (self.viewToScreenPxlOffsetY/float(tileHeight)) >= len(wallMap)) and self.boundCharacter.deltaY > 0:
            self.viewToScreenPxlOffsetY = (float(float(self.DisplayHeight/float(tileHeight)) - int(self.DisplayHeight/float(tileHeight))))*tileHeight
            self.yTile = int(len(wallMap) - int(self.DisplayHeight/float(tileHeight))) - 1
            self.atWorldEdgeY = True
        if (1 + self.yTile - self.viewToScreenPxlOffsetY/float(tileHeight) + (self.boundCharacter.deltaY/float(tileHeight)) <= 0 and self.boundCharacter.deltaY < 0):
            self.yTile = -1
            self.viewToScreenPxlOffsetY = 0
            self.atWorldEdgeY = True

    def Move(self, tileWidth, tileHeight, deltaX = 0, deltaY = 0):#, deltaZ = 0, deltaZoom = 0):
        self.viewToScreenPxlOffsetY = self.viewToScreenPxlOffsetY - deltaY #MOVE CAMERA ALONG Y AXIS
        self.viewToScreenPxlOffsetX = self.viewToScreenPxlOffsetX - deltaX #MOVE CAMERA ALONG X AXIS
        self.RefreshViewCoords(tileWidth, tileHeight)

    def MoveBasedOnBoundCharacterMovement(self, tileHeight, tileWidth, levelWidth, levelHeight):

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

        if self.boundCharacter != None:
            #QUESTIONABLE TODO: IF CHARACTER IS PRESSING AGAINST BLOCK, BUT OUTSIDE OF MIDDLE 9TH AND CAMERA CAN MOVE FURTHER BEFORE HITTING THE EDGE OF THE WORLD, THEN MOVE CAMERA, BUT NOT THE PERSON??

            #*UNLESS SCREEN SCROLLING PUTS CAMERA VIEW OUTSIDE OF THE WORLD
            #(IS PLAYER MOVING TO THE LEFT TO LEAVE MIDDLE THIRD AND IS IT NOT THE CASE THAT SCREEN SCROLLING WOULD PLACE THE CAMERA FARTHER LEFT THAN WORLD START)    OR    (IS PLAYER MOVING TO THE RIGHT TO LEAVE MIDDLE THIRD AND IS IT NOT THE CASE THAT SCREEN SCROLLING WOULD PLACE CAMERA FARTHER RIGHT THAN WORLD END)?
            if self.boundCharacter.xok == 1 and self.atWorldEdgeX == False and ((self.boundCharacter.deltaX < 0 and self.boundCharacter.x + self.boundCharacter.deltaX < (self.DisplayWidth)*((1-self.xPercentBound)/2.0)) or (self.boundCharacter.deltaX >0 and self.boundCharacter.x + self.boundCharacter.width + self.boundCharacter.deltaX > (self.DisplayWidth)*((1-self.xPercentBound)/2.0 + self.xPercentBound))):
                self.Move(tileWidth, tileHeight, deltaX = self.boundCharacter.deltaX) #MOVE CAMERA ALONG X AXIS
                self.boundCharacter.deltaXScreenOffset = -self.boundCharacter.deltaX #KEEP PLAYER'S CHARACTER FIXED @ MIDDLE 9TH EDGE

            else:
                self.boundCharacter.deltaXScreenOffset = 0

            if self.boundCharacter.yok == 1 and self.atWorldEdgeY == False and ((self.boundCharacter.deltaY < 0 and self.boundCharacter.y + self.boundCharacter.deltaY < (self.DisplayHeight)*((1-self.yPercentBound)/2.0)) or (self.boundCharacter.deltaY >0 and self.boundCharacter.y + self.boundCharacter.height + self.boundCharacter.deltaY > (self.DisplayHeight)*((1-self.yPercentBound)/2.0 + self.yPercentBound))):
                self.Move(tileWidth, tileHeight, deltaY = self.boundCharacter.deltaY) #MOVE CAMERA ALONG Y AXIS
                self.boundCharacter.deltaYScreenOffset = -self.boundCharacter.deltaY #KEEP PLAYER'S CHARACTER FIXED @ MIDDLE 9TH EDGE
            else:
                self.boundCharacter.deltaYScreenOffset = 0

    def RefreshViewCoords(self, tileWidth, tileHeight):
        #CAMERA MOVES IN PIXELS, BUT THE WORLD IS BUILT IN TILES.
        #WHEN SCREEN MOVES IN PIXELS WITH USER'S MOVEMENT, THIS
        #IS STORED IN cameraViewToScreenPxlOffsetX/Y. BUT IF USER'S
        #MOVEMENT (AND THEREFORE, cameraViewToScreenPxlOffsetX/Y) GOES BEYOND
        #THE SIZE OF A TILE, THEN TAKE AWAY THE TILE SIZE FROM THE 
        #cameraViewToScreenPxlOffsetX/Y, AND CONSIDER THAT THE CAMERA HAS MOVED
        #1 TILE IN DISTANCE IN THE WORLD. THIS IS IMPORTANT IN
        #ACCURATELY TRACKING THE CAMERA'S LOCATION COORDINATES.
        if self.viewToScreenPxlOffsetX >= tileWidth:
            self.viewToScreenPxlOffsetX = self.viewToScreenPxlOffsetX - tileWidth
            self.xTile = self.xTile - 1
            
        elif self.viewToScreenPxlOffsetX <0:
            self.viewToScreenPxlOffsetX = self.viewToScreenPxlOffsetX + tileWidth
            self.xTile = self.xTile + 1

        if self.viewToScreenPxlOffsetY >= tileHeight:
            self.viewToScreenPxlOffsetY = self.viewToScreenPxlOffsetY - tileHeight
            self.yTile = self.yTile - 1

        elif self.viewToScreenPxlOffsetY <0:
            self.viewToScreenPxlOffsetY = self.viewToScreenPxlOffsetY + tileHeight
            self.yTile = self.yTile + 1

    def GetLocationInWorld(self, tileHeight, tileWidth):
        return [1 + self.xTile - (self.viewToScreenPxlOffsetX/float(tileWidth)), 1 + self.yTile - (self.viewToScreenPxlOffsetY/float(tileHeight))]

    def SetLocationInWorld(self, x, y, tileHeight, tileWidth):
        pass
        #self.xTile = (self.viewToScreenPxlOffsetX/float(tileWidth)) + x - 1
        #self.yTile = (self.viewToScreenPxlOffsetY/float(tileHeight)) + y - 1

    def ValidatePosition(self, gameDisplay):
        #CAN'T BE BEYOND WORLD EDGES
            #WHAT IF CAMERA VIEW IS LARGER THAN WORLD SIZE?
        #CAN'T PUT USER CHARACTER OUTSIDE OF INNER NINTH IF CAMERA CAN MOVE CLOSER TO WORLD EDGE
        pass
