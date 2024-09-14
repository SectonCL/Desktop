import deskinfo
import deskfuncs
import deskinterface


class Program(deskinfo.Application):
    name = "TestService"
    quitButton = deskinterface.Elements.Button()
    
    def __init__(self):
        super().__init__()
        self.quitButton.label = "Stop"
        self.quitButton.pos = [deskinfo.screenSize[0] - 64, 8]
        self.quitButton.size = [48, 24]
        self.quitButton.__init__()
        self.quitButton.callFunction = self.shutdown
        print("A Test Service has been succesfully launched.")
    
    def think(self):
        deskfuncs.queue_text([8, 52], text="Hello World!", shadowed=True)
        deskfuncs.queue_text([8, 24], text=f"Delta time: {deskinfo.get_deltatime()}")
        deskfuncs.queue_text([8, 38], text=f"Mouse Speed: {deskinfo.mousePos[0] - deskinfo.prevMousePos[0]}, {deskinfo.mousePos[1] - deskinfo.prevMousePos[1]}")
        self.quitButton.logic()

    
    def shutdown(self):
        super().shutdown()
        print("Goodbye, Cruel World!")