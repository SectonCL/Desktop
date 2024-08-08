import deskinfo
import deskfuncs

class Program(deskinfo.Application):
    name = "TestService"
    
    def __init__(self):
        super().__init__()
        print("A Test Service has been succesfully launched.")
    
    def think(self):
        deskfuncs.queue_text(0, 48, text="Hello World!", centered=False, shadowed=True)
    
    def shutdown(self):
        super().shutdown()
        print("Goodbye, Cruel World!")