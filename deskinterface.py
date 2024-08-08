import deskinfo
import deskfuncs

class Elements():
    class Device(deskinfo.Application):
        devtitle: str = "Unnamed Device"
        color: str = "white"; """Either HEX or color NAME"""
        closeButton: bool = True
        pocketsButton: bool = True

        def __init__(self):
            super().__init__()
            print(f"Starting Interface for {self.devtitle}...")

        def logic(self):
            deskfuncs.queue_draw("box", 0, 0, deskinfo.screenSize[0], deskinfo.screenSize[1] - 32, self.color)

    class Button(deskinfo.DeviceElement):
        label: str = "Ok"
        pos: list[int, int] = [0, 0]
        size: list[int, int] = [128,16]

        def logic(self):
            deskfuncs.queue_draw("box", self.pos[0], self.pos[1], self.size[0], self.size[1], "gray")
            deskfuncs.queue_text(self.pos[0], self.pos[1], color="black", text=self.label)

    class List(deskinfo.DeviceElement):
        items: list = ["Nothing", "was", "added", "here."]
        pos: list[int, int] = [0, 0]
        size: list[int, int] = [128,16]

        def itemClicked(self, index: int):
            if len(self.items) <= index:
                print("DeviceElement List, itemClicked: the index, " + str(index) + ", is out of " + str(len(self.items)) + "'s bounds!")

        def logic(self):
            for idx,item in enumerate(self.items):
                deskfuncs.queue_draw("box", self.pos[0], self.pos[1], self.size[0], self.size[1], "white")
                if deskfuncs.in_box(deskinfo.mousePos[0], deskinfo.mousePos[1], self.pos[0], self.pos[1] + idx * 8, self.pos[0] + self.size[0], self.pos[1] + 16 + self.pos[1] + idx * 8):
                    deskfuncs.queue_draw("box", self.pos[0], self.pos[1] + idx * 8, self.size[0], 16 + self.pos[1] + idx * 8, "blue")
                    if deskinfo.clickOnce: self.itemClicked(idx)
                deskfuncs.queue_text(self.pos[0], self.pos[1] + idx * 8, "black", item, False)