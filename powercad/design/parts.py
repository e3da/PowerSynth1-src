import os
from Tkinter import *
import copy


class Connection_Table:
    def __init__(self,name="",cons={},width=400,height=200):
        self.table=Tk()
        self.table.resizable(0, 0)
        screen_width = self.table.winfo_screenwidth()
        screen_height = self.table.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.table.geometry("{}x{}+{}+{}".format(width,height,x,y))
        self.table.title("Set Connection For " + name)
        Label(self.table, text="Connections:").grid(row=0, sticky=W)
        self.connections = cons
        self.vars = []
        self.states=[]
    def set_up_table(self):
        row=1
        for conns in self.connections:
            var = IntVar()
            text = conns[0]+" to " + conns[1]
            Checkbutton(self.table, text=text, variable=var).grid(row=row, sticky=W)
            row += 1
            self.vars.append(var)
        Button(self.table, text='Add Connection', command=self.get_var_states).grid(row=row, sticky=W, pady=4)
        self.table.mainloop()

    def get_var_states(self):
        self.table.destroy()
        self.states= [v.get() for v in self.vars]


def set_up_pins_connections(parts=[]):
    """

    :param parts: list of parts
    :return: conn_dict, a table represent selected connections in the layout
    """
    print "Please select the connection of each component"
    conn_dict = {}
    for p in parts:

        if p.type == 1: # only takes care of components for now
            name = p.name + str(p.layout_component_id)
            table = Connection_Table(name=name,cons=p.conn_dict)
            table.set_up_table()
            conn_dict[name]=table.states
    print conn_dict

    return conn_dict






class Part:
    def __init__(self, name=None, type=None, info_file=None, layout_component_id=None, datasheet_link=None):
        """

        :param name: part name : signal_lead, power_lead, MOS, IGBT, Diode
        :param type: lead:0, comp:1
        :param info_file: technology file for each part
        :param layout_component_id: 1,2,3.... id in the layout information
        :param datasheet_link: link to online datasheet or pdf files on PC
        """
        # general info
        self.name = name  # this is used in layout engine for name_id
        self.raw_name = None  # Raw datasheet name
        self.type = type
        self.info_file = info_file
        self.layout_component_id = layout_component_id
        self.datasheet_link = datasheet_link  # link for datasheet
        self.footprint = [0, 0]  # W,H of the components
        self.object = None  # Depends on whether this is a component type for connector type
        self.pin_name = []  # list of pins name
        self.conn_dict = {}  # form a relationship between internal parasitic values and connections
        self.pin_locs = {}  # store pin location for later use. for each pins name the info is [left,bot,width,height,dz]
        self.thickness = 0  # define part thickness

    def load_part(self):
        # Update part info from file
        with open(self.info_file, 'rb') as inputfile:
            pin_read = False
            para_read = False
            for line in inputfile.readlines():
                line = line.strip("\r\n")
                info = line.split(" ")
                if info[0] == "+Name":
                    self.raw_name = info[1]
                elif info[0] == "+Type":
                    if info[1] == "component":
                        self.type = 1
                    elif info[1] == "connector":
                        self.type = 0
                elif info[0] == "+Link":
                    self.datasheet_link = info[1]
                elif info[0] == "+Footprint":
                    self.footprint[0] = float(info[1])  # Width
                    self.footprint[1] = float(info[2])  # Length
                elif info[0] == '+Thickness':
                    self.thickness = float(info[1])
                if info[0] == "+Pins":
                    pin_read = True
                    for p in range(1, len(info)):
                        self.pin_name.append(info[p])
                    continue
                # Handle Pins info
                if ("\t" in info[0]) and pin_read:
                    pin_name = info[0].strip("\t+")
                    pin_loc = info[1:-1]
                    pin_loc = [float(i) for i in pin_loc]
                    pin_loc.append(info[-1])
                    self.pin_locs[pin_name] = pin_loc
                else:
                    pin_read = False
                if info[0] == "+Parasitics":
                    para_read = True
                    continue
                # Handle Connections info
                if ("\t" in info[0]) and para_read:
                    name1 = info[0].strip("\t+")
                    name2 = info[1]
                    connection = (name1, name2)
                    parasitc = {"R": 1e-6, "L": 1e-12, "C": 1e-15}
                    for para_val in info[2:len(info)]:
                        if "R:" in para_val:
                            val = para_val.strip("R:")
                            parasitc["R"] = float(val)
                        elif "L:" in para_val:
                            val = para_val.strip("L:")
                            parasitc["R"] = float(val)
                        elif "C:" in para_val:
                            val = para_val.strip("C:")
                            parasitc["R"] = float(val)
                    self.conn_dict[connection] = parasitc
                else:
                    para_read = False

        #self.show_info()

    def show_info(self):
        print "raw_name", self.raw_name
        print "footprint", self.footprint
        print "pins name", self.pin_name
        print "pins locations",self.pin_locs

        print "connection dictionary"
        for k in self.conn_dict:
            print k, self.conn_dict[k]

def test_load():
    dir = "C:\Users\qmle\Desktop\New Layout Engine\Component"
    for file in os.listdir(dir):
        if file.endswith(".part"):
            file_dir = os.path.join(dir, file)
            P = Part(info_file=file_dir)
            P.load_part()
def test_setup():
    dir = "C:\Users\qmle\Desktop\New Layout Engine\Component"
    Parts = []

    for file in os.listdir(dir):
        if file.endswith(".part"):
            file_dir = os.path.join(dir, file)
            P = Part(info_file=file_dir)
            P.load_part()
            Parts.append(P)
    NewParts=[]
    for P in Parts:
        new_part = copy.deepcopy(P)
        new_part.name = new_part.raw_name
        new_part.layout_component_id=1
        NewParts.append(new_part)

    set_up_pins_connections(NewParts)




if __name__ == "__main__":
    #test_load()
    test_setup()