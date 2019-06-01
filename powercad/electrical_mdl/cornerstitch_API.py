# Collecting layout information from CornerStitch, ask user to setup the connection and show the loop
from powercad.design.parts import *
from powercad.electrical_mdl.e_module import *
from powercad.electrical_mdl.e_struct import *
from powercad.general.data_struct.util import Rect
import networkx as nx
class CS_API:
    # This is an API with cornerstitch
    def __init__(self,comp=[],part_list=[],layer_to_z={}):
        self.pins=None
        self.comp_list=comp
        self.part_list = part_list
        self.e_comps=[] # list of electrical components
        self.e_sheets=[] # list of sheets for connector presentaion
        self.layer_to_z=layer_to_z
    def read_parts(self):
        for i in range(len(self.comp_list)):
            comp = self.comp_list[i]
            part = self.part_list[i]
            x,y,w,h,layout_id,layer_id = comp
            if part.type==0: # this is a connector
                r = Rect(x,y,w,h)
                z = self.layer_to_z[layer_id]
                sh = Sheet(rect=r,net_name=layout_id,z=z)
                self.e_sheets.append(sh)
            elif part.type==1:
                print "TODO"





