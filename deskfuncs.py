import deskinfo
import time

def colorNameToList(name: str, alpha: int = 255) -> list[int]:
	"""Available colors: black,white,red,green,blue"""
	match name:
		case "black": return [0,0,0,alpha]
		case "gray": return [100,100,100,alpha]
		case "white": return [255,255,255,alpha]
		case "red": return [255,0,0,alpha]
		case "green": return [0,255,0,alpha]
		case "blue": return [0,0,255,alpha]
		case _: print("colorNameToList, " + name + ": not in match case!"); return [0,0,0,alpha]

def in_box(check_x, check_y, area_x, area_y, area_width, area_height):
	"""Checks if the given position inside the provided area"""
	horizontal = False
	vertical   = False
	if deskinfo.debugMode:
		# Top-Left Corner
		queue_line([area_x, area_y], [area_x + 5, area_y], "red")
		queue_line([area_x, area_y], [area_x, area_y + 5], "red")
		# Top-Right Corner
		queue_line([area_x + area_width, area_y], [area_x + area_width - 5, area_y], "red")
		queue_line([area_x + area_width, area_y], [area_x + area_width, area_y - 5], "red")
		# Bottom-Left Corner
		queue_line([area_x, area_y + area_height], [area_x + 5, area_y + area_height], "red")
		queue_line([area_x, area_y + area_height], [area_x, area_y + area_height - 5], "red")
		# Bottom-Right Corner
		queue_line([area_x + area_width, area_y + area_height], [area_x + area_width - 5, area_y + area_height], "red")
		queue_line([area_x + area_width, area_y + area_height], [area_x + area_width, area_y + area_height - 5], "red")
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

def clamp(n, minn, maxn): """Limits the number"""; return max(min(maxn, n), minn)

def tween(start_value, end_value, duration):
	start_time = time.time()
	delta = end_value - start_value
	duration /= 1000

	def update():
		nonlocal start_value
		elapsed = time.time() - start_time
		if elapsed >= duration:
			return end_value
		t = elapsed / duration
		start_value = start_value + t * delta
		return start_value

	return update

def queue_draw(pos: list[int,int] = [0,0],
			   size: list[int,int] = [100,100],
			   color: str | list[int,int,int,int] | tuple[int,int,int,int] = (255,255,255,255), shadowed: bool = False,
			   border: str | list[int,int,int,int] | tuple[int,int,int,int] = (0,0,0,255), priority: int = 0):
	"""Draws a box inside an environment"""
	if shadowed: queue_shadow(pos + [4,4], size)
	if type(color) is str: resultColor = colorNameToList(color, 255)
	else: resultColor = color
	if type(color) is str: resultBorder = colorNameToList(color, 255)
	else: resultBorder = border

	deskinfo.drawingQueue[priority].append(f"dpg.draw_rectangle({pos}, {[pos[0] + size[0], pos[1] + size[1]]}, fill={resultColor}, color={resultBorder}, thickness=1.0)")

def queue_shadow(pos: list[int, int] = [0, 0],
				 size: list[int, int] = [100, 100],
				 smoothness: int = 4,
				 priority: int = 0):
	"""Draws a shadow inside an environment"""
	match deskinfo.detailLevel:
		case 0: deskinfo.drawingQueue[priority].append(f"dpg.draw_rectangle({pos}, {[pos[0] + size[0], pos[1] + size[1]]}, fill=(0,0,0,255))")
		case 1: deskinfo.drawingQueue[priority].append(f"dpg.draw_rectangle({pos}, {[pos[0] + size[0], pos[1] + size[1]]}, fill=(0,0,0,155))")
		case 2:
			for i in range(1, smoothness):
				deskinfo.drawingQueue[priority].append(f"dpg.draw_rectangle({[pos[0] - i, pos[1] - i]}, {[pos[0] + size[0] + i, pos[1] + size[1] + i]}, fill=(0,0,0,{int(255 / smoothness)}), color=(0,0,0,0), rounding={i}.0)")
			deskinfo.drawingQueue[priority].append(f"dpg.draw_rectangle({           pos          }, {[pos[0] + size[0]    , pos[1] + size[1]    ]}, fill=(0,0,0,50), color=(0,0,0,0))")

def queue_text(pos: list[int] = [0,0],
			   color: list[int,int,int,int] | tuple[int,int,int,int] = (255,255,255,255),
			   text: str = "Hello World",
			   shadowed: bool = False,
			   size: float = 16.0,
			   rotation: float = 0.0,
			   priority: int = 0):
	if type(color) is str: resultColor = colorNameToList(color, 255)
	else: resultColor = color
	processingCMD = f"dpg.draw_text({pos}, color={resultColor}, text='{text}', size={size}"
	# if rotation != 0.0: processingCMD += f", angle=-{rotation}"
	if shadowed:
		match deskinfo.detailLevel:
			case 0: deskinfo.drawingQueue[priority].append(f"dpg.draw_text([{pos[0] + 2}, {pos[1] + 2}], color=(0,0,0,255), text='{text}', size={size})")
			case 1: deskinfo.drawingQueue[priority].append(f"dpg.draw_text([{pos[0] + 2}, {pos[1] + 2}], color=(0,0,0,155), text='{text}', size={size})")
			case 2:
				deskinfo.drawingQueue[priority].append(f"dpg.draw_text({[pos[0] + 1, pos[1] + 1]}, text='{text}', color=(0,0,0,100), size={size})")
				deskinfo.drawingQueue[priority].append(f"dpg.draw_text({[pos[0] + 1, pos[1]    ]}, text='{text}', color=(0,0,0,20), size={size})")
				deskinfo.drawingQueue[priority].append(f"dpg.draw_text({[pos[0] + 2, pos[1]    ]}, text='{text}', color=(0,0,0,20), size={size})")
				deskinfo.drawingQueue[priority].append(f"dpg.draw_text({[pos[0] + 2, pos[1] + 1]}, text='{text}', color=(0,0,0,20), size={size})")
				deskinfo.drawingQueue[priority].append(f"dpg.draw_text({[pos[0] + 2, pos[1] + 2]}, text='{text}', color=(0,0,0,20), size={size})")
				deskinfo.drawingQueue[priority].append(f"dpg.draw_text({[pos[0] + 1, pos[1] + 2]}, text='{text}', color=(0,0,0,20), size={size})")
				deskinfo.drawingQueue[priority].append(f"dpg.draw_text({[pos[0]    , pos[1] + 2]}, text='{text}', color=(0,0,0,20), size={size})")
				deskinfo.drawingQueue[priority].append(f"dpg.draw_text({[pos[0]    , pos[1] + 1]}, text='{text}', color=(0,0,0,20), size={size})")
	deskinfo.drawingQueue[priority].append(processingCMD + ")")

def queue_line(begin: list[int], end: list[int], color: list[int,int,int,int] | tuple[int,int,int,int] = (255,255,255,255),
			   shadowed: bool = False, priority: int = 0):
	"""Draws a line inside an environment. The end position is not relative"""
	if type(color) is str: resultColor = colorNameToList(color, 255)
	else: resultColor = color
	if shadowed: deskinfo.drawingQueue[priority].append(f"dpg.draw_line({begin}, {end}, color=(0,0,0,255))")
	deskinfo.drawingQueue[priority].append(f"dpg.draw_line({begin}, {end}, color={resultColor})")

def queue_msg(text: str):
	"""Creates a message that follows a cursor."""

def guide_hint(pos: list[int], size: list[int], time: int):
	"""**NOT DONE YET!**
	Guides a colleague to a certain area. **This will not work when there's another hint**, so use responsibly"""
	pass