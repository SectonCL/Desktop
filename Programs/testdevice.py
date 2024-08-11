import deskfuncs
import deskinfo
import deskinterface

class Program(deskinterface.Elements.Device):
    speenValue = 0.0
    speenSpeed: float = 200.0
    name = "TestDevice"
    devtitle = "Device Preview"
    needsExpert = True

    def faster(self): self.speenSpeed += 50.0
    def slower(self): self.speenSpeed -= 50.0
    
    def __init__(self):
        super().__init__()
        print("We hope you already received a warning about running unknown devices/commands/SCLipts in SCLDesktop. "
              "Just in case you didn't, listen REALLY carefully: SCLDesktop and the SCL itself are not isolated "
              "from your host system. That is the case if you are not running this under SCLOS, but even then "
              "a malicious program can enter other drives.\n"
              "We are NOT responsible for any damages done by any malicious device/command/SCLipt you run, so think twice!!!")
        testButton = deskinterface.Elements.Button()
        testButton.label = "Hello World!"
        testButton.pos = [32, 32]
        fastButton = deskinterface.Elements.Button()
        fastButton.label = "Faster!"
        fastButton.pos = [184, 32]
        fastButton.size = [64, 24]
        fastButton.callFunction = self.faster
        slowButton = deskinterface.Elements.Button()
        slowButton.label = "Slower!"
        slowButton.pos = [256, 32]
        slowButton.size = [64, 24]
        slowButton.callFunction = self.slower
        self.drawElements.append(testButton)
        self.drawElements.append(fastButton)
        self.drawElements.append(slowButton)
    
    def think(self):
        super().think()
        self.speenValue += deskinfo.get_deltatime() * self.speenSpeed
        deskfuncs.queue_text(32, 64, "black", f"running apps: {str(deskinfo.runningApplications)}", "nw")
        deskfuncs.queue_text(32, 80, "black", f"drawing device {deskinfo.drawDeviceIndex}", "nw")
        deskfuncs.queue_text(64, 128, "black", f"teeeeest!", "nw", rotation=self.speenValue)