"""A simple script to write planes for use in FastHenry
@author: tmevans
"""

import numpy as np
import sobol as sb

import os


class Plane(object):
    """Object for creating planes to be written out as a text file for use in FastHenry"""

    def __init__(self, name, id_number, start_coords, end_coords, width, thickness, conductivity, nwinc, nhinc):
        """Instantiation of the parameters used in creating a plane. These are defined as:
        :param name: Unique name for the plane being created
        :param id_number: Unique number identifying the segment
        :param start_coords: Cartesian coordinates of the starting node of the plane in format [x,y,z]
        :param end_coords: Cartesian coordinates of the ending node of the plane in format [x,y,z]
        :param width: Width of the plane in mm
        :param thickness: Thickness of the plane in mm
        :param conductivity: Conductivity of the material in Siemens/mm (Cu=5.85e4,3.69e4 )
        :param nwinc: Number of lateral filaments for computation
        :param nhinc: Number of vertical filaments for computation
        :type name: string
        :type id_number: int
        :type start_coords: float array
        :type end_coords: float array
        :type width: float
        :type thickness: float
        :type conductivity: float
        :type nwinc: int
        :type nhinc: int
        """
        self.name = name
        self.id_number = id_number
        self.start_coords = start_coords
        self.end_coords = end_coords
        self.width = width
        self.thickness = thickness
        self.conductivity = conductivity
        self.nwinc = nwinc
        self.nhinc = nhinc
        self.startnode = str('N%s%ss' % (str(self.name), str(self.id_number)))
        self.endnode = str('N%s%se' % (str(self.name), str(self.id_number)))

    def plane_text(self):
        """Method for generating the necessary block of string for the FastHenry input file
        :returns: A block of text with each line as a list in an array
        :rtype: string array
        """
        textout = plane.format(self.name, self.start_coords[0],self.start_coords[1],self.start_coords[2], self.end_coords[0],self.end_coords[1],self.end_coords[2], self.width,self.thickness,self.conductivity,self.nwinc,self.nhinc,self.id_number)
        print textout
        return textout

    def equivalent_nodes_text(self):
        return str(
            '.equiv N%s%se N%s%ss' % (str(self.name), str(self.id_number - 1), str(self.name), str(self.id_number)))


class wire(object):
    """Wire Definition class
    Attributes:
            name: Wire name based on group name
            start: 1st bond position [x,y,z]
            loopHeight: Loope height above midpoint
            loop: Loop position [x,y,z]
            end: 2nd bond position [x,y,z]
            elem1: 1st bond to loop middle
            elem2 : Loop middle to 2nd bond
            diameter: Wire diameter
            conductivity: Wire conductivity
    """

    def __init__(self, name, start, end, loopHeight, loopDirection, diameter, conductivity):
        start = np.array(start)
        end = np.array(end)
        loopDirection = np.array(loopDirection)
        self.name = name
        self.start = start
        self.end = end
        self.loopDirection = loopDirection
        self.loopHeight = loopHeight
        self.diameter = diameter
        self.conductivity = conductivity
        self.vector = end - start
        self.loop = (start + end) / 2.0 + loopDirection * loopHeight


def wireText(wireIn, equiv1, equiv2, nwinc, nhinc):
    textout = []
    textout.append('****************************')
    textout.append('* Wire %s' % (str(wireIn.name)))
    textout.append(
        'N%ss x=%s y=%s z=%s' % (str(wireIn.name), str(wireIn.start[0]), str(wireIn.start[1]), str(wireIn.start[2])))
    textout.append(
        'N%sm x=%s y=%s z=%s' % (str(wireIn.name), str(wireIn.loop[0]), str(wireIn.loop[1]), str(wireIn.loop[2])))
    textout.append(
        'N%se x=%s y=%s z=%s' % (str(wireIn.name), str(wireIn.end[0]), str(wireIn.end[1]), str(wireIn.end[2])))
    textout.append('E%ss N%ss N%sm w=%s h=%s sigma=%s' % (
    str(wireIn.name), str(wireIn.name), str(wireIn.name), str(wireIn.diameter), str(wireIn.diameter),
    str(wireIn.conductivity)))
    textout.append('+nwinc=%s nhinc=%s' % (str(nwinc), str(nhinc)))
    textout.append('E%se N%sm N%se w=%s h=%s sigma=%s' % (
    str(wireIn.name), str(wireIn.name), str(wireIn.name), str(wireIn.diameter), str(wireIn.diameter),
    str(wireIn.conductivity)))
    textout.append('+nwinc=%s nhinc=%s' % (str(nwinc), str(nhinc)))
    textout.append('.equiv N%ss %s' % (str(wireIn.name), str(equiv1)))
    textout.append('.equiv N%se %s' % (str(wireIn.name), str(equiv2)))
    textout.append('****************************')
    return textout

def single_plane_test(name, id, length, width, thickness, height, conductivity, nwinc, nhinc, freq):
    """Single plane generation for testing inductance and resistance"""
    start = np.array([0, -length / 2, (height + thickness / 2)])
    end = np.array([0, length / 2, (height + thickness / 2)])
    trace = Plane(name, id, np.array(start), end, width, thickness, conductivity, nwinc, nhinc)
    trace_text = trace.plane_text()

    baseplate = Plane('BP', 1, np.array([0, -74.93 / 2, -2.11]), np.array([0, 74.93 / 2, -2.11]), 91.44, 3.81,
                      conductivity, nwinc, nhinc)
    baseplate_text = baseplate.plane_text()

    metalplate = Plane('MP', 1, np.array([0, -74.73 / 2, -0.205]), np.array([0, 74.73 / 2, -0.205]), 91.24, 0.41,
                       conductivity, nwinc, nhinc)
    metalplate_text = metalplate.plane_text()

    text = '.units mm'
    text += baseplate_text
    text += metalplate_text
    text += trace_text


    text+=('\n.external %s %s' % (trace.startnode, trace.endnode))
    text+=('\n.freq fmin=%s fmax=%s ndec=1' % (str(freq), str(freq)))
    text+=('\n.end')
    return text


def write_plane_file(plane_text, filename):
    with open(filename, "w") as text_file:
        for i in plane_text:
            text_file.write(i)



plane="""
*-----------------------------------------------
* Plane {0}
N{0}{12}s x={1} y={2} z={3}
N{0}{12}e x={4} y={5} z={6}
E{0}{12} N{0}{12}s N{0}{12}e w={7} h={8} sigma={9}
+nwinc={10} nhinc={11}
*-----------------------------------------------
"""


def wireGroup(groupName, origin, start, end, direction, pitch, number, wireDiameter, equiv1, equiv2):
    loopHeight = 1.0
    loopDirection = [0, 0, 1]
    # wireDiameter = 0.350
    sigma = 5.8e4
    nwinc = 3
    nhinc = 3

    origin = np.array(origin)
    start = np.array(start) - origin
    end = np.array(end) - origin
    direction = np.array(direction)
    offset = direction * pitch

    for j in range(0, number, 1):
        for i in wireText(
                wire('W%s' % (str(groupName) + str(j)), start + offset * j, end + offset * j, loopHeight, loopDirection,
                     wireDiameter, sigma), equiv1, equiv2, nwinc, nhinc):
            print i


def output_fh_script(md, filename):
    filename = filename + '.inp'
    text_file = open(filename, "w")
    # given XYZ variables
    # only care about conductor since quasistatic method does not account for dielectric anyway
    (BaseXSize, BaseYSize, BaseZSize) = md.baseplate.dimensions
    (MetalXSize, MetalYSize) = (DielectricXSize, DielectricYSize) = (SolderXSize, SolderYSize) = md.substrate.dimensions
    sub_origin_x = BaseXSize / 2.0 - MetalXSize / 2.0
    sub_origin_y = BaseYSize / 2.0 - MetalYSize / 2.0
    SolderZSize = md.substrate_attach.thickness
    MetalZSize = md.substrate.substrate_tech.metal_thickness
    DielectricZSize = md.substrate.substrate_tech.isolation_thickness
    # Z positions
    SolderZPos = md.baseplate.dimensions[2]
    MetalZPos = md.substrate_attach.thickness + SolderZPos
    DielectricZPos = md.substrate.substrate_tech.metal_thickness + MetalZPos
    TraceZPos = md.substrate.substrate_tech.isolation_thickness + DielectricZPos
    TraceZSize = MetalZSize
    #material properties

    bp_cond=1/md.baseplate.baseplate_tech.properties.electrical_res
    mp_cond=1/md.substrate.substrate_tech.metal_properties.electrical_res
    # Convert to plane text
    nwinc = 10
    nhinc = 10
    BP = Plane('BP', 1, np.array([BaseXSize/2, 0, 0]), np.array([BaseXSize/2, BaseYSize, 0]), BaseXSize, BaseZSize,
                      bp_cond, nwinc, nhinc)
    baseplate_text = BP.plane_text()
    MP = Plane('MP', 1, np.array([sub_origin_x+MetalXSize/2, sub_origin_y, MetalZPos]), np.array([sub_origin_x+MetalXSize/2,sub_origin_y+ MetalYSize, MetalZPos]), MetalXSize, MetalZSize,
               mp_cond, nwinc, nhinc)
    metal_text=MP.plane_text()

    script=baseplate_text+metal_text
    # Metal Layers
    for index in xrange(len(md.traces)):
        trace = md.traces[index]
        trace.translate(0, 0)
        name = "trace" + str(index + 1)
        TraceXSize = trace.width()
        start = np.array([trace.width()/2 + trace.left,trace.bottom,TraceZPos])
        stop = np.array([trace.width()/2 + trace.left,trace.top,TraceZPos])
        trace_script=Plane(name,index,start,stop,TraceXSize,TraceZSize,mp_cond,nwinc,nhinc)
        trace_text=trace_script.plane_text()
        script+=trace_text

    # BW Layers
    for index in xrange(len(md.bondwires)):
        bw = md.bondwires[index]
        BwXPos, BwYPos = bw.positions[0]
        BwDiam = bw.eff_diameter
        BwDir = np.array(bw.positions[1]) - np.array(bw.positions[0])
        Distance = np.linalg.norm(BwDir)
        BwXPos += sub_origin_x
        BwYPos += sub_origin_y
        BwZPos = TraceZPos+TraceZSize+bw.beg_height
        h1 = bw.height
        h2 = bw.beg_height
        name = "bondwire" + str(index+1)
        text_file += create_bondwire.format(name, BwDiam, BwXPos, BwYPos, BwZPos, BwDir[0], BwDir[1], Distance, h1, h2, BwMaterial)
    text_file += apply_netting
    text_file.write(script)
    text_file.close()

if __name__ == "__main__":
    sobol_array = np.array(sb.sobol_seq.i4_sobol_generate(2,3,0))
    length = sobol_array[0,:] * 59 + 1
    width =  sobol_array[1,:]  * 14 + 1
    print length
    print width

    """
    length = np.array([1,5,10,15,20,25,30,35,40,45,50,55,60])
    width = np.arange(1, 16, 1)
    #thickness = np.array((0.25, 0.3, 0.35, 0.4))
    #height = np.array((0.25, 0.32, 0.38, 0.5, 0.63, 1.00))+
    """

    height = 0.32
    thickness = 0.4

    path = "C:/Users/qmle/Desktop/Testing/FastHenry/New folder/"
    if not os.path.exists(path):
        os.makedirs(path)
    filename_list = []

    for i in range(0, len(length), 1):
        plane_text = single_plane_test('A', 1, length[i], width[i], thickness, height, 5.8e4, 10, 10, 300000)
        filename = path + str('length_%s_width_%s_thickness_%s_height_%s.inp' % (str(length[i]), str(width[i]), str(thickness), str(height)))
        filename_list.append(filename)
        write_plane_file(plane_text, filename)


    for i in range(0, len(length), 1):
        for j in range(0, len(width), 1):
            plane_text = single_plane_test('A', 1, length[i], width[j], thickness, height, 5.8e4, 10, 10, 300000)
            filename = path + str('length_%s_width_%s_thickness_%s_height_%s.inp' % (str(length[i]), str(width[j]), str(thickness), str(height)))
            filename_list.append(filename)
            write_plane_file(plane_text, filename)

    wireGroup('A', [0, 0, 0], [0, 0, 0], [0, 10, 0], [1, 0, 0], 0.4, 1, 4, 'Nin', 'Nout')