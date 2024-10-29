# Save processing time by putting this into the very beginning
import os
if os.environ["XDG_SESSION_TYPE"] == "wayland": exit("Skia cannot create GL context in Wayland!\n"
													 "We suggest you launch this through Xwayland or start your compositor in X11 mode.\n"
													 "Please contact the Skia devs for the Wayland support of Skia. We can't do anything about this, really.")
import time
import sys
import mpv

import skia
import contextlib
import glfw
import skia
from OpenGL import GL

import deskinterface
import deskinfo
import deskfuncs

isMenuOpened = False

for file in os.listdir("./Programs"):
	if os.path.isfile("./Programs/" + file):
		# why
		exec(f"import Programs.{file.removesuffix(".py")}\ndeskinfo.availableApplications.append(Programs.{file.removesuffix('.py')}.Program)")


@contextlib.contextmanager
def glfw_window():
	if not glfw.init(): raise RuntimeError('GLFW Initialization has completely failed. Too bad!')
	glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
	glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
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
	standardFont = skia.Font(skia.Typeface(), 16)

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
			deskfuncs.queue_draw([self.pos[0], self.pos[1]], [self.size[0], self.size[1]], "white", True, priority=2)
			for idx, item in enumerate(self.items):
				if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1] + idx * 20, self.size[0], 18):
					deskfuncs.queue_draw([self.pos[0], self.pos[1] + idx * 20], [self.size[0], 20], (0, 178, 255, 125), True, priority=2)
					if deskinfo.clickOnce: self.itemClicked(idx)
				deskfuncs.queue_text([self.pos[0] + 2, self.pos[1] + idx * 20], "black", item.name, False, priority=2)

	popmenu2 = PopUPMenu()  # why do i have to do it like this...
	actbut2 = ActionsButton()
	pock2 = Pockets()
	yPosTween1 = deskfuncs.Tween(curDecoMenuPos, 0.0, 0.5)

	def logic(self):
		deskinfo.drawingQueue[0].clear()
		deskinfo.drawingQueue[1].clear()
		deskinfo.drawingQueue[2].clear()
		global window
		touchingButton = deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], 0, deskinfo.screenSize[1] - 32, 98, 32)

		if glfw.get_cursor_pos(window) >= (0.0, 0.0): deskinfo.mousePos = glfw.get_cursor_pos(window)
		if len(deskinfo.interval) != 0: deskinfo.interval[0] = time.time()
		else: deskinfo.interval.append(time.time())

		# Give thinking to opened applications
		for service in deskinfo.runningApplications:
			service.think()
			if service.close: service.shutdown(); deskinfo.runningApplications.remove(service)
		if deskinfo.drawDeviceIndex != -1: deskinfo.devices[deskinfo.drawDeviceIndex].think()

		self.Pockets.logic(self.pock2)
		if isMenuOpened:
			self.yPosTween1.changeEndValue(32.0)
			if not touchingButton:
				self.yPosTween1.changeEndValue(24.0)
			self.PopUPMenu.logic(self.popmenu2)
		else:
			if touchingButton:
				self.yPosTween1.changeEndValue(8.0)
			else:
				self.yPosTween1.changeEndValue(0.0)

		if deskinfo.clickOnce and touchingButton: self.toggleMenu()
		deskfuncs.queue_text([8, deskinfo.screenSize[1] + 4 - self.curDecoMenuPos], text="CLOSE", shadowed=True)
		deskfuncs.queue_text([4, deskinfo.screenSize[1] - 22 - self.curDecoMenuPos], text="PROGRAMS", shadowed=True)
		self.ActionsButton.logic(self.actbut2)
		if deskinfo.mouseEvents[0] and deskinfo.clickOnce: deskinfo.clickOnce = False  # Make sure that clickOnce actually clicksOnce

		self.curDecoMenuPos = self.yPosTween1.update()

		deskinfo.prevMousePos = deskinfo.mousePos


desk = Desktop()


bgImage = skia.Image.open("./Assets/bg.png")
cursor = skia.Image.open("./Assets/cursor.png")
def redraw(surfaceRef):
	global bgImage
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
							case _: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 3.0, 3.0, skia.ColorBLACK))
					surfaceRef.drawRect(skia.Rect.MakeXYWH(float(instruction[1][0]), float(instruction[1][1]), float(instruction[2][0]), float(instruction[2][1])), painter)
				case 1:
					# if rotation != 0.0: processingCMD += f", angle=-{rotation}"
					painter: skia.Paint = skia.Paint()
					if instruction[4]:
						match deskinfo.detailLevel:
							case 0: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 0.0, 0.0, skia.ColorBLACK))
							case _: painter.setImageFilter(skia.ImageFilters.DropShadow(3.0, 3.0, 3.0, 3.0, skia.ColorBLACK))
					painter.setColor(skia.Color(instruction[3][0], instruction[3][1], instruction[3][2], instruction[3][3]))
					surfaceRef.drawString(instruction[2], instruction[1][0], instruction[1][1] + instruction[5], standardFont, painter)
				case 2:
					painter: skia.Paint = skia.Paint(Color=skia.Color(instruction[3][0], instruction[3][1], instruction[3][2], instruction[3][3]))
					if instruction[4]:
						match deskinfo.detailLevel:
							case 0: painter.setImageFilter(skia.ImageFilters.DropShadow(line, 3.0, 3.0, 0.0, 0.0, skia.ColorBLACK))
							case _: painter.setImageFilter(skia.ImageFilters.DropShadow(line, 3.0, 3.0, 5.0, 5.0, skia.ColorBLACK))
					surfaceRef.drawLine(instruction[1][0], instruction[1][1], instruction[2][0], instruction[2][1], painter)
	# </drawInstructions>

	# BG
	if [bgImage.width(), bgImage.height()] == deskinfo.screenSize:
		bgRect = skia.Rect(0, 0, deskinfo.screenSize[0], deskinfo.screenSize[1])
	else:
		bgRect = skia.Rect(deskinfo.screenSize[0] / 2 - bgImage.width() / 2,
						   deskinfo.screenSize[1] / 2 - bgImage.height() / 2,
						   deskinfo.screenSize[0] / 2 + bgImage.width()  / 2,
						   deskinfo.screenSize[1] / 2 + bgImage.height() / 2)
	if deskinfo.detailLevel <= 0: modBG = bgImage.convert(skia.ColorType.kRGB_888x_ColorType, skia.AlphaType.kOpaque_AlphaType)
	else: modBG = bgImage
	surfaceRef.drawImageRect(modBG, dst=bgRect)

	# Before EVERYTHING
	drawInstructions(deskinfo.drawingQueue[0])

	curPaint = skia.Paint(Color=skia.ColorWHITE)
	curText = skia.TextBlob(f"SCLDesktop {deskinfo.version} {deskinfo.edition}", standardFont)
	surfaceRef.drawTextBlob(curText, deskinfo.screenSize[0] - curText.bounds().width() - 16, deskinfo.screenSize[1] - 48, curPaint)

	curPaint.setColor(skia.ColorWHITE)
	curText = skia.TextBlob(time.strftime("%H:%M"), standardFont)
	surfaceRef.drawTextBlob(curText, deskinfo.screenSize[0] - 8, deskinfo.screenSize[1] - 16, curPaint)


	# On Devices
	drawInstructions(deskinfo.drawingQueue[1])

	# After EVERYTHING
	drawInstructions(deskinfo.drawingQueue[2])

	# Cursor (ALWAYS THE LAST!)
	surfaceRef.drawImageRect(cursor, dst=skia.Rect.MakeXYWH(deskinfo.mousePos[0], deskinfo.mousePos[1], 24, 31))


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
	# mpv.MPV().play("./Assets/Startup.ogg")
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