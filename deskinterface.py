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
            deskfuncs.queue_draw(0, 0, deskinfo.screenSize[0], deskinfo.screenSize[1] - 32, self.color)
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
            if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1],
                                self.size[0], self.size[1]):
                if deskinfo.mouseEvents[0] or self.isHolding:
                    deskfuncs.queue_draw(self.pos[0], self.pos[1], self.size[0], self.size[1], "black")
                    deskfuncs.queue_text(self.pos[0] + int(self.size[0] / 2), self.pos[1] + int(self.size[1] / 2),
                                         color="white", text=self.label, maxwidth=self.size[0])
                else:
                    if self.shadows: deskfuncs.queue_draw(self.pos[0] + 2, self.pos[1] + 2, self.size[0], self.size[1], "black")
                    deskfuncs.queue_draw(self.pos[0], self.pos[1], self.size[0], self.size[1], "blue")
                    deskfuncs.queue_text(self.pos[0] + int(self.size[0] / 2), self.pos[1] + int(self.size[1] / 2),
                                         color="black", text=self.label, maxwidth=self.size[0])
                if deskinfo.clickOnce: self.button_click()
            else:
                if self.shadows: deskfuncs.queue_draw(self.pos[0] + 4, self.pos[1] + 4, self.size[0], self.size[1], "black")
                deskfuncs.queue_draw(self.pos[0], self.pos[1], self.size[0], self.size[1], "gray")
                deskfuncs.queue_text(self.pos[0] + int(self.size[0] / 2), self.pos[1] + int(self.size[1] / 2),
                                     color="black", text=self.label, maxwidth=self.size[0])

    class Book(deskinfo.DeviceElement):
        currentPage: int = -1
        pages: list[str] = ["Page 1", "Page 2", "Page 3"]
        size = [256, 16]

        def logic(self):
            deskfuncs.queue_draw(self.pos[0], self.pos[1], self.size[0], self.size[1])
            for idx,page in enumerate(self.pages):
                horizbegin = self.pos[0] + (self.size[0] / len(self.pages)) * idx
                horizend = self.size[0] / len(self.pages) # * (idx + 1)
                if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], horizbegin, self.pos[1], horizend, self.pos[1] + self.size[1]):
                    if deskinfo.clickOnce: self.pageSwitched(idx)
                    deskfuncs.queue_draw(horizbegin, self.pos[1], int(self.size[0] / len(self.pages)), self.pos[1] + self.size[1], "blue")
                deskfuncs.queue_line([horizbegin, self.pos[1]],
                                     [horizbegin, self.pos[1] + self.size[1]],
                                     "black")
                deskfuncs.queue_text(self.pos[0] + self.size[0] / len(self.pages) * idx + 4, self.pos[1] + 4, "black", page, "nw")
            if self.currentPage != -1:
                deskfuncs.queue_draw(self.pos[0] + (self.size[0] / len(self.pages)) * self.currentPage, self.pos[1] + self.size[1] / 1.5, int(self.size[0] / len(self.pages)), int(self.size[1] / 4), "blue")

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
            deskfuncs.queue_draw(self.pos[0], self.pos[1], self.size[0], self.size[1], "white")
            for idx,item in enumerate(self.items):
                if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1] + idx * 16, self.size[0], 16):
                    deskfuncs.queue_draw(self.pos[0], self.pos[1] + idx * 16, self.size[0], 16, "blue")
                    if deskinfo.clickOnce: self.itemClicked(idx)
                deskfuncs.queue_text(self.pos[0] + 4, self.pos[1] + 4 + (idx * 16), "black", item, "nw")

class EnhancedElements():
    class OptionButton(Elements.Button):
        options: list = []
        openOnHover: bool = True
        showList: bool = False
        listElement = Elements.List()
        listWidth: int = 100

        def __init__(self):
            super().__init__()
            self.listElement.items = self.options
            self.listElement.callFunction = self.option_clicked

        def logic(self):
            super().logic()
            if self.options != self.listElement.items: self.listElement.items = self.options
            if self.showList:
                # We now check if list won't go outside the screen
                # TOP-LEFT check
                if not deskfuncs.out_of_screen_BOX(self.pos[0], self.pos[1] + self.size[1], self.listWidth, len(self.options) * 16):
                    self.listElement.pos = [self.pos[0], self.pos[1] + self.size[1]]
                    self.listElement.size = [self.listWidth, len(self.options) * 16]
                # BOTTOM-RIGHT check
                elif not deskfuncs.out_of_screen_BOX(self.pos[0] + self.size[0] - self.listWidth, self.pos[1] - len(self.options) * 16, self.listWidth, len(self.options) * 16):
                    self.listElement.pos = [self.pos[0] + self.size[0] - self.listWidth, self.pos[1] - len(self.options) * 16]
                    self.listElement.size = [self.listWidth, len(self.options) * 16]

                # Then we can give logic to list
                self.listElement.logic()

        def option_clicked(self, index: int):
            self.showList = False

        def button_click(self):
            # super().button_click()
            if self.showList: self.showList = False
            else: self.showList = True