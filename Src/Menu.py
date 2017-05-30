import pygame

class Menu(object):
    def __init__(self):
        pass

class MenuView(object):
    def __init__(self, display, backgroundColor, backgroundPicture, xScroll, yScroll):
        pass

class MenuController(object):
    def __init__(self):
        pass

class MenuItem(object):
    def __init__(self, text, unselectedColor, selectedColor, fontSize, horizAlign, vertAlign, selectionChoices, defaultSelection, controllerAction, modelValue):
        self.text = text
        self.unselectedColor = unselectedColor
        self.selectedColor = selectedColor
        self.fontSize = fontSize
        self.horizAlign = horizAlign
        self.vertAlign = vertAlign
        self.selectionChoices = selectionChoices
        self.defaultSelection = defaultSelection
        self.modelValue = modelValue
        self.controllerAction = controllerAction

class MainMenu(Menu):
    def __init__(self, modelValues):
        self.title = "2D Game"
        self.menuItems = [Play("Play", [255,255,255], [255,0,0], 12, 1, 1, None, None, ["Action", "Value"], None), MenuItem("Difficulty: ", [255,255,255], [255,0,0], 12, 1, 1, ["Easy", "Medium", "Hard", "Expert"], 0, ["Value"], modelValues[0]), MenuItem("Screen Mode: ", [255,255,255], [255,0,0], 12, 1, 1, ["Window", "Full Screen"], 0, ["Value", "Action"], screenMode), MenuItem("Exit", [255,255,255], [255,0,0], 12, 1, 1, [], None, None, None)]


class Play(MenuItem):
    def __init__(self):
        pass

    def Action(self):
        return 
