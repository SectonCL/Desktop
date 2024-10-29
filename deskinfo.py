"""SCLDesktop - DeskInfo
Contains pretty much every information about current session - from version to drawing queue.
It is also automatically updated.
You can, for example, get the screen size here or the mouse position.
You have the power to modify them, because... It's a python script of course!"""
import enum
import os
import skia
from fileinput import close


"""DrawingQueue is a dictionary that contains only 3 levels of draw access:
  0. Draw before everything
  1. Draw in Device
  2. Draw after everything

They're all equal to a list that contains instruction lists:
	0: Instruction Type (0 is Rectangle, 1 is Text and 2 is Line)
	1: Position
	2:
		For Rectangles, the size
		For Text, the text, literally.
		For lines, the ending position (not relative)
	3:
""" # TODO: Finish this comment!
drawingQueue = {0: [], 1: [], 2: []}
directDraw   = {0: [], 1: [], 2: []}
"""DirectDraw: Not to be confused with Micro$oft's DX.
Example for text:
	0. Type (0: Rectangle, 1: TextBlob, 2: Path)
	1. Drawable (TextBlob)
	2. Painter (Paint)
Read more info in Docs."""

version = 0.5
edition = "Developer Preview";         """Something like "Beta", or "Alpha"."""
debugMode = False;        """Makes some calculations visualized"""
interval = [];            """CPU Calculation time"""
desktopIsBusy = False;    """Desktop is very busy"""
screenSize = [1280, 960]

prevMousePos = [0, 0];               """Mouse Position in a previous frame."""
mousePos = [0, 0]
clickOnce = False;                   """Activates special things once, like buttons. Is true only on first frame the LMB is pressed"""
mouseEvents = [False, False, False]; """Current Mouse clicks in right order: Left, Middle (Scroll Button), Right"""

detailLevel = 1;      """How detailed do we render screen, 0 is classic."""
useAnimations = True

availableApplications = []; """Everything from ./Programs"""
runningApplications = [];   """The Applications that are currently running, those are Devices and even services."""
devices = [];               """The Devices that were hidden in pockets, we need to remember them for variables"""
drawDeviceIndex = -1;       """If index equals to -1, then don't render any device."""

def get_deltatime() -> float:
	if len(interval) == 2: return interval[1] - interval[0]

def get_mousespeed() -> list[int]: return [mousePos[0] - prevMousePos[0], mousePos[1] - prevMousePos[1]]

class Application:
	__type__: str = "service"
	name: str = "Unnamed"
	isBusy: bool = False # Give full control to Application when doing something
	needsExpert: bool = False # SUDO mode
	close: bool = False; """set to True when Application should not run anymore"""
	secretDevice: bool = False
	singular: bool = False; """Limit launching this Application to one process"""

	def __init__(self): print("Starting " + self.name)
	def shutdown(self): print("Closing " + self.name); self.close = True

class DeviceElement:
	__type__: str = "element"
	pos: list[int, int] = [0, 0]
	size: list[int, int] = [128,16]
	disabled = False; """Don't draw and give logic to this Element"""
	shadows: bool = True
	callFunction: callable or None = None