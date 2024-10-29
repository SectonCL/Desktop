import skia
import time

import deskinfo

def colorNameToList(name: str, alpha: int = 255) -> list[int]:
	"""Available colors: black,white,red,green,blue"""
	match name:
		case "black" : return [ 0 , 0 , 0 ,alpha]
		case "gray"  : return [100,100,100,alpha]
		case "white" : return [255,255,255,alpha]
		case "red"   : return [255, 0 , 0 ,alpha]
		case "green" : return [ 0 ,255, 0 ,alpha]
		case "blue"  : return [ 0 , 0 ,255,alpha]
		case "cyan"  : return [ 0 ,255,255,alpha]
		case "yellow": return [255,255, 0 ,alpha]
		case "orange": return [255,150, 0 ,alpha]
		case "purple": return [150, 0 ,255,alpha]
		case "pink"  : return [255,150,150,alpha]
		# Custom palette goes now...
		case "energeticblue": return [ 0 , 76,255,alpha]
		case "moderngreen"  : return [ 0 ,255, 90,alpha]
		case "lambdaorange" : return [243,123, 33,alpha]
		case "basketball"   : return [252, 90, 3 ,alpha]
		case "cuteypink"    : return [255,150,178,alpha]
		case _: print("colorNameToList, " + name + ": not in match case!"); return [0,0,0,alpha]

def in_box(check_x, check_y, area_x, area_y, area_width, area_height):
	"""Checks if the given position inside the provided area"""
	horizontal = False
	vertical   = False
	if deskinfo.debugMode:
		# Top-Left Corner
		queue_line([area_x, area_y], [area_x + 5, area_y], "red", priority=2)
		queue_line([area_x, area_y], [area_x, area_y + 5], "red", priority=2)
		# Top-Right Corner
		queue_line([area_x + area_width, area_y], [area_x + area_width - 5, area_y], "red", priority=2)
		queue_line([area_x + area_width, area_y], [area_x + area_width, area_y + 5], "red", priority=2)
		# Bottom-Left Corner
		queue_line([area_x, area_y + area_height], [area_x + 5, area_y + area_height], "red", priority=2)
		queue_line([area_x, area_y + area_height], [area_x, area_y + area_height - 5], "red", priority=2)
		# Bottom-Right Corner
		queue_line([area_x + area_width, area_y + area_height], [area_x + area_width - 5, area_y + area_height], "red", priority=2)
		queue_line([area_x + area_width, area_y + area_height], [area_x + area_width, area_y + area_height - 5], "red", priority=2)
	if area_y + area_height > check_y > area_y: vertical   = True
	if area_x + area_width  > check_x > area_x: horizontal = True
	return horizontal and vertical

def out_of_screen_BOX(box_x, box_y, box_width, box_height) -> bool:
	"""Checks if the given box is colliding outside of screen.
	Examples:
		________
		|      |  Does not collide
		|  ██  |
		|______|

	------------------------------
		________
		|      |  Does collide
		|     ███
		|______|
	"""
	horizontal = False
	vertical   = False
	if box_x + box_width  > deskinfo.screenSize[0] or box_x < 0: horizontal = True
	if box_y + box_height > deskinfo.screenSize[1] or box_y < 0: vertical   = True
	return horizontal and vertical

def calcTextSize(textLength: int) -> int:
	return textLength * 8 + 8;

def clamp(n, minn, maxn): """Limits the number"""; return max(min(maxn, n), minn)

class Tween():
	"""Advanced smoothing system. Provides `changeEndValue` and `update` functions to make dynamic animations."""
	startValue = 0.0; endValue = 1.0; duration = 1.0
	startTime = time.time()
	delta = endValue - startValue
	curValue = None

	def __init__(self, startValue, endValue, duration):
		self.startValue = startValue
		self.endValue = endValue
		self.duration = duration
		self.delta = endValue - startValue

	def changeEndValue(self, newEndValue):
		"""Changes the end value and resets the timer."""
		if newEndValue == self.endValue: return
		self.endValue = newEndValue
		self.delta = newEndValue - self.startValue
		self.startTime = time.time()
		self.startValue = self.curValue

	def update(self, *ignoreArgs ):
		"""Updates and returns current value."""
		elapsed = time.time() - self.startTime
		if elapsed >= self.duration:
			self.startValue = self.endValue
			return self.endValue
		t = elapsed / self.duration
		self.curValue = self.startValue + t * self.delta
		return self.startValue + t * self.delta

def queue_draw(pos   : list[int,int] | list[float,float] = [ 0 , 0 ],
			   size  : list[int,int] | list[float,float] = [100,100],
			   color : str | list[int,int,int,int] | tuple[int,int,int,int] | str = (255,255,255,255), shadowed: bool = False,
			   border: str | list[int,int,int,int] | tuple[int,int,int,int] | str = ( 0 , 0 , 0 ,255), priority:  int = 1):
	"""Draws a box inside an environment"""
	if type(color) is str: resultColor = colorNameToList(color, 255)
	else: resultColor = color
	if type(border) is str: resultBorder = colorNameToList(color, 255)
	else: resultBorder = border

	deskinfo.drawingQueue[priority].append([0, pos, size, resultColor, shadowed, resultBorder])

def queue_text(pos: list[int] = [0,0],
			   color: list[int,int,int,int] | tuple[int,int,int,int] | str = (255,255,255,255),
			   text: str = "Hello World!",
			   shadowed: bool = False,
			   size: int = 16,
			   rotation: float = 0.0,
			   priority: int = 1):
	if type(color) is str: resultColor = colorNameToList(color, 255)
	else: resultColor = color

	deskinfo.drawingQueue[priority].append([1, pos, text, resultColor, shadowed, size])

def queue_line(begin: list[int], end: list[int], color: list[int,int,int,int] | tuple[int,int,int,int] | str = (255,255,255,255),
			   shadowed: bool = False, priority: int = 1):
	"""Draws a line inside an environment. The end position is not relative"""
	if type(color) is str: resultColor = colorNameToList(color, 255)
	else: resultColor = color
	deskinfo.drawingQueue[priority].append([2, begin, end, resultColor, shadowed])

def queue_msg(message: str, position: list[int, int] | None = None):
	"""Creates a message that follows a cursor."""
	if position != None:
		queue_draw([position[0], position[1]], [calcTextSize(len(message)), 20], [255, 248, 156, 255], True, priority=2)
		queue_text([position[0], position[1]], "black", message, priority=2)
	else:
		queue_draw([deskinfo.mousePos[0] + 24, deskinfo.mousePos[1] + 24], [calcTextSize(len(message)), 20], [255, 248, 156, 255], True, priority=2)
		queue_text([deskinfo.mousePos[0] + 24, deskinfo.mousePos[1] + 24], "black", message, priority=2)

def alert(title: str, message: str):
	"""**NOT DONE YET!**
	Sends a notification with title and message. Stays infinitely until the colleague closes it."""
	pass

def guide_hint(pos: list[int], size: list[int], time: int):
	"""**NOT DONE YET!**
	Guides the colleague to a certain area. **This will not work when there's another hint**, so use responsibly"""
	pass