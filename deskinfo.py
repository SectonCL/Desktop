import os
import skia
from fileinput import close


"""DRAWINGQUEUE Explanation:
DrawingQueue is a dictionary that contains only 3 levels of draw access:
  0: Draw before everything
  1: Draw in Device
  2: Draw after everything

They're all equal to a list that contains instruction dictionaries:
Example of a DDQ file (Desktop Drawing Queue):
	Type: Text
	Position: [128, 128]
	Color: White
	Label: "Hello world!"
	Angle: 5.0
	Shadows: Yes
	Shadow Offset: [3, 3]
	Shadow Blur: 3.0
	Outline: Yes
	Outline Color: Black
	Outline Range: 1.0
	Priority: 2
DDQ lets you draw stuff without coding it.
Planned DDQ Rules:
	1. Every `Type` style splits the DDQ file, that means you can draw multiple things from one DDQ file
	2. Style names can be any case and with spaces. That means that `Draw This Thing` will translate to `drawthisthing`.
	3. Style name and value should be between `: `. That means you should always split them with colon and a space.
	4. Booleans can be either `True` `False` or `Yes` `No` 
	5. Colors, `Type` values, booleans must not be contained in quotes.
	6. Parser will ignore EVERY line that starts with `//`. That means you can write comments!
"""
drawingQueue = {
	0: [],
	1: [],
	2: []
}

debugMode = True; """Makes some calculations visualized"""
interval = []; """CPU Calculation time"""
clickOnce = False; """Activates special things once, like buttons"""
desktopIsDoing = False; """Desktop is very busy"""
prevMousePos = [0, 0]; """Mouse Position in a previous frame; useful for calculation of Mouse Velocity (it's already done, get_mousespeed().)"""
mousePos = [0, 0]
mouseEvents = [False, False, False]; """Current Mouse clicks in right order: Left, Middle (Scroll Button), Right"""
screenSize = [640, 480]
detailLevel = 2; """How detailed do we render screen, 0 is classic."""
useAnimations = True

availableApplications = []; """Everything from ./Programs"""
runningApplications = []; """The Applications that are currently running, those are Devices and even services."""
devices = []; """The Devices that were hidden in pockets, we need to remember them for variables"""
drawDeviceIndex = -1; """If index equals to -1, then don't render any device."""

def get_deltatime() -> float:
	if len(interval) == 2: return interval[1] - interval[0]

def get_mousespeed() -> list[int]:
	return [mousePos[0] - prevMousePos[0], mousePos[1] - prevMousePos[1]]

class Application:
	__type__: str = "service"
	name: str = "Unnamed"
	isBusy: bool = False # Give full control to Application when doing something
	needsExpert: bool = False # SUDO mode
	close: bool = False; """set to True when Application should not run anymore"""
	secretDevice: bool = False
	singular: bool = False; """Limit launching this Application to one process"""

	def __init__(self):
		print("Starting " + self.name)

	def shutdown(self):
		print("Closing " + self.name)
		self.close = True

class DeviceElement:
	__type__: str = "element"
	pos: list[int, int] = [0, 0]
	size: list[int, int] = [128,16]
	disabled = False; """Don't draw and give logic to this Element"""
	shadows: bool = True
	callFunction: callable or None = None