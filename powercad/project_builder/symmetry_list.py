'''
Created on Apr 29, 2013

@author: bxs003

Note:
The nomenclature for symmetry groups has been changed to design variable correlations.
This is reflected in the GUI, but not in the code yet.
'''

import traceback

from PySide import QtCore, QtGui

from powercad.sym_layout.symbolic_layout import SymLine, SymPoint

class SymmetryItem(object): #done
    def __init__(self, SymmUI, row_item, symmetry_list, color_index):
        self.row_item = row_item
        self.table = SymmUI.parent.ui.tbl_symmetry
        self.symmetry_lists = SymmUI.parent.project.symb_layout.symmetries
        self.used_colors = SymmUI.used_colors
        self.symmetry_list = symmetry_list
        self.color_index = color_index
        self.SymmUI = SymmUI
        
        self.remove_button = QtGui.QPushButton(self.table)
        self.remove_button.setText('X')
        self.remove_button.pressed.connect(self.remove)
        self.table.setCellWidget(self.row_index(),2,self.remove_button)
    
    def remove(self): #done
        patch_dict = self.SymmUI.parent.patch_dict
        
        # remove constraints from each object
        for obj in self.symmetry_list:
            obj.constraint = None

        # remove color from associated elements
        for patch, symbolic in list(patch_dict.items()):
            if symbolic in self.symmetry_list:
                if patch.window == self.SymmUI.parent.SYMMETRY_PLOT or\
                   patch.window == self.SymmUI.parent.CONSTRAINT_PLOT:
                    patch.set_facecolor(self.SymmUI.parent.default_color)
                    patch.symmetry = None
        
        self.symmetry_lists.remove(self.symmetry_list)
        self.table.removeRow(self.row_index())
        self.used_colors[self.color_index] = False
        self.SymmUI.symmetry_items.remove(self)
        
        # Update symmetry and constraints plots
        self.SymmUI.parent.symb_canvas[self.SymmUI.parent.SYMMETRY_PLOT].draw()
        self.SymmUI.parent.symb_canvas[self.SymmUI.parent.CONSTRAINT_PLOT].draw()
        
    def row_index(self): #done
        return self.table.row(self.row_item)
    
    def get_constraint(self): #done
        for layout_obj in self.symmetry_list:
            if hasattr(layout_obj, 'constraint'):
                if layout_obj.constraint is not None:                    
                    return layout_obj.constraint
        return None

class SymmetryListUI(object): #done
    
    def __init__(self, parent):
        ''' Symmetry Identification Module
        
            Keyword Arguments:
            parent: ProjectBuilder object
        '''
        self.parent = parent
        self.ui = self.parent.ui
        self.project= self.parent.project
        self.color_wheel = self.parent.color_wheel
        
        # Setup table
        self._setup_symb_fields()
        
        # Connect actions
        self.ui.btn_new_symmetry.pressed.connect(self.add_symmetry)
        
        self.symmetry_items = []
        self.used_colors = [] # stores which colors have been used
        for __ in self.color_wheel: #sxm - why use "__"?
            self.used_colors.append(False)
            
        # connect pick event
        self.parent.symb_canvas[self.parent.SYMMETRY_PLOT].mpl_connect('pick_event', self.symmetry_pick)

    def _setup_symb_fields(self):
        # set up table that displays added symmetries in Symmetry Selection
        # sxm - The numbers seem hardcoded. Not sure what they represent.
        self.ui.tbl_symmetry.setColumnCount(3)
        self.ui.tbl_symmetry.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeMode.Custom)
        self.ui.tbl_symmetry.setColumnWidth(0,50)
        self.ui.tbl_symmetry.setColumnWidth(2,50)
        #self.ui.tbl_symmetry.horizontalHeader().setStretchLastSection(True)
        # set up table that displays added performances in Performance Identification Selection
        self.ui.tbl_performance.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeMode.Custom)
        self.ui.tbl_performance.setColumnWidth(0,20)
        self.ui.tbl_performance.setColumnWidth(2,80)
        self.ui.tbl_performance.setColumnWidth(3,100)
        self.ui.tbl_performance.setColumnWidth(4,20)
    
    def load_symmetries(self): #done
        #self.project.symb_layout.symmetries = []
        
        for symmetry_list in self.project.symb_layout.symmetries:
            self.add_symmetry(symmetry_list, True)
                
        self.parent.symb_canvas[self.parent.SYMMETRY_PLOT].draw()
        self.parent.symb_canvas[self.parent.CONSTRAINT_PLOT].draw()

    def add_symmetry(self, symmetry_list=None, from_load=False): #done
        """Add symmetry item to list"""
        patch_dict = self.parent.patch_dict
        row = self.ui.tbl_symmetry.rowCount()
        
        # Get next color, if too long prevent adding new symmetry
        if row >= len(self.color_wheel)-1:
            QtGui.QMessageBox.warning(self.parent, "Color Wheel Overflow", "Not enough colors to represent symmetries! Increase color wheel count or change paradigm!")
            return
            
        # get free color from color wheel
        for i in range(len(self.color_wheel)):
            if not self.used_colors[i]:
                color_index = i
                break
            
        self.used_colors[color_index] = True
        bg_color = self.color_wheel[color_index]
        
        # add row to table
        self.ui.tbl_symmetry.insertRow(row)
        self.ui.tbl_symmetry.setItem(row,0,QtGui.QTableWidgetItem())
        self.ui.tbl_symmetry.item(row,0).setBackground(QtGui.QBrush(bg_color))
        # add list to symm_list
        if not from_load:
            symmetry_list = []
            self.project.symb_layout.symmetries.append(symmetry_list)
        else:
            # color objects in symmetry list the designated color
            for patch, symbolic in list(patch_dict.items()):
                if symbolic in symmetry_list:
                    if patch.window == self.parent.SYMMETRY_PLOT or \
                       patch.window == self.parent.CONSTRAINT_PLOT:
                        patch.set_facecolor(bg_color.getRgbF())
                        patch.symmetry = symmetry_list
       
        # display everything in table
        row_item = QtGui.QTableWidgetItem()
        self.ui.tbl_symmetry.setItem(row, 1, row_item)
        row_item.setText('Correlation')
        
        # create representative item
        symm_item = SymmetryItem(self, row_item, symmetry_list, color_index)
        self.symmetry_items.append(symm_item)
        
    def symmetry_pick(self, event): #done
        """Pick event called when symmetry selection symbolic layout is clicked"""
        patch_dict = self.parent.patch_dict
        
        if len(self.ui.tbl_symmetry.selectionModel().selectedIndexes()) < 1:
            return
        
        # save the row number and its corresponding layout parts (symmetries)   
        row_sel = self.ui.tbl_symmetry.selectionModel().selectedIndexes()[0].row()
        symm_item = self.symmetry_items[row_sel]
        selected_elem = patch_dict.get_layout_obj(event.artist)
        constraint = symm_item.get_constraint()
        
        # remove from any other symmetry lists
        for symm_list in self.project.symb_layout.symmetries:
            if selected_elem in symm_list:
                symm_list.remove(selected_elem)
        
        # select a color for the object
        col = self.color_wheel[symm_item.color_index]
        color = col.getRgbF()
        color = (color[0],color[1],color[2],0.5)
        
        # if the artist is already colored that color
        if event.artist.get_facecolor() == color:
            # set back to default color
            event.artist.set_facecolor(self.parent.default_color)
            # do same in constraint section ("Constraint Creation" page)
            if isinstance(selected_elem, SymLine):
                patch_dict.get_patch(selected_elem, 2).set_facecolor(self.parent.default_color)
                patch_dict.get_patch(selected_elem, 2).symmetry = symm_item.symmetry_list                
            # Remove constraint
            selected_elem.constraint = None
        else:
            # color object
            event.artist.set_facecolor(color)
            # color object in constraint section ("Constraint Creation' page) as well
            if isinstance(selected_elem, SymLine):
                patch_dict.get_patch(selected_elem, 2).set_facecolor(color)
                patch_dict.get_patch(selected_elem, 2).set_alpha(0.25)
                patch_dict.get_patch(selected_elem, 2).symmetry = symm_item.symmetry_list
            # add to symmetry list in symm_list
            self.project.symb_layout.symmetries[row_sel].append(selected_elem)
            
            # check if object has constraint
            if selected_elem.constraint is not None:
                QtGui.QMessageBox.warning(self.parent, "Existing Constraint", "Selected object has a constraint! Object will take on constraint of the symmetry selection!")
            selected_elem.constraint = constraint # copy constraint to object
            
        self.parent.symb_canvas[self.parent.SYMMETRY_PLOT].draw()
        self.parent.symb_canvas[self.parent.CONSTRAINT_PLOT].draw()
        

