import simplejson as json
import matlab.engine
import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Rectangle
import matplotlib.cm as cm
# from matplotlib.pylab import *
import seaborn as sns


class Params(object):
    """The :class:`Params` object contains attributes that are used in the solver setting of ParaPower.

    **Attributes**

    :ivar Tsteps: A list of time steps to be used in analysis. If the list is empty, static analysis will be performed.
    :type Tsteps: list
    :ivar DeltaT: Time step size.
    :type DeltaT: float
    :ivar Tinit: The initial temperature for the solution setup.
    :type Tinit: float

    """
    def __init__(self):
        self.Tsteps = []
        self.DeltaT = 1
        self.Tinit = 20.

    def to_dict(self):
        """A function to return the attributes of the :class:`Params` object as a dictionary. This dictionary is used
        to generate the JSON text stream in :class:`ParaPowerInterface`.

        :return params_dict: A dictionary of the solver parameters.
        :type params_dict: dict
        """
        return self.__dict__


class Feature(object):
    """A feature definition class containing all of the relevant information from
    a :class:`~PowerSynthStructures.ModuleDesign` object as it pertains to forming a ParaPower model.


    :param entity: The type of entity to be converted. This can be one of either baseplate, substrate_attach, substrate,traces, or devices.
    :type entity: str
    :param ref_loc: Reference location for the geometry.
    :type ref_loc: list of reference coordinates
    :param x: Feature relative x-coordinate.
    :param y: Feature relative y-coordinate.
    :param z: Feature relative z-coordinate.
    :param w: Feature width.
    :param l: Feature length.
    :param h: Feature height.
    :param dx: Feature x-direction meshing discretization.
    :param dy: Feature y-direction meshing discretization.
    :param dz: Feature z-direction meshing discretization.
    :param material: Feature material properties
    :type material: A :class:`~MaterialProperties` object
    :param substrate: Parent substrate if applicable.
    :param power: Heat dissipation to be provided by the feature.
    :param name: Name of the feature.

    """
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


class ParaPowerWrapper(object):
    """The :class:`ParaPowerWrapper` object takes a PowerSynth module design and converts it to features, parameters,
    and external conditions to be used in ParaPower analysis routines.

    A module design is of the form :class:`~PowerSynthStructures.ModuleDesign` and is passed to this wrapper class as
    the parameter module_design. This wrapper class identifies all of the necessary components in a PowerSynth
    :class:`~PowerSynthStructures.ModuleDesign` and runs :func:`get_features` to generate a list of ParaPower compatible
    features. External conditions are set based on the ambient temperature found in
    :class:`~PowerSynthStructures.ModuleDesign`. Parameters used to specify static versus transient analysis and
    desired timesteps can optionally be passed to this wrapper as a :class:`Params` object. The default parameters are
    for static analysis.

    :param  module_design: A PowerSynth module design.
    :type module_design: :class:`~PowerSynthStructures.ModuleDesign`
    :param solution_parameters: Static or transient solver settings (optional, default is static solver settings).
    :type solution_parameters: :class:`Params`
    :return parapower: A ParaPower solution model with external conditions, parameters, and features.
    :rtype parapower: :class:`~ParaPowerInterface`

    """

    def __init__(self, module_design):
        self.module_design = module_design
        self.device_id = self.module_design.dv_id
        self.ref_locs = self.get_ref_locs()
        self.t_amb = self.module_design.sym_layout.module.ambient_temp
        self.external_conditions = ExternalConditions(Ta=self.t_amb)
        self.parameters = Params()
        self.features_list = self.get_features()
        self.features = [feature.to_dict() for feature in self.features_list]

        self.parapower = ParaPowerInterface(self.external_conditions.to_dict(),
                                            self.parameters.to_dict(),
                                            self.features)
        # self.output = PPEncoder().encode(self.parapower)
        # self.write_md_output()

    def get_ref_locs(self):
        """Returns reference locations for each of the following:

        **PowerSynth Components**

        * Baseplate from :class:`~PowerSynthStructures.BaseplateInstance`
        * Substrate Attach  from :class:`~PowerSynthStructures.SubstrateAttachInstance`
        * Substrate from :class:`~PowerSynthStructures.SubstrateInstance`
        * Traces from :class:`~PowerSynthStructures.SubstrateInstance`
        * Devices from :class:`~PowerSynthStructures.DeviceInstance`


        :return ref_locs: Reference locations for each of the PowerSynth structures listed above.
        :rtype: dict
        """

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
        """A function that returns all of the relevant features necessary for a ParaPower analysis run from the
        :class:`~PowerSynthStructures.ModuleDesign` object as a list.

        :return features: A list of features for ParaPower.
        :rtype features: list of :class:`Feature` objects
        """

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


class FeaturesClassDict(object):
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class ParaPowerInterface(object):
    """The main interface between ParaPower and PowerSynth.

    This class accepts external conditions, parameters, and all of the features that have been previously converted from
    a :class:`~PowerSynthStructures.ModuleDesign` object. Additionally, given a path to the MATLAB workspace containing
    ParaPower, the function :func:`~run_parapower_thermal` sends the necessary information to the receiving script in
    MATLAB and will run a ParaPower analysis before returning temperature results.


    :param external_conditions: External conditions for the ParaPower solver
    :type external_conditions: dict of :class:`~ExternalConditions`
    :param parameters: ParaPower solver parameters
    :type parameters: dict of :class:`~Params`
    :param features: All of the features to be included from a :class:`~PowerSynthStructures.ModuleDesign` object.
    :param matlab_path: dict of :class:`~Feature`

    """
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
        """Converts all of the external conditions, parameters, features, and potting material to a dictionary.
        This dictionary is then converted to a JSON text stream in :func:`~run_parapower_thermal`.

        :return model_dict: A dictionary collection of the ParaPower model.
        :rtype model_dict: dict
        """
        model_dict = {'ExternalConditions': self.ExternalConditions,
                      'Params': self.Params,
                      'Features': self.Features,
                      'PottingMaterial': self.PottingMaterial}
        return model_dict

    def init_matlab(self):
        """Initializes the MATLAB for Python engine and starts it in the working directory specified in the path
        attribute.

        :return eng: An instance of the MATLAB engine.
        """
        eng = matlab.engine.start_matlab()
        eng.cd(self.path)
        return eng

    def run_parapower_thermal(self, matlab_engine=None, visualize=False):
        """Executes the ParaPower thermal analysis on the given PowerSynth design and returns temperature results.

        This function accepts a currently running MATLAB engine or defaults to instantiating its own. All of the
        relevant structures necessary to run the ParaPower thermal analysis are first converted to a JSON text stream.
        Next this information is sent to the receiving MATLAB script, **ImportPSModuleDesign.m**, where a ParaPower
        model is formed and evaluated. Currently, the maximum temperature is returned to be used in PowerSynth
        optimization.

        If this function is being called outside of the optimization routine, the visualize flag can be set to 1 to
        invoke ParaPower's visualization routines.

        :param matlab_engine: Instance of a running MATLAB engine.
        :param visualize: Flag for turning on or off visualization. The default is 0 for off.
        :type visualize: int (0 or 1)
        :return temperature: The maximum temperature result from ParaPower thermal analysis.
        :rtype temperature: float
        """
        if not matlab_engine:
            matlab_engine = self.init_matlab()
        md_json = json.dumps(self.to_dict())
        temperature = matlab_engine.PowerSynthImport(md_json, visualize)
        # self.eng.workspace['test_md'] = self.eng.ImportPSModuleDesign(json.dumps(self.to_dict()), nargout=1)
        # self.eng.save('test_md_file.mat', 'test_md')
        # return temperature + 273.5
        self.save_parapower()
        return temperature

    def save_parapower(self):
        """Saves the current JSON text stream so that it can be analyzed later. This is only used for debugging right
        now.

        :return: None
        """
        fname = self.path + 'PowerSynth_MD_JSON.json'
        with open(fname, 'w') as outfile:
            json.dump(self.to_dict(), outfile)


def init_matlab(path):
    eng = matlab.engine.start_matlab()
    eng.cd(path)
    return eng

# The following classes and methods are currently only used for visualization testing in Python
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


class ParaPowerData(object):
    def __init__(self, data):
        """
        Gathers data from MATLAB via PreparePlotData.m and converts MATLAB arrays into Numpy ones.
        Current data structure includes:
        - x, y, z: coordinate arrays
        - origin: coordinate array
        - model: A 3D matrix containing integers at each location specifying material
        - temp: A 3D matrix holding temperature results
        - materials: A list of all materials, referenced by their index in 'model'. Note: This uses MATLAB indexing!
        :param data: Data from PreparePlotData.m
        :type data: Dictionary
        """
        self.x = None
        self.y = None
        self.z = None
        self.origin = None
        self.model = None
        self.temp = None
        self.materials = None
        self.material_lookup = {}

        # Read in data and set attributes. Convert numpy arrays to MATLAB ones as necessary
        for name, entry in data.iteritems():
            if type(entry) == matlab.double:
                setattr(self, name, np.array(entry))
            else:
                setattr(self, name, entry)

        # Make a dictionary of materials with keys corresponding to values in self.model
        for index, material in enumerate(self.materials, 1):
            self.material_lookup[index] = material


    def make_mesh(self, plot_data):
        origin = self.origin[0]
        dx = self.x[0]
        dy = self.y[0]
        dz = self.z[0]

        x = np.concatenate([[0], np.cumsum(dx)[:-1]])
        y = np.concatenate([[0], np.cumsum(dy)[:-1]])
        z = np.concatenate([[0], np.cumsum(dz)[:-1]])

        temp = self.temp[:, :, :, 1]
        cell_list = []
        index = 0
        print len(x), len(dx)
        for i in range(len(x)):
            for j in range(len(y)):
                for k in range(len(z)):
                    temp_cell = Cell(index, [x[i], y[j], z[k]], [dx[i], dy[j], dz[k]])
                    temp_cell.T = temp[i, j, k]
                    temp_cell.material_name = self.material_lookup[self.model[i, j, k]]
                    cell_list.append(temp_cell)
                    index += 1

        return [x, y, z], [dx, dy, dz], cell_list



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

    x = np.concatenate([[origin[0]], np.cumsum(dx)])
    y = np.concatenate([[origin[1]], np.cumsum(dy)])
    z = np.concatenate([[origin[2]], np.cumsum(dz)])

    temp = plot_data['temp'][:, :, :, 1]
    '''
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
    '''
    return [x, y, z], [dx, dy, dz] # cell_list


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
    norm = plt.colors.Normalize(min_val, max_val)  # the color maps work for [0, 1]
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


def plot_parapower_2d(plot_data, min_val=345, max_layer=5):
    pdc = plot_data_convert(plot_data)
    xyz, wlh = make_mesh(pdc)
    # min_val = np.amin(pdc['temp'][:, :, :, 1])
    temp = pdc['temp'][:, :, :, 1]
    min_val = min_val
    max_val = np.amax(pdc['temp'][:, :, :, 1])
    X, Y = np.meshgrid(xyz[0], xyz[1])

    fig, ax = plt.subplots()

    my_cmap = cm.get_cmap('jet')  # or any other one
    norm = plt.colors.Normalize(min_val, max_val)  # the color maps work for [0, 1]
    for i in range(max_layer):
        temp_i = temp[:, :, i]
        temp_i_ma = np.ma.masked_where(temp_i == 0, temp_i)
        ax.pcolormesh(X, Y, temp_i_ma.T, cmap=my_cmap)

    cmmapable = cm.ScalarMappable(norm, my_cmap)
    cmmapable.set_array(range(int(min_val), int(max_val)))
    plt.colorbar(cmmapable)

    plt.show()


def plot_parapower_2d_mats(plot_data, max_layer=5):
    pdc = plot_data_convert(plot_data)
    xyz, wlh = make_mesh(pdc)
    # min_val = np.amin(pdc['temp'][:, :, :, 1])
    mat_labels = np.unique(pdc['model'])
    materials = pdc['materials']
    print materials.shape
    material_lookup = {}
    for index, material in enumerate(materials, 1):
        material_lookup[index] = material

    rgb_values = sns.color_palette("Set2", len(mat_labels))
    color_map = dict(zip(mat_labels, rgb_values))


    X, Y = np.meshgrid(xyz[0], xyz[1])

    fig, ax = plt.subplots()

    for i in range(max_layer):
        mat_i = materials[:, :, i]
        mat_i_ma = np.ma.masked_where(mat_i == 0, mat_i)
        ax.pcolormesh(X, Y, mat_i_ma.T, cmap=color_map)


    plt.show()
'''
matlab_path = 'C:/Users/tmevans/Documents/MATLAB/ParaPower/ARL_ParaPower/ARL_ParaPower'
eng = init_matlab(matlab_path)
plotdata = eng.PreparePlotData()
ppd = ParaPowerData(plotdata)
pdc = plot_data_convert(plotdata)
# xyz, wlh, cells = make_mesh(pdc)

# plot_parapower(plotdata)
plot_parapower_2d(plotdata, max_layer=4)
plot_parapower_2d_mats(plotdata)
'''

if __name__ == '__main__':
    pass



