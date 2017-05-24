import copy

from powercad.interfaces.Q3D.Ipy_script import Q3D_ipy_script

from powercad.general.data_struct.BasicsFunction import *         # group of BasicFunction that can be used for any classes
from powercad.interfaces.Q3D.Electrical import rect_q3d_box


class Layer_Stack:
    
    def __init__(self):
        # e-Layers can be interfaced with FastHenry or Q3D
        self.eLayers=[]   # Set of electrical Layers that will be translated to Q3d or other computational method
        self.Tlayers=[]   # Set of Thermal Layers 
        # Q3d Realated
        self.Q3d_script=Q3D_ipy_script() 
        # Layer Counter
        self.layer_index=0 # index 0 means there is no Layer added
    
    def add_Layers(self, elayer):       # For PowerSynth=Q3d Interface
        for layer in elayer:
            if isinstance(layer, rect_q3d_box):      # check if this is Rect_Box instance
                if self.layer_index!=0:          # if there is at least 1 layer in the topology 
                    layer.faces=add_num_to_list(self.eLayers[self.layer_index-1].faces,28)   # Update the faces index (This let us choose correct face in Q3D) --> [top,bot,xz_close,yz_close,xz_far,yz_far]
                    layer.set_z(self.eLayers[self.layer_index-1].get_z()+self.eLayers[self.layer_index-1].get_thickness())   # Update the height of new layer based on the previous one 
                
                self.eLayers.append(copy.deepcopy(layer))      # add this layer to liet 
                self.layer_index+=1                            # increase list layer index
                layer.set_layer_ID(self.layer_index)           # set layer id=newest index
            
    def define_trace(self,index,bp_dim):
        #index: index of a layer that will be set as trace
        if self.eLayers[index-1]==None or self.eLayers[index-2]==None:
            raise('Layers not existed, or layers doesnt have dielectric below')
        else:    
            self.eLayers[index-1].set_layer_as_trace()                             # set layer as trace 
            bp_width=bp_dim[0]
            bp_length=bp_dim[1]
            self.eLayers[index-1].set_width(bp_width/5)   # set initial trace width based on dielectric (below) width
            self.eLayers[index-1].set_length(bp_length/5) # set initial trace length based on dielectric (below) length
            self.eLayers[index-1].set_x((bp_width-self.eLayers[index-1].get_width())/2)   # Move the initial trace to center of dielectric
            self.eLayers[index-1].set_y((bp_length-self.eLayers[index-1].get_length())/2) # Move the initial trace to center of dielectric
            
    def define_ground(self,index):
        # select a plane as a ground 
        # optional, if not defined then Q3d set ground at infinity, can only be done after define nets
        print 'Code me tmr'

    def get_trace_index(self):
        for layers in self.eLayers:
            if layers.type=='trace':
                return layers.id
        print('No Trace Selected')  # set this as a ctype message later  
                       
    def get_all_elayers(self): # For PowerSynth=Q3d Interface
        str=''                 # a blank string object
        for layers in self.eLayers:      # loop through all layers
            layers.make()
            str=str+layers.get_script() # Update the output script 
        return str            # return the layer structure (can be updated by adding traces and layers.
             
if __name__ == '__main__':
    # Set up rectangle layers (initialize its structure)
    e1=rect_q3d_box()
    e2=rect_q3d_box()
    e3=rect_q3d_box()
    e4=rect_q3d_box()
    # Set size, object name
    e1.set_size(50, 50, 5)
    e1.set_name('Baseplate')
    e2.set_size(48, 48, 0.5)
    e2.set_name('Metal1')
    e3.set_size(50, 50, 0.7)
    e3.set_name('Substrate')
    e4.set_size(48, 48, 0.5)
    e4.set_name('Metal2')
    # Set Materials
    e3.set_material('Al_N')
    # initialize a topology
    T1=Layer_Stack()
    T1.add_Layers([e1, e2, e3, e4])
    T1.define_trace(4)  # Select trace layer (where the optimization will be done)
    
    print 'here'
    script1=Q3D_ipy_script('16.2','C:\Users\qmle\Desktop\Testing\Py_Q3D_test','test1','C:\Users\qmle\Desktop\Testing\Py_Q3D_test')  # Initialize Script Object
    print 'here'
    script1.add_script(T1.get_all_elayers())                                                                                            # Add Topology structure to script  
    script1.set_params('Width', 9, 'XSize',e4,1)               # Set up parameters          
    script1.set_params('Length', 9, 'YSize',e4,1)              # Set up parameters 
    
    script1.identify_net('signal', 'Metal2', 'SignalNet1')     # Create net objects 
    script1.select_source_sink('Source1',e4.get_face(2),'Sink1', e4.get_face(4),'SignalNet1') # Select Source Sink to faces
    script1.analysis_setup()                                   # Set up an analysis, in this case set as default    
    script1.add_freq_sweep('10k', '1M', '10k')                 # Set up frequency sweep on analysis
    script1.analyze_all()                                      # Run analysis
    script1.create_report('Freq', 'ACR','SignalNet1', 'Source1','Sweep1',1)      # Create report 
    script1.update_report('Freq','ACL', 'SignalNet1', 'Source1','Sweep1',1)
    script1.update_report('Freq','C','SignalNet1','','Sweep1',1)
    script1.export_report('Data Table 1', 'C:/Users/qmle/Desktop/Testing/Py_Q3D_test/','test')  # export report to csv files
    
    script1.change_properties('Width',12, 1)
    script1.change_properties('Length',12, 1)
    script1.analyze_all()
    script1.make()    
    script1.build('C:\Users\qmle\workspace\Python_Q3d_model\IronPython\ipy64.exe')  # Use Ipy64.exe to run simulation  
                                            # write all script to string
    script2=Q3D_ipy_script('16.2','C:\Users\qmle\Desktop\Testing\Py_Q3D_test','test2','C:\Users\qmle\Desktop\Testing\Py_Q3D_test')
    
    script2.add_script(script1.script)                              
    script2.set_params('Width', 15, 'XSize',e4,1)               # Set up parameters          
    script2.set_params('Length', 15, 'YSize',e4,1)              # Set up parameters 
    script2.make()
    
    #script2.build('C:\Users\qmle\workspace\Python_Q3d_model\IronPython\ipy64.exe')  # Use Ipy64.exe to run simulation     
    