import deskinfo
import deskfuncs

class Elements():
	class Device(deskinfo.Application):
		__type__: str = "device"
		devtitle: str = "Unnamed Device"; """The Device name that will appear on a pocket"""
		color: str = "white"; """Either HEX or color NAME"""
		drawElements: list[deskinfo.DeviceElement] = []; """Put EVERY element you need the user to see!"""
		closeButton: bool = True
		pocketsButton: bool = True; """Hide to pockets button"""

		def __init__(self):
			super().__init__()
			print(f"Starting Interface for {self.devtitle}...")

		def think(self):
			deskfuncs.queue_draw([0, 0], [deskinfo.screenSize[0], deskinfo.screenSize[1] - 32], self.color)
			for element in self.drawElements:
				element.logic()


	class Button(deskinfo.DeviceElement):
		label: str = "Ok"
		toggle: bool = False
		isHolding: bool = False
		pos: list[int, int] = [0, 0]
		size: list[int, int] = [128,24]

		def button_click(self):
			# print("A button was pressed!")
			if self.callFunction is not None: self.callFunction()

		def logic(self):
			isHovered = deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1], self.size[0], self.size[1])
			if self.isHolding:
				deskfuncs.queue_draw([self.pos[0], self.pos[1]], [self.size[0], self.size[1]], "black")
				deskfuncs.queue_text([self.pos[0] + 2, self.pos[1]],
									 color="white", text=self.label)
			elif not isHovered:
				deskfuncs.queue_draw([self.pos[0], self.pos[1]], [self.size[0], self.size[1]], "gray", self.shadows, "black")
				deskfuncs.queue_text([self.pos[0] + 2, self.pos[1]],
									 color="black", text=self.label)

			if not self.isHolding and isHovered:
				deskfuncs.queue_draw([self.pos[0], self.pos[1]], [self.size[0], self.size[1]], "blue")
				deskfuncs.queue_text([self.pos[0], self.pos[1]],
									 color="black", text=self.label)

			if isHovered:
				if deskinfo.clickOnce:
					self.button_click()
					if self.toggle: self.isHolding = not self.isHolding
				if not self.toggle: self.isHolding = deskinfo.mouseEvents[0]


	class Book(deskinfo.DeviceElement):
		currentPage: int = -1
		pages: list[str] = ["Page 1", "Page 2", "Page 3"]
		size = [256, 16]

		def logic(self):
			deskfuncs.queue_draw([self.pos[0], self.pos[1]], [self.size[0], self.size[1]])
			for idx,page in enumerate(self.pages):
				horizbegin = self.pos[0] + (self.size[0] / len(self.pages)) * idx
				horizend = self.size[0] / len(self.pages) # * (idx + 1)
				if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], horizbegin, self.pos[1], horizend, self.pos[1] + self.size[1]):
					if deskinfo.clickOnce: self.pageSwitched(idx)
					deskfuncs.queue_draw([horizbegin, self.pos[1]], [int(self.size[0] / len(self.pages)), self.pos[1] + self.size[1]], "blue")
				deskfuncs.queue_line([horizbegin, self.pos[1]],
									 [horizbegin, self.pos[1] + self.size[1]],
									 (0,0,0,255))
				deskfuncs.queue_text([self.pos[0] + self.size[0] / len(self.pages) * idx + 4, self.pos[1] + 4], (0,0,0,255), text=page)
			if self.currentPage != -1:
				deskfuncs.queue_draw([self.pos[0] + (self.size[0] / len(self.pages)) * self.currentPage, self.pos[1] + self.size[1] / 1.5],
									 [int(self.size[0] / len(self.pages) + 1), int(self.size[1] / 4)], "blue")

		def pageSwitched(self, index):
			print("Page Switched!")
			if index == self.currentPage: self.currentPage = -1
			else: index = self.currentPage


	class List(deskinfo.DeviceElement):
		items: list = ["Nothing", "was", "added", "here."]
		pos: list[int, int] = [0, 0]
		size: list[int, int] = [128,16]

		def itemClicked(self, index: int):
			if len(self.items) <= index:
				print("DeviceElement List, itemClicked: the index, " + str(index) + ", is out of " + str(len(self.items)) + "'s bounds!")
			if self.callFunction is not None: self.callFunction(index)

		def logic(self):
			deskfuncs.queue_draw([self.pos[0], self.pos[1]], [self.size[0], self.size[1]], "white", border="black")
			for idx,item in enumerate(self.items):
				if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1] + idx * 18, self.size[0], 18):
					deskfuncs.queue_draw([self.pos[0], self.pos[1] + idx * 18], [self.size[0], 18], (0, 178, 255, 125), True)
					if deskinfo.clickOnce: self.itemClicked(idx)
				deskfuncs.queue_text([self.pos[0] + 3, self.pos[1] + (idx * 18)], "black", item)


	class Slider(deskinfo.DeviceElement):
		pos: list[int, int] = [0, 0]
		size: list[int, int] = [128, 16]
		min: float = 0.0
		current: float = 50.0
		max: float = 100.0
		isHolding: bool = False
		roundToDigits: int = 1
		normalized_value = (current - min) / (max - min)
		tweenValue1 = deskfuncs.tween(current, pos[0] + (normalized_value * size[0]) - 8, 10)
		curTweenValue1 = tweenValue1()

		def logic(self):
			self.curTweenValue1 = self.tweenValue1()
			self.normalized_value = (self.current - self.min) / (self.max - self.min)
			deskfuncs.queue_draw(self.pos, self.size, "black")
			if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1], self.size[0], self.size[1]) or self.isHolding:
				if deskinfo.clickOnce: self.isHolding = True
				deskfuncs.queue_draw([int(self.curTweenValue1), self.pos[1]], [16, self.size[1]], "blue", self.shadows)
				deskfuncs.queue_msg(str(self.current if self.roundToDigits != 0 else int(self.current)))
			else:
				deskfuncs.queue_draw([int(self.curTweenValue1), self.pos[1]], [16, self.size[1]], "gray")
			if self.isHolding and not deskinfo.mouseEvents[0]: self.isHolding = False
			if self.isHolding:
				oldCurrent = self.current
				self.current = deskfuncs.clamp(round(((deskinfo.mousePos[0] - self.pos[0]) / self.size[0]) * self.max, self.roundToDigits), self.min, self.max)
				self.currentChanged(oldCurrent)

		def currentChanged(self, oldValue):
			self.tweenValue1 = deskfuncs.tween(self.current, self.pos[0] + (self.normalized_value * self.size[0]) - 8, 10)


class EnhancedElements():
	class OptionButton(Elements.Button):
		options: list = []
		openOnHover: bool = True
		toggle = True
		listElement = Elements.List()
		listWidth: int = 100

		def __init__(self):
			super().__init__()
			self.listElement.items = self.options
			self.listElement.callFunction = self.option_clicked

		def logic(self):
			super().logic()
			if self.options != self.listElement.items: self.listElement.items = self.options
			if self.isHolding:
				# We now check if list won't go outside the screen
				# TOP-LEFT check
				if not deskfuncs.out_of_screen_BOX(self.pos[0], self.pos[1] + self.size[1], self.listWidth, len(self.options) * 18):
					self.listElement.pos = [self.pos[0], self.pos[1] + self.size[1]]
					self.listElement.size = [self.listWidth, len(self.options) * 18]
				# BOTTOM-RIGHT check
				elif not deskfuncs.out_of_screen_BOX(self.pos[0] + self.size[0] - self.listWidth, self.pos[1] - len(self.options) * 18, self.listWidth, len(self.options) * 18):
					self.listElement.pos = [self.pos[0] + self.size[0] - self.listWidth, self.pos[1] - len(self.options) * 18]
					self.listElement.size = [self.listWidth, len(self.options) * 18]

				# Then we can give logic to list
				self.listElement.logic()

		def option_clicked(self, index: int):
			self.isHolding = False


	class ListBox(deskinfo.DeviceElement):
		options: list = []
		chosenIndex: int = -1
		listElement = Elements.List()
		listWidth: int = 100
		isHolding: bool = False

		def __init__(self):
			super().__init__()
			self.listElement.items = self.options
			self.listElement.callFunction = self.wasChosen

		def logic(self):
			deskfuncs.queue_draw(self.pos, self.size)
			deskfuncs.queue_draw([self.pos[0] + (self.size[0] - 16), self.pos[1]], [16, self.size[1]], "gray", True)
			deskfuncs.queue_text(self.pos, "black", str(self.options[self.chosenIndex]))
			if self.options != self.listElement.items: self.listElement.items = self.options
			if self.isHolding:
				# We now check if list won't go outside the screen
				# TOP-LEFT check
				if not deskfuncs.out_of_screen_BOX(self.pos[0], self.pos[1] + self.size[1], self.listWidth,
												   len(self.options) * 18):
					self.listElement.pos = [self.pos[0], self.pos[1] + self.size[1]]
					self.listElement.size = [self.listWidth, len(self.options) * 18]
				# BOTTOM-RIGHT check
				elif not deskfuncs.out_of_screen_BOX(self.pos[0] + self.size[0] - self.listWidth,
													 self.pos[1] - len(self.options) * 18, self.listWidth,
													 len(self.options) * 18):
					self.listElement.pos = [self.pos[0] + self.size[0] - self.listWidth,
											self.pos[1] - len(self.options) * 18]
					self.listElement.size = [self.listWidth, len(self.options) * 18]

				# Then we can give logic to list
				self.listElement.logic()

		def wasChosen(self, index: int):
			self.isHolding = False
			self.chosenIndex = index