import time
import deskfuncs
import dearpygui.dearpygui as dpg
import os
from sys import argv
import deskinterface
import deskinfo

dpg.create_context()
dpg.create_viewport(title="SCLDestkop", width=deskinfo.screenSize[0], height=deskinfo.screenSize[1], resizable=False, clear_color=(0,0,255,255), vsync=True)
canvas = None

isMenuOpened = False
# bgImage = tkinter.PhotoImage(file="./Assets/bg.png")

for file in os.listdir("./Programs"):
	if os.path.isfile("./Programs/" + file):
		exec("import Programs." + file.removesuffix(".py") + "\n"
															 f"deskinfo.availableApplications.append(Programs.{file.removesuffix('.py')}.Program)")

if argv[0].lower() == "os_mode":
	dpg.toggle_viewport_fullscreen()

if os.name == "posix":
	with dpg.font_registry():
		monospaceFont = dpg.add_font("/usr/share/fonts/xscreensaver/clacon.ttf", 16)

class Desktop(deskinfo.Application):
	name = "Environment"
	curDecoMenuPos = 0

	def toggleMenu(self):
		global isMenuOpened
		if    isMenuOpened: isMenuOpened = False
		else: isMenuOpened = True

	class ActionsButton(deskinterface.EnhancedElements.OptionButton):
		options = ["Shut Down", "Re boot", "Hibernate", "Close Device", "Hide to Pockets"]
		pos = [deskinfo.screenSize[0] - 48, deskinfo.screenSize[1] - 32]
		shadows = False
		size = [48, 16]
		label = "ACTS"

		def option_clicked(self, index: int):
			super().option_clicked(index)
			match index:
				case 0: dpg.stop_dearpygui()
				case 1: pass
				case 2: pass
				case 3:
					if deskinfo.drawDeviceIndex != -1:
						deskinfo.devices[deskinfo.drawDeviceIndex].shutdown()
						deskinfo.devices.pop(deskinfo.drawDeviceIndex)
						deskinfo.drawDeviceIndex = -1
					else:
						print("Desktop ActionsButton, option_clicked 'CLOSE': Nothing to close!")
				case 4: deskinfo.drawDeviceIndex = -1

	class Pockets(deskinterface.Elements.Book):
		pages = []
		pos = [100, deskinfo.screenSize[1] - 32]
		size = [deskinfo.screenSize[0] - pos[0] - 48, 32]

		def logic(self):
			super().logic()
			self.pages.clear()
			self.currentPage = deskinfo.drawDeviceIndex
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
			for app in deskinfo.availableApplications:
				self.items.append(app)

		def itemClicked(self, index: int):
			global isMenuOpened
			super().itemClicked(index)
			if self.items[index].__type__ == "device":
				deskinfo.devices.append(self.items[index]())
				deskinfo.drawDeviceIndex = len(deskinfo.devices) - 1
			else:
				deskinfo.runningApplications.append(self.items[index]())
			isMenuOpened = False

		def logic(self):
			# super().logic() # override standard logic
			# With this:
			deskfuncs.queue_shadow([self.pos[0] + 4, self.pos[1] + 4], [self.size[0], self.size[1]])
			deskfuncs.queue_draw([self.pos[0], self.pos[1]], [self.size[0], self.size[1]], "white")
			for idx,item in enumerate(self.items):
				if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1] + idx * 16, self.size[0], 16):
					deskfuncs.queue_draw([self.pos[0], self.pos[1] + idx * 16], [self.size[0], 16], "blue")
					if deskinfo.clickOnce: self.itemClicked(idx)
				deskfuncs.queue_text([self.pos[0] + 2, self.pos[1] + idx * 16], "black", item.name, False) # Here's modification: i added name after item

	popmenu2 = PopUPMenu() # why do i have to do it like this...
	actbut2 = ActionsButton()
	pock2 = Pockets()
	yPosTween1 = None

	def logic(self):
		deskinfo.drawingQueue[0].clear()
		deskinfo.drawingQueue[1].clear()
		deskinfo.drawingQueue[2].clear()

		if dpg.get_mouse_pos(local=False) >= [0.0, 0.0]: deskinfo.mousePos = dpg.get_mouse_pos(local=False)
		if len(deskinfo.interval) != 0: deskinfo.interval[0] = time.time()
		else: deskinfo.interval.append(time.time())
		if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], 0, deskinfo.screenSize[1] - 32, 98, 32):
			self.yPosTween1 = deskfuncs.tween(self.curDecoMenuPos, 16.0, 0.25)
			deskfuncs.queue_draw([8, deskinfo.screenSize[1] - 6], [84, 1], color="black")
			if deskinfo.clickOnce: self.toggleMenu()
		else:
			self.yPosTween1 = deskfuncs.tween(self.curDecoMenuPos, 0.0, 0.25)

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

		redraw()
		deskinfo.prevMousePos = deskinfo.mousePos

desk = Desktop()

def redraw():
	global canvas
	dpg.delete_item(canvas, children_only=False)
	# BG
	# canvas.create_image(int(deskinfo.screenSize[0] / 2), int(deskinfo.screenSize[1] / 2), image=bgImage)
	with dpg.viewport_drawlist(label="canvas") as canvas:
		dpg.bind_font(monospaceFont)
		dpg.draw_text((10, 10), text="SCLDesktop v0.4 Alpha", color=(0,0,0,255), size=16.0)
		dpg.draw_text((8, 8),  text="SCLDesktop v0.4 Alpha", color=(255,255,255,255), size=16.0)
		dpg.draw_text((deskinfo.screenSize[0] - 46, deskinfo.screenSize[1] - 14), text=time.strftime("%H:%M"), color=(0,0,0,255), size=16.0)
		dpg.draw_text((deskinfo.screenSize[0] - 48, deskinfo.screenSize[1] - 16), text=time.strftime("%H:%M"), color=(255,255,255,255), size=16.0)

		for command in deskinfo.drawingQueue[0]:
			if command.startswith("dpg.draw_") and command.find(";") == -1: exec(command) # Dangerous, but we have trust in queue_draw
			else: print("drawingQueue, Before Devices: hack prevented!")

		for command in deskinfo.drawingQueue[1]:
			if command.startswith("dpg.draw_") and command.find(";") == -1: exec(command) # Dangerous, but we have trust in queue_draw
			else: print("drawingQueue, After Devices: hack prevented!")


		# Cursor (ALWAYS THE LAST!)
		if deskinfo.detailLevel > 1:
			dpg.draw_line([deskinfo.mousePos[0] - deskinfo.get_mousespeed()[0], deskinfo.mousePos[1] - deskinfo.get_mousespeed()[1]],
						  [deskinfo.mousePos[0], deskinfo.mousePos[1]],
						  color=(0,0,0,255), thickness=4.0)
			dpg.draw_line([deskinfo.mousePos[0] - deskinfo.get_mousespeed()[0], deskinfo.mousePos[1] - deskinfo.get_mousespeed()[1]],
						  [deskinfo.mousePos[0], deskinfo.mousePos[1]],
						  color=(255,255,255,255), thickness=2.0)
		dpg.draw_rectangle([deskinfo.mousePos[0] - 2, deskinfo.mousePos[1] - 2], [deskinfo.mousePos[0] + 2, deskinfo.mousePos[1] + 2], color=(0,0,0,255), fill=(255,255,255,255), thickness=1.0)

		for command in deskinfo.drawingQueue[2]:
			if command.startswith("dpg.draw_") and command.find(";") == -1: exec(command) # Dangerous, but we have trust in queue_draw
			else: print("drawingQueue, After Everything: hack prevented!")

		dpg.render_dearpygui_frame()

	if len(deskinfo.interval) == 2: deskinfo.interval[1] = time.time()
	else: deskinfo.interval.append(time.time())


def lmb (event:bool): deskinfo.mouseEvents[0] = event; deskinfo.clickOnce = event
def mmb (event:bool): deskinfo.mouseEvents[1] = event
def rmb (event:bool): deskinfo.mouseEvents[2] = event

with dpg.handler_registry():
	dpg.add_mouse_click_handler(0, callback=lambda: lmb(True)); dpg.add_mouse_release_handler(0, callback=lambda: lmb(False))
	dpg.add_mouse_click_handler(1, callback=lambda: mmb(True)); dpg.add_mouse_release_handler(1, callback=lambda: mmb(False))
	dpg.add_mouse_click_handler(2, callback=lambda: rmb(True)); dpg.add_mouse_release_handler(2, callback=lambda: rmb(False))

dpg.setup_dearpygui()
dpg.show_viewport()

while dpg.is_dearpygui_running():
	desk.logic()
	redraw()

dpg.destroy_context()