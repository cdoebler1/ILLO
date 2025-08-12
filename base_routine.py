# Charles Doebler at Feral Cat AI
# Base class for UFO routines

from hardware_manager import HardwareManager
from color_utils import ColorFunctions

class BaseRoutine:
    def __init__(self):
        self.hardware = HardwareManager()
        
    def get_color_function(self, mode):
        """Get color function based on mode, with validation."""
        if mode > 3:
            mode = 1
        color_functions = [ColorFunctions.wheel, ColorFunctions.pink, ColorFunctions.blue]
        return color_functions[mode - 1]
    
    def run(self, mode, volume):
        """Override this method in subclasses."""
        raise NotImplementedError("Subclasses must implement run() method")
