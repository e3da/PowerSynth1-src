from powercad.corner_stitch.CornerStitch import Rectangle

class CornerStitchSolution:

    def __init__(self, name='', index=None, params=None,fig_data=None):
        """Describes a solution saved from the Solution Browser

        Keyword arguments:
        name -- solution name
        index -- cs solution index
        params -- list of objectives in tuples (name, unit, value)
        fig_data -- list of matplotlib patches to plot the layout
        """
        self.name = name
        self.index = index
        self.params = params
        self.fig_data = fig_data
        self.layout_info={}   # dictionary holding layout_info for a solution with key=size of layout
        self.abstract_info={} # dictionary with solution name as a key and layout_symb_dict as a value


    def form_abs_obj_rect_dict(self, div=1000):
        '''
        From group of CornerStitch Rectangles, form a single rectangle for each trace
        Output type : {"Layout id": {'Sym_info': layout_rect_dict,'Dims': [W,H]} --- Dims is the dimension of the baseplate
        where layout_rect_dict= {'Symbolic ID': [R1,R2 ... Ri]} where Ri is a Rectangle object
        '''

        layout_symb_dict={}
        layout_rect_dict = {}
        p_data = self.layout_info

        W, H = p_data.keys()[0]
        W = float(W) / div
        H = float(H) / div
        rect_dict = p_data.values()[0]
        for r_id in rect_dict.keys():
            # print 'rect id',r_id
            left = 1e32
            bottom = 1e32
            right = 0
            top = 0
            for rect in rect_dict[r_id]:
                type = rect.type
                min_x = float(rect.left) / div
                max_x = float(rect.right) / div
                min_y = float(rect.bottom) / div
                max_y = float(rect.top) / div
                if min_x <= left:
                    left = float(min_x)
                if min_y <= bottom:
                    bottom = float(min_y)
                if max_x >= right:
                    right = float(max_x)
                if max_y >= top:
                    top = float(max_y)
            layout_rect_dict[r_id] = Rectangle(x=left, y=bottom, width=right - left, height=top - bottom, type=type)
        layout_symb_dict[self.name] = {'rect_info': layout_rect_dict, 'Dims': [W, H]}
        #print layout_symb_dict[layout]
        return layout_symb_dict