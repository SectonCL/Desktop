import deskfuncs
import deskinfo
import deskinterface

class Program(deskinterface.Elements.Device):
    name = "Configuration"
    devtitle = "Configuration"
    needsExpert = True
    detailSlider = deskinterface.Elements.Slider()
    ScreenBox = deskinterface.EnhancedElements.ListBox()
    
    def __init__(self):
        super().__init__()
        print("We hope you already received a warning about running unknown devices/commands/SCLipts in SCLDesktop. "
              "Just in case you didn't, listen REALLY carefully: SCLDesktop and the SCL itself are not isolated from your host system.\n"
              "We are NOT responsible for any damages done by any malicious device/command/SCLipt you run, so think twice!!!")
        self.detailSlider.pos = [128, 16]
        self.detailSlider.roundToDigits = 0
        self.detailSlider.min = 0.0
        self.detailSlider.max = 2.0
        self.detailSlider.current = deskinfo.detailLevel

        self.ScreenBox.pos = [32, 32]
        self.ScreenBox.options = ["640 by 480", "800 by 600", "1280 by 720"]
        self.drawElements.append(self.detailSlider)
        self.drawElements.append(self.ScreenBox)
    
    def think(self):
        super().think()
        deskfuncs.queue_text([16, 16], "black", f"Detail level:")
        deskinfo.detailLevel = int(self.detailSlider.current)