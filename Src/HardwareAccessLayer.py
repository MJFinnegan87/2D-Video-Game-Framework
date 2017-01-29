import pygame
from Controllers import *

class Hardware(Controller):
    def __init__(self):
        self.gameEvents = {}
        self.characterEvents = {}
        #TODO: Load user defined controls from database

    def GetConfiguredControls(self):
        pass

    def PollHardware(self):
        #Use deployment/language specific library to poll hardware
        self.HWEventList = pygame.event.get()
        self.keys = pygame.key.get_pressed()

        #Map key and hardware event queues to associative arrays that the game cares about
        self.gameEvents = {}
        self.characterEvents = {}
        self.gameEvents["saved"] = False
        self.characterEvents["activeWeapon"] = None
        self.characterEvents["shotsFiredFromMe"] = False
        self.characterEvents["right"] = False
        self.characterEvents["left"] = False
        self.characterEvents["up"] = False
        self.characterEvents["down"] = False

        
        self.GetKeyPresses()
        self.GetKeysDown()

    def GetKeyPresses(self):
        #Gets keys pressed for the first time
        #TODO: Add joystick/controller handling
        for pyEvent in self.HWEventList:     #ASK WHAT EVENTS OCCURRED
            #IF PLAYER MUST PRESS TRIGGER REPEATEDLY, FIRE ON KEY DOWN:
            if pyEvent.type == pygame.KEYDOWN:
                if pyEvent.key == pygame.K_s:
                    self.gameEvents["saved"] = True
                if pyEvent.key == pygame.K_SPACE:
                    self.characterEvents["shotsFiredFromMe"] = True
                if pyEvent.key == pygame.K_KP1 or pyEvent.key == pygame.K_1:
                    self.characterEvents["activeWeapon"] = 0
                if pyEvent.key == pygame.K_KP2 or pyEvent.key == pygame.K_2:
                    self.characterEvents["activeWeapon"] = 1
                if pyEvent.key == pygame.K_KP3 or pyEvent.key == pygame.K_3:
                    self.characterEvents["activeWeapon"] = 2
                if pyEvent.key == pygame.K_KP4 or pyEvent.key == pygame.K_4:
                    self.characterEvents["activeWeapon"] = 3
                if pyEvent.key == pygame.K_KP_ENTER or pyEvent.key == pygame.K_RETURN:
                    self.gameEvents["enterPressed"] = True

    def GetKeysDown(self):
        #Gets keys held down
        #TODO: Add joystick/controller handling

        if self.keys[pygame.K_RIGHT] and not self.keys[pygame.K_LEFT]:
            self.characterEvents["right"] = True
        if self.keys[pygame.K_LEFT] and not self.keys[pygame.K_RIGHT]:
            self.characterEvents["left"] = True
        if self.keys[pygame.K_UP] and not self.keys[pygame.K_DOWN]:
            self.characterEvents["up"] = True
        if self.keys[pygame.K_DOWN] and not self.keys[pygame.K_UP]:
            self.characterEvents["down"] = True


class Cursor(object):
    def __init__(self):
        self.coords = (0,0)
        self.btn = (0,0,0)
        self.xTile = 0
        self.yTile = 0
        self.blockWidth = 0
        self.blockHeight = 0
