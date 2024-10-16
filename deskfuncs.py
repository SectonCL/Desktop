import skia

import deskinfo
import time

def colorNameToList(name: str, alpha: int = 255) -> list[int]:
	"""Available colors: black,white,red,green,blue"""
	match name:
		case "black": return [ 0 , 0 , 0 ,alpha]
		case "gray" : return [100,100,100,alpha]
		case "white": return [255,255,255,alpha]
		case "red"  : return [255, 0 , 0 ,alpha]
		case "green": return [ 0 ,255, 0 ,alpha]
		case "blue" : return [ 0 , 0 ,255,alpha]
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
		queue_line([area_x + area_width, area_y], [area_x + area_width, area_y - 5], "red", priority=2)
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

def tween(start_value, end_value, duration):
	start_time = time.time()
	delta = end_value - start_value
	duration /= 1000

	def update( *ignoreArgs ):
		nonlocal start_value
		elapsed = time.time() - start_time
		if elapsed >= duration: return end_value
		t = elapsed / duration
		start_value = start_value + t * delta
		return start_value

	return update

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

def queue_msg(message: str):
	"""Creates a message that follows a cursor."""
	queue_draw([deskinfo.mousePos[0] + 8 , deskinfo.mousePos[1] +  8], [calcTextSize(len(message)), 20], [255, 248, 156, 255], True, priority=2)
	queue_text([deskinfo.mousePos[0] + 10, deskinfo.mousePos[1] + 10], "black", message, priority=2)

def alert(title: str, message: str):
	"""**NOT DONE YET!**
	Sends a notification with title and message. Stays infinitely until the colleague closes it."""
	pass

def guide_hint(pos: list[int], size: list[int], time: int):
	"""**NOT DONE YET!**
	Guides the colleague to a certain area. **This will not work when there's another hint**, so use responsibly"""
	pass