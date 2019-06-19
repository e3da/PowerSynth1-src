import sys
import numpy as np
# from simplejson import JSONEncoder
import simplejson as json
import matlab.engine
import cPickle as pickle


class Feature(object):
    def __init__(self, entity=None, ref_loc=[0., 0., 0.],  x=None, y=None, z=None, w=None, l=None, h=None,
                 dx=1, dy=1, dz=1, material=None, substrate=None, power=0, name=None):
        self.name = name
        self.entity = entity
        self.ref_loc = ref_loc
        self.material = material
        self.x = x
        self.y = y
        self.z = z
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.width = w
        self.length = l
        self.height = h
        self.child_features = None
        self.substrate = substrate
        self.power = power
        self.h_val = None
        self.type = self.entity.__class__.__name__
        self.possible_types = {'DeviceSolution': self.def_device,
                               'BaseplateInstance': self.def_baseplate,
                               'SubstrateInstance': self.def_substrate,
                               'SubstrateAttachInstance': self.def_substrate_attach,
                               'Rect': self.def_trace
                               }

        if self.type in self.possible_types:
            self.possible_types[self.type]()

    def def_device(self):
        self.length, self.width, self.height = self.entity.device_instance.device_tech.dimensions
        left = self.entity.footprint_rect.left
        bottom = self.entity.footprint_rect.bottom
        die_attach_height = self.entity.device_instance.attach_thickness
        die_attach_z = np.array([0., die_attach_height]) + self.ref_loc[2]

        self.x = np.array([0., self.width]) + self.ref_loc[0] + left
        self.y = np.array([0., self.length]) + self.ref_loc[1] + bottom
        self.z = np.array([0., self.height]) + die_attach_z + die_attach_height
        self.material = MaterialProperties(self.entity.device_instance.device_tech.properties)
        self.power = float(self.entity.device_instance.heat_flow)

        die_attach_material = MaterialProperties(self.entity.device_instance.attach_tech.properties)
        die_attach = Feature(x=self.x, y=self.y, z=die_attach_z,
                             dx=self.dx, dy=self.dy, dz=self.dz,
                             w=self.width, l=self.length, h=die_attach_height,
                             material=die_attach_material)
        self.child_features = [die_attach]

    def def_baseplate(self):
        self.width, self.length, self.height = self.entity.dimensions
        self.x = np.array([0., self.width]) + self.ref_loc[0]
        self.y = np.array([0., self.length]) + self.ref_loc[1]
        self.z = np.array([0., self.height]) + self.ref_loc[2]
        self.material = MaterialProperties(self.entity.baseplate_tech.properties)
        self.h_val = self.entity.eff_conv_coeff

    def def_substrate(self):
        self.width, self.length = self.entity.dimensions
        metal_height = self.entity.substrate_tech.metal_thickness
        isolation_height = self.entity.substrate_tech.isolation_thickness
        self.height = isolation_height
        ledge_width = float(self.entity.ledge_width)

        self.x = np.array([0., self.width]) + self.ref_loc[0]
        self.y = np.array([0., self.length]) + self.ref_loc[1]
        self.z = np.array([0., self.height]) + self.ref_loc[2] + metal_height
        self.material = MaterialProperties(self.entity.substrate_tech.isolation_properties)

        metal_w = self.width - 2*ledge_width
        metal_l = self.length - 2*ledge_width
        metal_x = np.array([ledge_width, metal_w]) + self.ref_loc[0]
        metal_y = np.array([ledge_width, metal_l]) + self.ref_loc[1]
        metal_z = np.array([0., metal_height]) + self.ref_loc[2]

        metal_material = MaterialProperties(self.entity.substrate_tech.metal_properties)
        metal = Feature(x=metal_x, y=metal_y, z=metal_z,
                        dx=self.dx, dy=self.dy, dz=self.dz,
                        w=metal_w, l=metal_l, h=metal_height,
                        material=metal_material, ref_loc=self.ref_loc)

        self.child_features = [metal]

    def def_substrate_attach(self):
        self.height = self.entity.thickness
        ledge_width = float(self.substrate.ledge_width)
        sub_width, sub_length = self.substrate.dimensions
        self.width = sub_width - 2*ledge_width
        self.length = sub_length - 2*ledge_width

        self.x = np.array([ledge_width, self.width]) + self.ref_loc[0]
        self.y = np.array([ledge_width, self.length]) + self.ref_loc[1]
        self.z = np.array([0., self.height]) + self.ref_loc[2]

        self.material = MaterialProperties(self.entity.attach_tech.properties)

    def def_trace(self):
        self.height = self.substrate.substrate_tech.metal_thickness
        ledge_width = float(self.substrate.ledge_width)
        left = self.entity.left
        right = self.entity.right
        bottom = self.entity.bottom
        top = self.entity.top
        self.width = right - left
        self.length = top - bottom

        self.x = np.array([0., self.width]) + self.ref_loc[0] + left
        self.y = np.array([0., self.length]) + self.ref_loc[1] + bottom
        self.z = np.array([0., self.height]) + self.ref_loc[2]

        self.material = MaterialProperties(self.substrate.substrate_tech.metal_properties)

    def to_dict(self):
        # print self.name, self.material
        x = self.x * 1e3
        y = self.y * 1e3
        z = self.z * 1e3

        print self.name, x.tolist(), y.tolist(), z.tolist()

        feature_output = {'name': self.name,
                          'x': x.tolist(), 'y': y.tolist(), 'z': z.tolist(),
                          'dz': self.dz, 'dy': self.dy, 'dx': self.dx,
                          'Q': self.power, 'Matl': self.material.properties_dictionary['name']}
        '''
        feature_output = {'name': self.name,
                          'x': matlab.double([self.x[0], self.x[1]]),
                          'y': matlab.double([self.x[0], self.x[1]]),
                          'z': matlab.double([self.x[0], self.x[1]]),
                          'dz': self.dz, 'dy': self.dy, 'dx': self.dx,
                          'Q': self.power, 'Matl': self.material.properties_dictionary['name']}
        '''
        return feature_output


class MaterialProperties(object):
    def __init__(self, properties):
        self.properties_dictionary = vars(properties)
        '''
        for key, value in self.properties_dictionary.iteritems():
            setattr(self, key, value)
        '''


class ExternalConditions(object):
    def __init__(self, Ta=20., hbot=100., Tproc=280.):
        self.h_Left = 0.
        self.h_Right = 0.
        self.h_Front = 0.
        self.h_Back = 0.
        self.h_Bottom = hbot
        self.h_Top = 0.
        self.Ta_Left = Ta
        self.Ta_Right = Ta
        self.Ta_Front = Ta
        self.Ta_Back = Ta
        self.Ta_Bottom = Ta
        self.Ta_Top = Ta
        self.Tproc = Tproc

    def to_dict(self):
        return self.__dict__


class Params(object):
    def __init__(self):
        self.Tsteps = []
        self.DeltaT = 1
        self.Tinit = 20.

    def to_dict(self):
        return self.__dict__


class ParaPowerWrapper(object):
    def __init__(self, module_design):
        self.module_design = module_design
        self.device_id = self.module_design.dv_id
        self.ref_locs = self.get_ref_locs()
        self.t_amb = self.module_design.sym_layout.module.ambient_temp
        self.external_conditions = ExternalConditions(Ta=self.t_amb)
        self.parameters = Params()
        self.features_list = self.get_features()
        self.features = [feature.to_dict() for feature in self.features_list]

        self.parapower = ParaPower(self.external_conditions.to_dict(),
                                   self.parameters.to_dict(),
                                   self.features)
        # self.output = PPEncoder().encode(self.parapower)
        # self.write_md_output()

    def get_ref_locs(self):
        baseplate_w, baseplate_l, baseplate_h = self.module_design.baseplate.dimensions
        substrate_attach_h = self.module_design.substrate_attach.thickness
        substrate_metal_h = self.module_design.substrate.substrate_tech.metal_thickness
        substrate_isolation_h = self.module_design.substrate.substrate_tech.isolation_thickness
        trace_h = substrate_metal_h

        baseplate_z = 0.
        substrate_attach_z = baseplate_z + baseplate_h
        substrate_metal_z = substrate_attach_z + substrate_attach_h
        substrate_isolation_z = substrate_metal_z + substrate_metal_h
        trace_z = substrate_isolation_z + substrate_isolation_h
        die_attach_z = trace_z + trace_h

        sub_w, sub_l = self.module_design.substrate.dimensions
        offset_x = (baseplate_w - sub_w) / 2.0
        offset_y = (baseplate_l - sub_l) / 2.0

        ref_locs = {'baseplate': [0., 0., baseplate_z],
                    'substrate_attach': [offset_x, offset_y, substrate_attach_z],
                    'substrate': [offset_x, offset_y, substrate_metal_z],
                    'traces': [offset_x, offset_y, trace_z],
                    'devices': [offset_x, offset_y, die_attach_z]}
        for loc in ref_locs:
            print loc, ref_locs[loc]
        return ref_locs

    def get_features(self):
        features = []
        features_1 = []
        features_2 = []
        features_3 = []
        baseplate = self.module_design.baseplate
        substrate_attach = self.module_design.substrate_attach
        substrate = self.module_design.substrate
        traces = self.module_design.traces
        devices = self.module_design.devices

        # Baseplate
        baseplate_f = Feature(entity=baseplate, ref_loc=self.ref_locs['baseplate'], dx=1, dy=1, dz=1)
        baseplate_f.name = 'Baseplate'
        features_1.append(baseplate_f)
        self.external_conditions.h_Bottom = baseplate_f.h_val

        # Substrate Attach
        substrate_attach_f = Feature(entity=substrate_attach,
                                     ref_loc=self.ref_locs['substrate_attach'], substrate=substrate)
        substrate_attach_f.name = 'Substrate_Attach'
        features_1.append(substrate_attach_f)

        # Substrate
        substrate_f = Feature(entity=substrate, ref_loc=self.ref_locs['substrate'])
        substrate_f.name = 'Substrate_Isolation'
        features_2.append(substrate_f)
        if substrate_f.child_features:
            for child in substrate_f.child_features:
                child.name = 'Substrate_Backside_Metal'
                features_1.append(child)

        # Traces
        for i in range(len(traces)):
            trace_f = Feature(entity=traces[i], ref_loc=self.ref_locs['traces'], substrate=substrate)
            trace_f.name = 'Trace_' + str(i)
            features_2.append(trace_f)
        '''
        for trace in traces:
            features.append(Feature(entity=trace, ref_loc=self.ref_locs['traces'], substrate=substrate))
        '''

        # Devices
        '''
        for device in devices:
            device_instance = Feature(entity=device, ref_loc=self.ref_locs['devices'])
        '''
        for i in range(len(devices)):
            device_instance = Feature(entity=devices[i], ref_loc=self.ref_locs['devices'], dx=3, dy=3, dz=2)
            device_instance.name = self.device_id[i]
            if device_instance.child_features:
                for child in device_instance.child_features:
                    child.name = device_instance.name + "_Attach"
                    features_2.append(child)
            features_3.append(device_instance)

        features_2.extend(features_3)
        features_1.extend(features_2)
        features_1.reverse()
        return features_1

    def write_md_output(self):
        filename = 'PPExportTestMD.p'
        pickle.dump(self.module_design, open(filename, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)


class FeaturesClass(object):
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class ParaPower(object):
    def __init__(self, external_conditions=None, parameters=None, features=None,
                 matlab_path='C:/Users/tmevans/Documents/MATLAB/ParaPower/ARL_ParaPower/ARL_ParaPower'):
        self.ExternalConditions = external_conditions
        self.Params = parameters
        self.Features = features
        self.PottingMaterial = 0
        self.temperature = None
        self.path = matlab_path
        #self.eng = self.init_matlab()

    def to_dict(self):
        model_dict = {'ExternalConditions': self.ExternalConditions,
                      'Params': self.Params,
                      'Features': self.Features,
                      'PottingMaterial': self.PottingMaterial}
        return model_dict

    def init_matlab(self):
        eng = matlab.engine.start_matlab()
        eng.cd(self.path)
        return eng

    def run_parapower_thermal(self, matlab_engine=None):
        if not matlab_engine:
            matlab_engine = self.init_matlab()
            print '=' * 50
            print 'oops, I self-started'
        md_json = json.dumps(self.to_dict())
        temperature = matlab_engine.PowerSynthImport(md_json)
        # self.eng.workspace['test_md'] = self.eng.ImportPSModuleDesign(json.dumps(self.to_dict()), nargout=1)
        # self.eng.save('test_md_file.mat', 'test_md')
        # return temperature + 273.5
        self.save_parapower()
        return temperature

    def save_parapower(self):
        fname = self.path + 'PowerSynth_MD_JSON.json'
        with open(fname, 'w') as outfile:
            json.dump(self.to_dict(), outfile)


def init_matlab(path):
    eng = matlab.engine.start_matlab()
    eng.cd(path)
    return eng


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Rectangle
import matplotlib.cm as cm
from matplotlib.pylab import *


class Coordinates(object):
    def __init__(self, lower_left_coordinate=[0., 0., 0.], width_length_height=[1., 1., 1.]):
        self.location = lower_left_coordinate
        self.dimensions = width_length_height

        if type(self.location) is not np.ndarray:
            self.location = np.array(self.location)

        if type(self.dimensions) is not np.ndarray:
            self.dimensions = np.array(self.dimensions)

        self.location = self.location * 1e3
        self.dimensions = self.dimensions * 1e3
        self.x = self.location[0]
        self.y = self.location[1]
        self.z = self.location[2]

        self.width = self.dimensions[0]
        self.length = self.dimensions[1]
        self.height = width_length_height[2]

        self.center = self.location + (self.dimensions/2.0)
        self.center_x = self.center[0]
        self.center_y = self.center[1]
        self.center_z = self.center[2]

        self.start = self.location
        self.start_x = self.x
        self.start_y = self.y
        self.start_z = self.z

        self.end = self.location + self.dimensions
        self.end_x = self.end[0]
        self.end_y = self.end[1]
        self.end_z = self.end[2]


class Cell(Coordinates):
    def __init__(self, index, xyz, wlh, material_name=None):
        Coordinates.__init__(self, lower_left_coordinate=xyz, width_length_height=wlh)
        self.index = index
        self.material_name = material_name
        self.dx = self.dimensions[0]
        self.dy = self.dimensions[1]
        self.dz = self.dimensions[2]
        self.neighbors = {'left': None, 'right': None, 'front': None, 'back': None, 'bottom': None, 'top': None}

        self.directions = {'left': np.array([-1, 0, 0]), 'right': np.array([1, 0, 0]),
                           'front': np.array([0, -1, 0]), 'back': np.array([0, 1, 0]),
                           'bottom': np.array([0, 0, -1]), 'top': np.array([0, 0, 1])}

        # Convenience variables
        self.sides = ['left', 'right', 'front', 'back', 'bottom', 'top']
        self.opposite_sides = {'left': 'right', 'right': 'left',
                               'front': 'back', 'back': 'front',
                               'bottom': 'top', 'top': 'bottom'}

        # Converting mm to meters and determining lengths, areas
        self.d_xyz = np.array([self.dx, self.dy, self.dz]) #* 1e-3
        # self.area = self.face_areas()
        # self.d = self.cell_half_length()
        # Boundary conditions
        self.h = {'left': None, 'right': None, 'front': None, 'back': None, 'bottom': None, 'top': None}
        self.partial_rth = None
        self.conductivity = None
        self.Q = 0
        self.Ta = None
        self.A = None
        self.B = None
        self.T = None

    def draw_cell(self, ax, edgecolor='gray', cmap=None):
        if self.T == 0.:
            return
        # color = self.material.color
        if cmap:
            color = cmap
        # alpha = self.material.alpha
        alpha = 1
        x = self.start_x
        y = self.start_y
        z = self.start_z
        width = self.width
        length = self.length
        height = self.height
        lw = '0.1'

        left = Rectangle((y, z), length, height, facecolor=color, alpha=alpha, edgecolor=edgecolor, linewidth=lw)
        ax.add_patch(left)
        art3d.pathpatch_2d_to_3d(left, z=x, zdir='x')

        right = Rectangle((y, z), length, height, facecolor=color, alpha=alpha, edgecolor=edgecolor, linewidth=lw)
        ax.add_patch(right)
        art3d.pathpatch_2d_to_3d(right, z=x + width, zdir='x')

        front = Rectangle((x, z), width, height, facecolor=color, alpha=alpha, edgecolor=edgecolor, linewidth=lw)
        ax.add_patch(front)
        art3d.pathpatch_2d_to_3d(front, z=y, zdir='y')

        back = Rectangle((x, z), width, height, facecolor=color, alpha=alpha, edgecolor=edgecolor, linewidth=lw)
        ax.add_patch(back)
        art3d.pathpatch_2d_to_3d(back, z=y + length, zdir='y')

        bottom = Rectangle((x, y), width, length, facecolor=color, alpha=alpha, edgecolor=edgecolor, linewidth=lw)
        ax.add_patch(bottom)
        art3d.pathpatch_2d_to_3d(bottom, z=z, zdir='z')

        top = Rectangle((x, y), width, length, facecolor=color, alpha=alpha, edgecolor=edgecolor, linewidth=lw)
        ax.add_patch(top)
        art3d.pathpatch_2d_to_3d(top, z=z + height, zdir='z')



'''
class BasePlate_v1(object):
    def __init__(self, MDBaseplate):
        self.bp = MDBaseplate
        self.width, self.length, self.height = float(self.bp.dimensions)
        self.startx


class MD_General_v1(object):
    def __init__(self, module_design):
        self.md = module_design

'''


def plot_data_convert(data):
    out = {}
    for name, entry in data.iteritems():
        if type(entry) == matlab.double:
            out[name] = np.array(entry)
        else:
            out[name] = entry
    return out


def make_mesh(plot_data):
    origin = plot_data['origin'][0]
    dx = plot_data['x'][0]
    dy = plot_data['y'][0]
    dz = plot_data['z'][0]

    x = np.concatenate([[0], np.cumsum(dx)[:-1]])
    y = np.concatenate([[0], np.cumsum(dy)[:-1]])
    z = np.concatenate([[0], np.cumsum(dz)[:-1]])

    temp = plot_data['temp'][:, :, :, 1]
    cell_list = []
    index = 0
    print len(x), len(dx)
    for i in range(len(x)):
        for j in range(len(y)):
            for k in range(len(z)):
                temp_cell = Cell(index, [x[i], y[j], z[k]], [dx[i], dy[j], dz[k]])
                temp_cell.T = temp[i, j, k]
                cell_list.append(temp_cell)
                index += 1

    return [x, y, z], [dx, dy, dz], cell_list


def plot_parapower(plot_data):
    pdc = plot_data_convert(plot_data)
    xyz, wlh, cells = make_mesh(pdc)
    # min_val = np.amin(pdc['temp'][:, :, :, 1])
    min_val = 345.
    max_val = np.amax(pdc['temp'][:, :, :, 1])

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')

    my_cmap = cm.get_cmap('jet')  # or any other one
    norm = matplotlib.colors.Normalize(min_val, max_val)  # the color maps work for [0, 1]
    for cell in cells:
        color_i = my_cmap(norm(cell.T))
        cell.draw_cell(ax, cmap=color_i)

    cmmapable = cm.ScalarMappable(norm, my_cmap)
    cmmapable.set_array(range(int(min_val), int(max_val)))
    plt.colorbar(cmmapable)
    ax.set_xlim(-5, 65)
    ax.set_ylim(-5, 65)
    ax.set_zlim(-1, 10)
    ax.view_init(elev=90, azim=90)
    plt.show()

'''
matlab_path = 'C:/Users/tmevans/Documents/MATLAB/ParaPower/ARL_ParaPower/ARL_ParaPower'
eng = init_matlab(matlab_path)
plotdata = eng.PreparePlotData()
pdc = plot_data_convert(plotdata)
xyz, wlh, cells = make_mesh(pdc)

plot_parapower(plotdata)
'''
if __name__ == '__main__':
    pass



