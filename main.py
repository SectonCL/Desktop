import time
import Programs.testservice
import deskfuncs
import tkinter
import os
import deskinterface
from deskinfo import *
import deskinfo

host = tkinter.Tk(className="FakeDesktop")
host.configure(width=screenSize[0], height=screenSize[1])
canvas = tkinter.Canvas(host, cursor="none")
canvas.pack()
isMenuOpened = False
bgImage = tkinter.PhotoImage(file="./Assets/bg.png")

for file in os.listdir("./Programs"):
    if os.path.isfile("./Programs/" + file):
        exec("import Programs." + file.removesuffix(".py") + "\n"
             f"deskinfo.availableApplications.append(Programs.{file.removesuffix('.py')}.Program())")
        print(deskinfo.availableApplications)


class Desktop(Application):
    name = "Environment"
    curDecoMenuPos = 0

    def toggleMenu(self):
        global isMenuOpened
        if    isMenuOpened: isMenuOpened = False
        else: isMenuOpened = True

    class PopUPMenu(deskinterface.Elements.List):
        items = []
        size = [100, screenSize[1] - 32]

        def __init__(self):
            super().__init__()
            for app in deskinfo.availableApplications:
                self.items.append(app)

        def itemClicked(self, index: int):
            global isMenuOpened
            super().itemClicked(index)
            runningApplications.append(self.items[index])
            isMenuOpened = False

        def logic(self):
            # super().logic() # override standard logic
            # With this:
            for idx,item in enumerate(self.items):
                deskfuncs.queue_draw("box", self.pos[0], self.pos[1], self.size[0], self.size[1], "white")
                if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1] + idx * 8, self.pos[0] + self.size[0], self.pos[1] + 16 + self.pos[1] + idx * 8):
                    deskfuncs.queue_draw("box", self.pos[0], self.pos[1] + idx * 8, self.size[0], 16 + self.pos[1] + idx * 8, "blue")
                    if deskinfo.clickOnce: self.itemClicked(idx)
                deskfuncs.queue_text(self.pos[0], self.pos[1] + idx * 8, "black", item.name, False) # Here's modification: i added name after item

    popmenu2 = PopUPMenu() # why do i have to do it like this...

    def logic(self):
        deskfuncs.queue_draw("box", 0, canvas.winfo_height() - self.curDecoMenuPos, 100, canvas.winfo_height(), "white")

        if len(interval) != 0: interval[0] = time.time()
        else: interval.append(time.time())
        if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], 0, canvas.winfo_height() - 32, 98, 32):
            self.curDecoMenuPos = int(deskfuncs.lerp(self.curDecoMenuPos, 16, 0.25))
            deskfuncs.queue_text(40, canvas.winfo_height() - 24, text="PROGRAMS")
            deskfuncs.queue_draw("box", 8, canvas.winfo_height() - 6, 84, 1, color="black")
            if deskinfo.clickOnce: self.toggleMenu()
        else:
            self.curDecoMenuPos = int(deskfuncs.lerp(self.curDecoMenuPos, 0, 0.25))
            deskfuncs.queue_text(40, canvas.winfo_height() - 16, text="PROGRAMS")

        # Give thinking to opened applications
        for service in deskinfo.runningApplications:
            service.think()

        if isMenuOpened:
            self.curDecoMenuPos = int(deskfuncs.lerp(self.curDecoMenuPos, 48, 0.25))
            deskfuncs.queue_draw("box", 8, canvas.winfo_height() - 24, 84, 1, color="black")
            self.PopUPMenu.logic(self.popmenu2)

        if host.winfo_width() != 1 and host.winfo_height() != 1: # Check if it will spontaneously resize itself
            canvas.configure(width=screenSize[0], height=screenSize[1])
        if mouseEvents[0] and deskinfo.clickOnce: deskinfo.clickOnce = False  # Make sure that clickOnce actually clicksOnce
        redraw()

desk = Desktop()

def redraw():
    canvas.delete("all")
    # BG
    # canvas.create_rectangle(0, 0, canvas.winfo_width(), canvas.winfo_height(), fill="blue")
    canvas.create_image(int(screenSize[0] / 2), int(screenSize[1] / 2), image=bgImage)
    canvas.create_rectangle(100, canvas.winfo_height(), canvas.winfo_width(), canvas.winfo_height() - 32, fill="white")
    canvas.create_text(74, 8, text="fakeDesktop v0.1 Alpha", fill="black")
    canvas.create_text(72, 6, text="fakeDesktop v0.1 Alpha", fill="white")
    if len(interval) == 2: canvas.create_text(128, 24, text=f"CPU Interval: {interval[0] - interval[1]}")


    for command in drawingQueue: exec(command) # Dangerous, but we have trust in queue_draw
    drawingQueue.clear()

    # Cursor (ALWAYS THE LAST!)
    canvas.create_rectangle(deskinfo.mousePos[0] - 2, deskinfo.mousePos[1] - 2, deskinfo.mousePos[0] + 2, deskinfo.mousePos[1] + 2, fill="black")
    canvas.create_rectangle(deskinfo.mousePos[0] - 1, deskinfo.mousePos[1] - 1, deskinfo.mousePos[0] + 1, deskinfo.mousePos[1] + 1, fill="white")

    if len(interval) == 2: interval[1] = time.time()
    else: interval.append(time.time())
    host.after(10, desk.logic)

def motion(event):
    deskinfo.mousePos = [event.x, event.y]
def  lmb (event): mouseEvents[0] = True; deskinfo.clickOnce = True
def  mmb (event): mouseEvents[1] = True
def  rmb (event): mouseEvents[2] = True
def relmb(event): mouseEvents[0] = False; mouseEvents[1] = False; mouseEvents[2] = False # We can't detect... um. you get the idea


host.bind('<Motion>', motion)
host.bind('<Button-1>', lmb)
host.bind('<Button-2>', mmb)
host.bind('<Button-3>', rmb)
host.bind('<ButtonRelease>', relmb)
desk.logic()
host.mainloop()