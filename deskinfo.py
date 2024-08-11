import os

drawingQueue = []; """don't you dare hack this"""
interval = []; """CPU Calculation time"""
clickOnce = False; """Activates special things once, like buttons"""
desktopIsDoing = False; """Desktop is very busy"""
prevMousePos = [0, 0]
mousePos = [0, 0]
mouseEvents = [False, False, False]; """Current Mouse clicks in right order: Left, Middle (Scroll Button), Right"""
screenSize = [640, 480]
detailLevel = 0; """How detailed do we render screen, 0 is classic."""

availableApplications = []; """Everything from ./Programs"""
runningApplications = []; """The Applications that are currently running, those are Devices and even services."""
devices = []; """The Devices that were hidden in pockets, we need to remember them for variables"""
drawDeviceIndex = -1; """If index equals to -1, then don't render any device."""

def get_deltatime() -> float:
    if len(interval) == 2: return interval[0] - interval[1]

def get_mousespeed() -> list[int]:
    return [mousePos[0] - prevMousePos[0], mousePos[1] - prevMousePos[1]]

class Application():
    __type__: str = "service"
    name: str = "Unnamed"
    isBusy: bool = False # Give full control to Application when doing something
    needsExpert: bool = False # SUDO mode
    close: bool = False; """set to True when Application should not run anymore"""
    secretDevice: bool = False

    def __init__(self):
        print("Starting " + self.name)

    def shutdown(self):
        print("Closing " + self.name)

class DeviceElement():
    __type__: str = "element"
    pos: list[int, int] = [0, 0]
    size: list[int, int] = [128,16]
    disabled = False; """Don't draw and give logic to this Element"""
    shadows: bool = True
    callFunction: callable or None = None