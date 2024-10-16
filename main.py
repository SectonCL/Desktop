import time
import os
import sys
import playsound

import skia
import contextlib
import glfw
import skia
from OpenGL import GL

import deskinterface
import deskinfo
import deskfuncs

isMenuOpened = False
# bgImage = tkinter.PhotoImage(file="./Assets/bg.png")

for file in os.listdir("./Programs"):
	if os.path.isfile("./Programs/" + file):
		# why
		exec(f"import Programs.{file.removesuffix(".py")}\ndeskinfo.availableApplications.append(Programs.{file.removesuffix('.py')}.Program)")


@contextlib.contextmanager
def glfw_window():
	if not glfw.init(): raise RuntimeError('GLFW Initialization has completely failed. Too bad!')
	glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
	glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
	if os.environ["XDG_SESSION_TYPE"] == "wayland" and sys.argv[0].lower() != "force_wayland": exit("Skia does not support Wayland.")
	glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
	glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
	glfw.window_hint(glfw.STENCIL_BITS, 8)
	glfw.window_hint(glfw.DEPTH_BITS, 8)
	# glfw.window_hint(glfw.DECORATED, False)
	origSize = glfw.get_video_mode(glfw.get_primary_monitor())[0]
	if sys.argv[-1].lower() == "os_mode":
		print("Goin' full screen!")
		window = glfw.create_window(deskinfo.screenSize[0], deskinfo.screenSize[1], 'SCLDesktop', glfw.get_primary_monitor(), None)
	else:
		window = glfw.create_window(deskinfo.screenSize[0], deskinfo.screenSize[1], 'SCLDesktop', None, None)
	glfw.make_context_current(window)
	yield window
	glfw.terminate()
	if sys.argv[-1].lower() == "os_mode":
		os.system(f"xrandr --size {origSize[0]}x{origSize[1]}")

@contextlib.contextmanager
def skia_surface():
	surf: skia.Surface
	context = skia.GrContext.MakeGL()
	backend_render_target = skia.GrBackendRenderTarget(
		deskinfo.screenSize[0],
		deskinfo.screenSize[1],
		0,  # sampleCnt
		0,  # stencilBits
		skia.GrGLFramebufferInfo(0, GL.GL_RGB8))
	surf = skia.Surface.MakeFromBackendRenderTarget(
		context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
		skia.kRGB_888x_ColorType, skia.ColorSpace.MakeSRGB())
	if surf is None: exit("Failed to initialize. Too bad!")
	yield surf
	context.abandonContext()


if os.name == "posix":
	monospaceFont = skia.Font(skia.Typeface('Classic Console'), 24)
	standardFont = skia.Font(skia.Typeface('Bahnschrift'), 24)

class Desktop(deskinfo.Application):
	name = "Environment"
	curDecoMenuPos = 0

	def toggleMenu(self):
		global isMenuOpened
		if isMenuOpened: isMenuOpened = False
		else           : isMenuOpened = True

	class ActionsButton(deskinterface.EnhancedElements.OptionButton):
		options = ["Shut Down", "Re boot", "Hibernate", "Close Device", "Hide to Pockets"]
		pos = [deskinfo.screenSize[0] - 48, deskinfo.screenSize[1] - 32]
		shadows = False
		size = [48, 16]
		label = "ACTS"

		def logic(self):
			super().logic()
			self.pos = [deskinfo.screenSize[0] - 48, deskinfo.screenSize[1] - 32]

		def option_clicked(self, index: int):
			super().option_clicked(index)
			match index:
				case 0: glfw.set_window_should_close(window, glfw.TRUE)
				case 1: pass
				case 2: pass
				case 3:
					if deskinfo.drawDeviceIndex != -1:
						deskinfo.devices[deskinfo.drawDeviceIndex].shutdown()
						deskinfo.devices.pop(deskinfo.drawDeviceIndex)
						deskinfo.drawDeviceIndex = -1
					else: print("Desktop ActionsButton, option_clicked 'CLOSE': Nothing to close!")
				case 4: deskinfo.drawDeviceIndex = -1

	class Pockets(deskinterface.Elements.Book):
		pages = []
		pos = [100, deskinfo.screenSize[1] - 32]
		size = [deskinfo.screenSize[0] - pos[0] - 48, 32]

		def logic(self):
			super().logic()
			self.pages.clear()
			self.currentPage = deskinfo.drawDeviceIndex
			self. pos[1] = deskinfo.screenSize[1] - 32
			self.size[0] = deskinfo.screenSize[0] - self.pos[0] - 48
			for device in deskinfo.devices:
				self.pages.append(device.devtitle)

		def pageSwitched(self, index):
			super().pageSwitched(index)
			if index == deskinfo.drawDeviceIndex: deskinfo.drawDeviceIndex = -1
			else: deskinfo.drawDeviceIndex = index

	class PopUPMenu(deskinterface.Elements.List):
		items = []
		size = [200, deskinfo.screenSize[1] - 32]

		def __init__(self):
			super().__init__()
			for app in deskinfo.availableApplications: self.items.append(app)

		def itemClicked(self, index: int):
			global isMenuOpened
			super().itemClicked(index)
			if self.items[index].__type__ == "device":
				deskinfo.devices.append(self.items[index]())
				deskinfo.drawDeviceIndex = len(deskinfo.devices) - 1
			else: deskinfo.runningApplications.append(self.items[index]())
			isMenuOpened = False

		def logic(self):
			# super().logic() # override standard logic
			# With this:
			self.size[1] = deskinfo.screenSize[1] - 32
			deskfuncs.queue_draw([self.pos[0], self.pos[1]], [self.size[0], self.size[1]], "white", True)
			for idx, item in enumerate(self.items):
				if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1] + idx * 18, self.size[0], 18):
					deskfuncs.queue_draw([self.pos[0], self.pos[1] + idx * 18], [self.size[0], 18], (0, 178, 255, 125), True)
					if deskinfo.clickOnce: self.itemClicked(idx)
				deskfuncs.queue_text([self.pos[0] + 2, self.pos[1] + idx * 18], "black", item.name, False)

	popmenu2 = PopUPMenu()  # why do i have to do it like this...
	actbut2 = ActionsButton()
	pock2 = Pockets()
	yPosTween1 = None

	def logic(self):
		deskinfo.drawingQueue[0].clear()
		deskinfo.drawingQueue[1].clear()
		deskinfo.drawingQueue[2].clear()
		global window

		if glfw.get_cursor_pos(window) >= (0.0, 0.0): deskinfo.mousePos = glfw.get_cursor_pos(window)
		if len(deskinfo.interval) != 0: deskinfo.interval[0] = time.time()
		else: deskinfo.interval.append(time.time())
		if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], 0, deskinfo.screenSize[1] - 32, 98, 32):
			self.yPosTween1 = deskfuncs.tween(self.curDecoMenuPos, 16.0, 0.25)
			deskfuncs.queue_draw([8, deskinfo.screenSize[1] - 6], [84, 1], color="black")
			if deskinfo.clickOnce: self.toggleMenu()
		else: self.yPosTween1 = deskfuncs.tween(self.curDecoMenuPos, 0.0, 0.25)

		# Give thinking to opened applications
		for service in deskinfo.runningApplications:
			service.think()
			if service.close: service.shutdown(); deskinfo.runningApplications.remove(service)
		if deskinfo.drawDeviceIndex != -1: deskinfo.devices[deskinfo.drawDeviceIndex].think()

		self.Pockets.logic(self.pock2)
		if isMenuOpened:
			self.yPosTween1 = deskfuncs.tween(self.curDecoMenuPos, 32.0, 0.5)
			if not deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], 0, deskinfo.screenSize[1] - 32, 98, 32):
				deskfuncs.queue_draw([8, deskinfo.screenSize[1] - 22], [84, 1], color="black")
			deskfuncs.queue_text([8, deskinfo.screenSize[1] + 12 - self.curDecoMenuPos], text="CLOSE", color="black")
			self.PopUPMenu.logic(self.popmenu2)
		else:
			deskfuncs.queue_text([8, deskinfo.screenSize[1] - 12 - self.curDecoMenuPos], text="PROGRAMS", color="black")
			deskfuncs.queue_text([4, deskinfo.screenSize[1] - 14 - self.curDecoMenuPos], text="PROGRAMS")
		self.ActionsButton.logic(self.actbut2)
		if deskinfo.mouseEvents[0] and deskinfo.clickOnce: deskinfo.clickOnce = False  # Make sure that clickOnce actually clicksOnce

		deskfuncs.queue_draw([0, deskinfo.screenSize[0] - self.curDecoMenuPos], [100, deskinfo.screenSize[1]], "white")

		if self.yPosTween1 is not None: self.curDecoMenuPos = self.yPosTween1()

		deskinfo.prevMousePos = deskinfo.mousePos


desk = Desktop()


def redraw(surfaceRef):
	surfaceRef = surfaceRef.getCanvas()
	# if deskinfo.surfaceRef is not None: surfaceRef = deskinfo.surfaceRef
	# else: print("No surfaceRef here!"); exit(404)
	surfaceRef.clear(skia.ColorBLACK)
	def drawInstructions(instructionSet: list):
		for instruction in instructionSet:
			match instruction[0]:
				case 0:
					skiaColor = skia.Color(instruction[3][0], instruction[3][1], instruction[3][2], instruction[3][3])
					painter = skia.Paint(Color=skiaColor)
					if instruction[4]:
						match deskinfo.detailLevel:
							case 0: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 0.0, 0.0, skia.ColorBLACK))
							case 1: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 0.0, 0.0, skia.Color(0, 0, 0, 155)))
							case 2: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 3.0, 3.0, skia.ColorBLACK))
							case _: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 0.0, 0.0, skia.ColorBLACK))
					surfaceRef.drawRect(skia.Rect.MakeXYWH(float(instruction[1][0]), float(instruction[1][1]), float(instruction[2][0]), float(instruction[2][1])), painter)
				case 1:
					# if rotation != 0.0: processingCMD += f", angle=-{rotation}"
					painter: skia.Paint = skia.Paint()
					if instruction[4]:
						match deskinfo.detailLevel:
							case 0: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 0.0, 0.0, skia.ColorBLACK))
							case 1: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 0.0, 0.0, skia.Color(0, 0, 0, 155)))
							case 2: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 3.0, 3.0, skia.ColorBLACK))
							case _: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 0.0, 0.0, skia.ColorBLACK))
					painter.setColor(skia.Color(instruction[3][0], instruction[3][1], instruction[3][2], instruction[3][3]))
					painter.setAntiAlias(False)
					surfaceRef.drawString(instruction[2], instruction[1][0], instruction[1][1] + instruction[5], monospaceFont, painter)
				case 2:
					painter: skia.Paint = skia.Paint()
					line = skia.Path()
					line.moveTo(instruction[1][0], instruction[1][1])
					line.lineTo(instruction[2][0], instruction[2][1])

					if instruction[4]:
						match deskinfo.detailLevel:
							case 0: painter.setImageFilter(skia.ImageFilters.DropShadow(line, 3.0, 3.0, 0.0, 0.0, skia.ColorBLACK))
							case 1: painter.setImageFilter(skia.ImageFilters.DropShadow(line, 3.0, 3.0, 0.0, 0.0, skia.Color(0, 0, 0, 155)))
							case 2: painter.setImageFilter(skia.ImageFilters.DropShadow(line, 3.0, 3.0, 5.0, 5.0, skia.ColorBLACK))

					surfaceRef.drawPath(line, painter)
	# </drawInstructions>

	# BG
	image = skia.Image.open("./Assets/bg.png")
	surfaceRef.drawImage(image, 0.0, 0.0)

	# Before EVERYTHING
	drawInstructions(deskinfo.drawingQueue[0])

	curPaint = skia.Paint(Color=skia.ColorWHITE)
	curText = skia.TextBlob("SCLDesktop v0.5 Beta", monospaceFont)
	surfaceRef.drawTextBlob(curText, 8, 24, curPaint)

	curPaint.setColor(skia.ColorBLACK)
	curText = skia.TextBlob(time.strftime("%H:%M"), monospaceFont)
	surfaceRef.drawTextBlob(curText, deskinfo.screenSize[0] - 46, deskinfo.screenSize[1] - 14, curPaint)

	curPaint.setColor(skia.ColorWHITE)
	curText = skia.TextBlob(time.strftime("%H:%M"), monospaceFont)
	surfaceRef.drawTextBlob(curText, deskinfo.screenSize[0] - 48, deskinfo.screenSize[1] - 16, curPaint)


	# On Devices
	drawInstructions(deskinfo.drawingQueue[1])

	# Cursor (ALWAYS THE LAST!)
	if deskinfo.detailLevel > 1:
		curBlur = skia.Path()
		painter = skia.Paint(AntiAlias=True)
		# dpg.draw_line([deskinfo.mousePos[0] - deskinfo.get_mousespeed()[0],
		# 			   deskinfo.mousePos[1] - deskinfo.get_mousespeed()[1]],
		# 			  [deskinfo.mousePos[0],  deskinfo.mousePos[1]],
		# 			  color=(0, 0, 0, 255), thickness=4.0)
		painter.setStrokeWidth(4.0)
		painter.setColor(skia.ColorBLACK)
		curBlur.moveTo(deskinfo.mousePos[0] - deskinfo.get_mousespeed()[0], deskinfo.mousePos[1] - deskinfo.get_mousespeed()[1])
		curBlur.lineTo(deskinfo.mousePos[0], deskinfo.mousePos[1])
		surfaceRef.drawPath(curBlur, painter)
		# dpg.draw_line([deskinfo.mousePos[0] - deskinfo.get_mousespeed()[0],
		# 			   deskinfo.mousePos[1] - deskinfo.get_mousespeed()[1]],
		# 			  [deskinfo.mousePos[0], deskinfo.mousePos[1]],
		# 			  color=(255, 255, 255, 255), thickness=2.0)
		painter.setStrokeWidth(2.0)
		painter.setColor(skia.ColorWHITE)
		curBlur.moveTo(deskinfo.mousePos[0] - deskinfo.get_mousespeed()[0], deskinfo.mousePos[1] - deskinfo.get_mousespeed()[1])
		curBlur.lineTo(deskinfo.mousePos[0], deskinfo.mousePos[1])
		surfaceRef.drawPath(curBlur, painter)
	# dpg.draw_rectangle([deskinfo.mousePos[0] - 2, deskinfo.mousePos[1] - 2],
	# 				   [deskinfo.mousePos[0] + 2, deskinfo.mousePos[1] + 2], color=(0, 0, 0, 255),
	# 				   fill=(255, 255, 255, 255), thickness=1.0)
	deskfuncs.queue_draw([deskinfo.mousePos[0] - 2, deskinfo.mousePos[1] - 2], [4, 4], "white", priority=2)
	curPainter = skia.Paint()
	curPainter.setStyle(skia.Paint.kStroke_Style)
	curPainter.setStrokeWidth(2)
	surfaceRef.drawRect(skia.Rect.MakeXYWH(deskinfo.mousePos[0] - 2, deskinfo.mousePos[1] - 2, 4, 4), curPainter)


	# After EVERYTHING
	drawInstructions(deskinfo.drawingQueue[2])

	if len(deskinfo.interval) == 2: deskinfo.interval[1]  =  time.time()
	else                          : deskinfo.interval.append(time.time())


def mouseRegister(mouseWindow, mouseButton, mouseAction, something):
	if mouseAction == glfw.PRESS:
		match mouseButton:
			case glfw.MOUSE_BUTTON_LEFT  : deskinfo.mouseEvents[0] = True; deskinfo.clickOnce = True
			case glfw.MOUSE_BUTTON_MIDDLE: deskinfo.mouseEvents[1] = True
			case glfw.MOUSE_BUTTON_RIGHT : deskinfo.mouseEvents[2] = True
	else:
		match mouseButton:
			case glfw.MOUSE_BUTTON_LEFT  : deskinfo.mouseEvents[0] = False
			case glfw.MOUSE_BUTTON_MIDDLE: deskinfo.mouseEvents[1] = False
			case glfw.MOUSE_BUTTON_RIGHT : deskinfo.mouseEvents[2] = False

def sizeRegister(sizeWindow, sizeWidth, sizeHeight):
	global reRun
	deskinfo.screenSize = [sizeWidth, sizeHeight]
	reRun = True # Could have used GOTO but there is none in Python3. Too bad!

reRun = False
with glfw_window() as window:
	# playsound.playsound("./Assets/startup.ogg", False)
	def main():
		global reRun
		global desk
		# GL.glClear(GL.GL_COLOR_BUFFER_BIT)
		with skia_surface() as surface:
			glfw.set_mouse_button_callback(window, mouseRegister)
			glfw.set_window_size_callback(window, sizeRegister)
			glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_HIDDEN)
			while not glfw.window_should_close(window) and not reRun:
				glfw.poll_events()
				desk.logic()
				redraw(surface)
				surface.flushAndSubmit()
				glfw.swap_buffers(window)

	while True: # Dumb but somewhat usable without GOTO.
		reRun = False
		main()
		if glfw.window_should_close(window): break
		print("RERUNNING! This might break some stuff.")