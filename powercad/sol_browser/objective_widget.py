'''
@author: Peter N. Tucker
'''

import sys
import timeit

from PySide import QtGui, QtOpenGL
from objective_widget_ui import Ui_ObjectiveWidget


# class for individual objective widgets that will be inserted onto the graphing form
class ObjectiveWidget(QtGui.QFrame):
    
    def __init__(self, name_units_, data_, index_, parent=None, window_ = None):
        # setup frame
        QtGui.QFrame.__init__(self,parent)
        self.frame = Ui_ObjectiveWidget()
        self.frame.setupUi(self)
        
        # bring in parameters
        self.name_units = name_units_
        self.data = data_
        self.index = index_
        self.window = window_
        self.data_size = len(self.data)
        
        # create dictionary for axis
        self.chkbox_dict = {'x': self.frame.ckbx_X, 'y': self.frame.ckbx_Y, 'z': self.frame.ckbx_Z}
        
        # connect actions to methods
        self.frame.sldr_env.valueChanged.connect(lambda: self.slider_value_changed("env"))
        self.frame.sldr_pos.valueChanged.connect(lambda: self.slider_value_changed("pos"))
        self.frame.txt_min.textEdited.connect(lambda: self.set_min_max(float(self.frame.txt_min.text()), 
                                                                        float(self.frame.txt_max.text()),
                                                                        self.frame.txt_min))
        self.frame.txt_max.textEdited.connect(lambda: self.set_min_max(float(self.frame.txt_min.text()), 
                                                                        float(self.frame.txt_max.text()),
                                                                        self.frame.txt_max))
        self.frame.ckbx_X.clicked.connect(lambda: self.window.set_graph_axis(self,'x'))
        self.frame.ckbx_Y.clicked.connect(lambda: self.window.set_graph_axis(self,'y'))
        self.frame.ckbx_Z.clicked.connect(lambda: self.window.set_graph_axis(self,'z'))
        
        # display name in widget "name (units)"
        self.frame.grpbx_objective.setTitle(str(self.name_units[0]) + " (" + str(self.name_units[1]) + ")")
        
        # set up mins and maxs of sliders
        self.set_min_max(min(self.data),max(self.data))
        
        # used to filter out data points when displaying results
        self.bool_data = []
        self.displayable_data = []
        
        # initially all points are set to display
        for i in self.data:
            self.bool_data.append(True)
            
        # set up scene for grfx_display
        self.scene = QtGui.QGraphicsScene()
        self.frame.grfx_display.setScene(self.scene)
        self.scene.setSceneRect(0,0,211,20)
        self.frame.grfx_display.setViewport(QtOpenGL.QGLWidget())
        self.draw_display()
        
        
    def set_min_max(self, min_, max_, txtbox=None):
        if min_ <= max_:  # take no action if user put invalid min or max
            # set min and max
            self.min = min_
            self.max = max_
            # set limits for Envelope Size slider
            self.env_min = (self.max - self.min)/100
            self.env_max = self.max - self.min
            # set limits for Position slider
            self.pos_min = self.min
            self.pos_max = self.max
            # set slider positions
            self.frame.sldr_env.setSliderPosition(100)
            self.envelope = self.env_min + (self.env_max-self.env_min)*self.frame.sldr_env.sliderPosition()/100
            self.frame.lbl_env.setText(str(self.envelope))
            self.frame.sldr_pos.setSliderPosition(50)
            self.position = self.pos_min + (self.pos_max-self.pos_min)*self.frame.sldr_pos.sliderPosition()/100
            self.frame.lbl_pos.setText(str(self.position))
            # display sldr positions to user
            self.frame.lbl_env.setText(str(round(self.env_max,2)))
            self.frame.lbl_pos.setText(str(round((self.max + self.min)/2,2)))
            
            # if a textbox is initiating this function:
            if txtbox is not None:
                # unhighlight if highlighed previously
                self.frame.txt_min.setStyleSheet("background-color:white")
                self.frame.txt_max.setStyleSheet("background-color:white")
                # filter data points outside of bounds
                self.window.filter_graph()
                self.window.filter_graph2()
            else:
                # display mins and maxs to user
                self.frame.txt_min.setText("%.2f" % self.min) # rounds, doesn't truncate :-/
                self.frame.txt_max.setText(str(round(self.max,2)))     
        else:
            if txtbox is not None:
                txtbox.setStyleSheet("background-color:pink")
            else:
                raise Exception("Min is less than max of incoming data!")
            
    def slider_value_changed(self, slider):
        # display value in label 
        if slider is "pos":
            self.position = round(self.pos_min + (self.pos_max-self.pos_min)*self.frame.sldr_pos.sliderPosition()/100,2)
            self.frame.lbl_pos.setText(str(self.position))
        elif slider is "env":
            self.envelope = round(self.env_min + (self.env_max-self.env_min)*self.frame.sldr_env.sliderPosition()/100,2)
            self.frame.lbl_env.setText(str(self.envelope))
        # filter graph
        self.window.filter_graph()
        self.window.filter_graph2()
#        t = timeit.Timer(self.window.filter_graph,"print 'filter 1:'")
#        t2 = timeit.Timer(self.window.filter_graph2,"print 'filter 2:'")
#        print t.timeit(1)
#        print t2.timeit(1)
#        print '---------'
        # redraw display
        self.draw_display()

    def filter_point(self,value):
        return (value >= self.min) and (value <= self.max) and (value >= self.position - self.envelope/2) and (value <= self.position + self.envelope/2)

    def draw_display(self):
        # clear scene (if first time running, then draw line)
        try:
            self.scene.removeItem(self.env_left)
            self.scene.removeItem(self.env_right)
            self.scene.removeItem(self.pos_dot)
        except:
            self.line = QtGui.QGraphicsLineItem(5,10,205,10)
            self.scene.addItem(self.line)
        
        # set up position dot
        self.pos_dot_X = 1.92*self.frame.sldr_pos.sliderPosition()+5
        self.pos_dot = QtGui.QGraphicsEllipseItem(self.pos_dot_X,6,8,8)
        
        # set up envelope items
        self.env_left = QtGui.QGraphicsTextItem('(')
        self.env_right = QtGui.QGraphicsTextItem(')')
        self.env_left.setPos(self.pos_dot_X - 0.97*self.frame.sldr_env.sliderPosition()-2,-1)
        self.env_right.setPos(self.pos_dot_X + 0.97*self.frame.sldr_env.sliderPosition(),-1)
        
        # add items to scene
        self.scene.addItem(self.env_left)
        self.scene.addItem(self.env_right)
        self.scene.addItem(self.pos_dot)
        
        
        
#Test function
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    obj_widg = ObjectiveWidget(("Title","Units"),[1.528,2,3,4,5,6,7,8,9,10.326],2)
    obj_widg.show()
    sys.exit(app.exec_())
        