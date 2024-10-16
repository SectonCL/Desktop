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
        testButton = deskinterface.Elements.Button()
        testButton.label = "Hello World!"
        testButton.pos = [32, 32]
        toggleButton = deskinterface.Elements.Button()
        toggleButton.label = "Toggle"
        toggleButton.pos = [184, 32]
        toggleButton.size = [64, 24]
        toggleButton.toggle = True
        testSlider = deskinterface.Elements.Slider()
        testSlider.pos = [32, 96]
        testSlider.size = [512, 16]
        testSlider.roundToDigits = 1
        self.drawElements.append(testButton)
        self.drawElements.append(toggleButton)
        self.drawElements.append(testSlider)
    
    def think(self):
        super().think()
        self.speenValue += deskinfo.get_deltatime() * self.speenSpeed
        deskfuncs.queue_text([32, 64], "blue", f"running apps: {str(deskinfo.runningApplications)}", shadowed=True)
        deskfuncs.queue_text([32, 80], "black", f"drawing device {deskinfo.drawDeviceIndex}")
        deskfuncs.queue_text([64, 128], "black", f"teeeeest!", rotation=self.speenValue)