import time
import Programs.testservice
import deskfuncs
import tkinter
import os
import deskinterface
import deskinfo

host = tkinter.Tk(className="SclDesktop")
host.configure(width=deskinfo.screenSize[0], height=deskinfo.screenSize[1])
host.resizable(False, False)
canvas = tkinter.Canvas(host, cursor="none")
canvas.pack(fill="both")
isMenuOpened = False
bgImage = tkinter.PhotoImage(file="./Assets/bg.png")

for file in os.listdir("./Programs"):
    if os.path.isfile("./Programs/" + file):
        exec("import Programs." + file.removesuffix(".py") + "\n"
             f"deskinfo.availableApplications.append(Programs.{file.removesuffix('.py')}.Program)")


class Desktop(deskinfo.Application):
    name = "Environment"
    curDecoMenuPos = 0

    def toggleMenu(self):
        global isMenuOpened
        if    isMenuOpened: isMenuOpened = False
        else: isMenuOpened = True

    class ActionsButton(deskinterface.EnhancedElements.OptionButton):
        options = ["Shut Down", "Re boot", "Hibernate", "Close Device", "Hide to Pockets"]
        pos = [deskinfo.screenSize[0] - 32, deskinfo.screenSize[1] - 32]
        shadows = False
        size = [32, 16]
        label = "ACTS"

        def option_clicked(self, index: int):
            super().option_clicked(index)
            match index:
                case 0: host.quit()
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
        size = [deskinfo.screenSize[0] - pos[0] - 32, 32]

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
            deskfuncs.queue_draw(self.pos[0] + 4, self.pos[1] + 4, self.size[0], self.size[1], "black")
            deskfuncs.queue_draw(self.pos[0], self.pos[1], self.size[0], self.size[1], "white")
            for idx,item in enumerate(self.items):
                if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1] + idx * 16, self.pos[0] + self.size[0], self.pos[1] + 16 + self.pos[1] + idx * 16):
                    deskfuncs.queue_draw(self.pos[0], self.pos[1] + idx * 16, self.size[0], 16, "blue")
                    if deskinfo.clickOnce: self.itemClicked(idx)
                deskfuncs.queue_text(self.pos[0] + 2, 4 + self.pos[1] + idx * 16, "black", item.name, "nw", False, 200) # Here's modification: i added name after item

    popmenu2 = PopUPMenu() # why do i have to do it like this...
    actbut2 = ActionsButton()
    pock2 = Pockets()

    def logic(self):
        deskfuncs.queue_draw(0, canvas.winfo_height() - self.curDecoMenuPos, 100, canvas.winfo_height(), "white")

        if len(deskinfo.interval) != 0: deskinfo.interval[0] = time.time()
        else: deskinfo.interval.append(time.time())
        if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], 0, canvas.winfo_height() - 32, 98, 32):
            self.curDecoMenuPos = int(deskfuncs.lerp(self.curDecoMenuPos, 16, 0.25))
            deskfuncs.queue_draw(8, canvas.winfo_height() - 6, 84, 1, color="black")
            if deskinfo.clickOnce: self.toggleMenu()
        else:
            self.curDecoMenuPos = int(deskfuncs.lerp(self.curDecoMenuPos, 0, 0.25))

        # Give thinking to opened applications
        for service in deskinfo.runningApplications: service.think()
        if deskinfo.drawDeviceIndex != -1: deskinfo.devices[deskinfo.drawDeviceIndex].think()

        self.Pockets.logic(self.pock2)
        if isMenuOpened:
            self.curDecoMenuPos = int(deskfuncs.lerp(self.curDecoMenuPos, 88, 0.1))
            if not deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], 0, canvas.winfo_height() - 32, 98, 32):
                deskfuncs.queue_draw(8, canvas.winfo_height() - 22, 84, 1, color="black")
            deskfuncs.queue_text(8, canvas.winfo_height() + 12 - self.curDecoMenuPos, text="CLOSE", color="black", anchor="nw")
            self.PopUPMenu.logic(self.popmenu2)
        else:
            deskfuncs.queue_text(42, canvas.winfo_height() - 6 - self.curDecoMenuPos, text="PROGRAMS", color="black")
            deskfuncs.queue_text(40, canvas.winfo_height() - 8 - self.curDecoMenuPos, text="PROGRAMS")

        if host.winfo_width() != 1 and host.winfo_height() != 1: # Check if it will spontaneously resize itself
            canvas.configure(width=deskinfo.screenSize[0], height=deskinfo.screenSize[1])
        self.ActionsButton.logic(self.actbut2)
        if deskinfo.mouseEvents[0] and deskinfo.clickOnce: deskinfo.clickOnce = False  # Make sure that clickOnce actually clicksOnce
        redraw()
        deskinfo.prevMousePos = deskinfo.mousePos

desk = Desktop()

def redraw():
    canvas.delete("all")
    # BG
    # canvas.create_rectangle(0, 0, canvas.winfo_width(), canvas.winfo_height(), fill="blue")
    canvas.create_image(int(deskinfo.screenSize[0] / 2), int(deskinfo.screenSize[1] / 2), image=bgImage)
    canvas.create_text(74, 10, text="SCLDesktop v0.3 Alpha", fill="black")
    canvas.create_text(72, 8,  text="SCLDesktop v0.3 Alpha", fill="white")
    canvas.create_text(4, 24, text=f"Delta time: {deskinfo.get_deltatime()}", fill="green", anchor="nw")
    canvas.create_text(4, 48, text=f"Mouse Speed: {deskinfo.mousePos[0] - deskinfo.prevMousePos[0]}, {deskinfo.mousePos[1] - deskinfo.prevMousePos[1]}", fill="black", anchor="nw")
    canvas.create_text(canvas.winfo_width() - 2, canvas.winfo_height() - 14, text=time.strftime("%H:%M"), fill="black", anchor="ne")
    canvas.create_text(canvas.winfo_width() - 4, canvas.winfo_height() - 16, text=time.strftime("%H:%M"), fill="white", anchor="ne")


    for command in deskinfo.drawingQueue:
        if command.startswith("canvas.create_"): exec(command) # Dangerous, but we have trust in queue_draw
        else: print("drawingQueue: hack prevented!")
    deskinfo.drawingQueue.clear()

    # Cursor (ALWAYS THE LAST!)
    if deskinfo.detailLevel > 1:
        canvas.create_line(deskinfo.mousePos[0] - deskinfo.get_mousespeed()[0], deskinfo.mousePos[1] - deskinfo.get_mousespeed()[1], deskinfo.mousePos[0], deskinfo.mousePos[1],
                           smooth=True, width=6)
        canvas.create_line(deskinfo.mousePos[0] - deskinfo.get_mousespeed()[0], deskinfo.mousePos[1] - deskinfo.get_mousespeed()[1], deskinfo.mousePos[0], deskinfo.mousePos[1],
                           fill="white", smooth=True, width=2)
    canvas.create_rectangle(deskinfo.mousePos[0] - 2, deskinfo.mousePos[1] - 2, deskinfo.mousePos[0] + 2, deskinfo.mousePos[1] + 2, fill="white", width=2)

    if len(deskinfo.interval) == 2: deskinfo.interval[1] = time.time()
    else: deskinfo.interval.append(time.time())
    host.after(10, desk.logic)

def motion(event):
    deskinfo.mousePos = [event.x, event.y]
def  lmb (event): deskinfo.mouseEvents[0] = True; deskinfo.clickOnce = True
def  mmb (event): deskinfo.mouseEvents[1] = True
def  rmb (event): deskinfo.mouseEvents[2] = True
def relmb(event): deskinfo.mouseEvents[0] = False; deskinfo.mouseEvents[1] = False; deskinfo.mouseEvents[2] = False # We can't detect... um. you get the idea


host.bind('<Motion>', motion)
host.bind('<Button-1>', lmb)
host.bind('<Button-2>', mmb)
host.bind('<Button-3>', rmb)
host.bind('<ButtonRelease>', relmb)
desk.logic()
host.mainloop()