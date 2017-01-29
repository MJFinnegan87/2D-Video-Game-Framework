from Models import *
import json
import sqlite3
import copy
from io import StringIO as StringIO

class DataAccessLayer(object):
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

    def __init__(self, fileName):
        self.fileName = fileName

    def ValidateDB(self):
        try:
            self.GetNumberOfLevels()
            if self.numberOfLevels == 0:
                return 0
        except:
            return 0
        finally:
            return 1

    def ConvertMapsToJSON(self, wallMap, objectMap):
        Marshaller = JSONConverter()
        wallMapJSON = None
        wallMapWithSerializedObjects = [[]]
        for h in range(len(wallMap)):
            if h != 0:
                wallMapWithSerializedObjects.append([])
            wallMapWithSerializedObjects[h].extend([0] *len(wallMap[0]))

        for i in range(len(wallMap)):
            for j in range(len(wallMap[0])):
                wallMapWithSerializedObjects[i][j] = Marshaller.toJSON(wallMap[i][j])
        wallMapJSON = Marshaller.toJSON(wallMapWithSerializedObjects)

        objectMapJSON = None
        objectMapWithSerializedObjects = [[]]
        for h in range(len(objectMap)):
            if h != 0:
                objectMapWithSerializedObjects.append([])
            objectMapWithSerializedObjects[h].extend([0] *len(objectMap[0]))

        for i in range(len(objectMap)):
            for j in range(len(objectMap[0])):
                objectMapWithSerializedObjects[i][j] = Marshaller.toJSON(objectMap[i][j])
        objectMapJSON = Marshaller.toJSON(objectMapWithSerializedObjects)
        return 

    def ConvertJSONToMaps(self, JSONWallData, JSONObjectData):
        Marshaller = self.JSONConverter()
        #print Marshaller.fromJSON(JSONWallData)
        wallMapJSON = copy.deepcopy(Marshaller.fromJSON(JSONWallData, "WallData"))
        objectMapJSON = copy.deepcopy(Marshaller.fromJSON(JSONObjectData, "ObjectData"))
        
        for i in range(len(wallMapJSON)):
            for j in range(len(wallMapJSON[0])):
                wallMapJSON[i][j] = Marshaller.fromJSON(str(wallMapJSON[i][j]), "WallData")
        
        for i in range(len(objectMapJSON)):
            for j in range(len(objectMapJSON[0])):
                objectMapJSON[i][j] = Marshaller.fromJSON(str(objectMapJSON[i][j]), "ObjectData")

        wallMap = copy.deepcopy(wallMapJSON)
        objectMap = copy.deepcopy(objectMapJSON)
        return wallMap, objectMap

    def LoadWallObjects(self):
        WallObjectData = []
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute('SELECT * FROM WallObjects')
        for wall in c:
            WallObjectData.append(WallObject(wall[0], wall[1], wall[2], wall[3], wall[4], wall[5], wall[6], wall[7], wall[8], wall[9]))
        connection.close()
        return WallObjectData

    def LoadWorldObjects(self):
        WorldObjectData = []
        connection = sqlite3.connect(self.fileName)
        c = connection.cursor()
        c.execute('SELECT * FROM WorldObjects')
        for obj in c:
            WorldObjectData.append(WorldObject(obj[0], obj[1], obj[2], obj[3], obj[4], obj[5], obj[6], obj[7], obj[8], obj[9], obj[10], obj[11], obj[12], obj[13]))
        connection.close()
        return WorldObjectData

    def Load(self, index, wallObjects, worldObejcts):
        if self.VerifyLevelExists(index) > 0:
            connection = sqlite3.connect(self.fileName)
            c = connection.cursor()
            c.execute('SELECT * FROM Levels WHERE IndexPK =?', str(index))
            levelData = c.fetchone()
            connection.close()
            activeLevel = Level(self)
            activeLevel.index = index
            activeLevel.name = levelData[1]
            activeLevel.description = levelData[2]
            activeLevel.weather = levelData[3]
            activeLevel.sideScroller = levelData[4]

            #with open(StringIO(levelData[5]).read(), 'r') as f:
                #with open(StringIO(levelData[6]).read(), 'r') as g:
                    #level.JSONToMaps(f , g)
            activeLevel.wallMap, activeLevel.objectMap = activeLevel.JSONToMaps(levelData[5], levelData[6])
            #level.wallMap = levelData[4]
            #level.objectMap = levelData[5]
            for y in range(len(activeLevel.wallMap)):
                for x in range(len(activeLevel.wallMap[0])):
                    activeLevel.wallMap[y][x] = activeLevel.wallMap[y][x]

            for y in range(len(activeLevel.objectMap)):
                for x in range(len(activeLevel.objectMap[0])):
                    activeLevel.objectMap[y][x] = activeLevel.objectMap[y][x]

            activeLevel.music = levelData[7]
            activeLevel.loopMusic = levelData[8]
            activeLevel.startX = levelData[9]
            activeLevel.startY = levelData[10]
            activeLevel.startXFacing = levelData[11]
            activeLevel.startYFacing = levelData[12]
            activeLevel.gravity = levelData[13]
            activeLevel.stickToWallsOnCollision = levelData[14]
            activeLevel.levelHeight = levelData[15]
            activeLevel.levelWidth = levelData[16]
            activeLevel.tileSheetRows = levelData[17]
            activeLevel.tileSheetColumns = levelData[18]
            activeLevel.tileWidth = levelData[19]
            activeLevel.tileHeight = levelData[20]
            activeLevel.tileXPadding = levelData[21]
            activeLevel.tileYPadding = levelData[22]
            #return Level(index, name, description, weather, sideScroller, wallMap, objectMap, music, loopMusic, startX, startY, startXFacing, startYFacing, xSize, ySize, gravity, stickToWallsOnCollision, tileSheetRows, tileSheetColumns, tileWidth, tileHeight, tileXPadding, tileYPadding)
            return activeLevel
        else:
            return None

    def Save(self):
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
                      sqlite3.Binary(self.activeLevel.wallMapJSON),
                      sqlite3.Binary(self.activeLevel.objectMapJSON),
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
        else:
            connection = sqlite3.connect(self.fileName)
            c = connection.cursor()
            c.execute("INSERT INTO Levels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (self.activeLevel.index,
                      self.activeLevel.name,
                      self.activeLevel.description,
                      self.activeLevel.weather,
                      self.activeLevel.sideScroller,
                      sqlite3.Binary(self.activeLevel.wallMapJSON),
                      sqlite3.Binary(self.activeLevel.objectMapJSON),
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
        connection.commit()
        connection.close()

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
            c.execute("CREATE TABLE Levels (IndexPK INT, Name TEXT, Description TEXT, Weather TEXT, SideScroller BOOL, WallMap BLOB, ObjectMap BLOB, music TEXT, loopMusic BOOL, startX INT, startY INT, startXFacing INT, startYFacing INT, gravity BOOL, stickToWallsOnCollision BOOL, levelHeight INT, levelWidth INT, tileSheetRows INT, tileSheetColumns INT, tileWidth INT, tileHeight INT, tileXPadding INT, tileYPadding INT)")
            #print "reset 5"
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

    def VerifyLevelExists(self, index):
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
