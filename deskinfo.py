import os

drawingQueue = []; """don't you dare hack this"""
interval = []; """CPU Calculation time"""
clickOnce = False; """Activates special things once, like buttons"""
desktopIsDoing = False; """Desktop is very busy"""
mousePos = [0, 0]
mouseEvents = [False, False, False]; """Current Mouse clicks in right order: Left, Middle (Scroll Button), Right"""
screenSize = [640, 480]

availableApplications = []
runningApplications = []
drawDevice = []

class Application():
    name: str = "Unnamed"
    isBusy: bool = False # Give full control to Application when doing something
    needsExpert: bool = False # SUDO mode
    close: bool = False # set to True when Application should not run anymore

    def __init__(self):
        print("Starting " + self.name)

    def shutdown(self):
        print("Closing " + self.name)

class DeviceElement():
    pos: list[int, int] = [0, 0]
    size: list[int, int] = [128,16]
    disabled = False; """Don't draw and give logic to this Element"""