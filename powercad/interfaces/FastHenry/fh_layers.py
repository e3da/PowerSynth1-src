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

        textout = []
        textout.append('*////////////////////')
        textout.append('* Plane %s' % (str(self.name)))
        # starting node
        textout.append('N%s%ss x=%s y=%s z=%s' % (str(self.name), str(self.id_number), str(self.start_coords[0]),
                                                  str(self.start_coords[1]), str(self.start_coords[2])))
        # ending node
        textout.append('N%s%se x=%s y=%s z=%s' % (str(self.name), str(self.id_number), str(self.end_coords[0]),
                                                  str(self.end_coords[1]), str(self.end_coords[2])))
        # element definition between nodes
        textout.append('E%s%s N%s%ss N%s%se w=%s h=%s sigma=%s' % (str(self.name), str(self.id_number), str(self.name),
                                                                   str(self.id_number), str(self.name),
                                                                   str(self.id_number), str(self.width),
                                                                   str(self.thickness), str(self.conductivity)))

        textout.append('+nwinc=%s nhinc=%s' % (str(self.nwinc), str(self.nhinc)))
        textout.append('*////////////////////')

        return textout

    def equivalent_nodes_text(self):
        return str(
            '.equiv N%s%se N%s%ss' % (str(self.name), str(self.id_number - 1), str(self.name), str(self.id_number)))


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

    text = []
    text.append('*\n')
    text.append('.units mm\n')

    for i in baseplate_text:
        text.append(i + '\n')

    for i in metalplate_text:
        text.append(i + '\n')

    for i in trace_text:
        text.append(i + '\n')

    text.append('\n.external %s %s' % (trace.startnode, trace.endnode))
    text.append('\n.freq fmin=%s fmax=%s ndec=1' % (str(freq), str(freq)))
    text.append('\n.end')
    return text


def write_plane_file(plane_text, filename):
    with open(filename, "w") as text_file:
        for i in plane_text:
            text_file.write(i)


sobol_array = np.array(sb.sobol_seq.i4_sobol_generate(2,100,0))
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

path = "./inputFiles_Sobol/"
if not os.path.exists(path):
    os.makedirs(path)
filename_list = []

for i in range(0, len(length), 1):
    plane_text = single_plane_test('A', 1, length[i], width[i], thickness, height, 5.8e4, 10, 10, 300000)
    filename = path + str('length_%s_width_%s_thickness_%s_height_%s.inp' % (str(length[i]), str(width[i]), str(thickness), str(height)))
    filename_list.append(filename)
    write_plane_file(plane_text, filename)

"""
for i in range(0, len(length), 1):
    for j in range(0, len(width), 1):
        plane_text = single_plane_test('A', 1, length[i], width[j], thickness, height, 5.8e4, 10, 10, 300000)
        filename = path + str('length_%s_width_%s_thickness_%s_height_%s.inp' % (str(length[i]), str(width[j]), str(thickness), str(height)))
        filename_list.append(filename)
        write_plane_file(plane_text, filename)

"""
