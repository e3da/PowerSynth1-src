# Collecting layout information from CornerStitch, ask user to setup the connection and show the loop
from powercad.design.parts import *
class node:
    # This is a simple node to show the selected loop
    def __init__(self):
        self.pos = [0,0] # left,bottom
        self.z = 0