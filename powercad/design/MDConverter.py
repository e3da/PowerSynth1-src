import sys
import numpy as np
# from simplejson import JSONEncoder
import simplejson as json
import matlab.engine

'''
def toJSON(object):
    if 'simplejson' not in sys.modules:
        import simplejson as json
    return json.dumps(object, default=lambda o: vars(o), sort_keys=True, indent=4)


class PPEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Feature(object):
    def __init__(self, FeatureInstance):
        self.geometry = None
        self.material_properties = None
        self.boundary_conditions = None
        self.FeatureInstance = FeatureInstance

    def get_geometry(self):
        pass
'''


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
    def __init__(self):
        self.h_Left = 0.
        self.h_Right = 0.
        self.h_Front = 0.
        self.h_Back = 0.
        self.h_Bottom = 100.
        self.h_Top = 0.
        self.Ta_Left = 20.
        self.Ta_Right = 20.
        self.Ta_Front = 20.
        self.Ta_Back = 20.
        self.Ta_Bottom = 20.
        self.Ta_Top = 20.
        self.Tproc = 280.

    def to_dict(self):
        return self.__dict__


class Params(object):
    def __init__(self):
        self.Tsteps = 1
        self.DeltaT = 1
        self.Tinit = 20.

    def to_dict(self):
        return self.__dict__


class ParaPowerWrapper(object):
    def __init__(self, module_design):
        self.module_design = module_design
        self.device_id = self.module_design.dv_id
        self.ref_locs = self.get_ref_locs()
        self.external_conditions = ExternalConditions()
        self.parameters = Params()
        self.features_list = self.get_features()
        self.features = [feature.to_dict() for feature in self.features_list]

        self.parapower = ParaPower(self.external_conditions.to_dict(),
                                   self.parameters.to_dict(),
                                   self.features)
        # self.output = PPEncoder().encode(self.parapower)

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
        baseplate = self.module_design.baseplate
        substrate_attach = self.module_design.substrate_attach
        substrate = self.module_design.substrate
        traces = self.module_design.traces
        devices = self.module_design.devices

        # Baseplate
        baseplate_f = Feature(entity=baseplate, ref_loc=self.ref_locs['baseplate'], dx=1, dy=1, dz=1)
        baseplate_f.name = 'Baseplate'
        features.append(baseplate_f)
        self.external_conditions.h_Bottom = baseplate_f.h_val

        # Substrate Attach
        substrate_attach_f = Feature(entity=substrate_attach,
                                     ref_loc=self.ref_locs['substrate_attach'], substrate=substrate)
        substrate_attach_f.name = 'Substrate_Attach'
        features.append(substrate_attach_f)

        # Substrate
        substrate_f = Feature(entity=substrate, ref_loc=self.ref_locs['substrate'])
        substrate_f.name = 'Substrate_Isolation'
        features.append(substrate_f)
        if substrate_f.child_features:
            for child in substrate_f.child_features:
                child.name = 'Substrate_Backside_Metal'
                features.append(child)

        # Traces
        for i in range(len(traces)):
            trace_f = Feature(entity=traces[i], ref_loc=self.ref_locs['traces'], substrate=substrate)
            trace_f.name = 'Trace_' + str(i)
            features.append(trace_f)
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
                    features.append(child)
            features.append(device_instance)

        return features


class FeaturesClass(object):
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class ParaPower(object):
    def __init__(self, external_conditions, parameters, features):
        self.ExternalConditions = external_conditions
        self.Params = parameters
        self.Features = features
        self.PottingMaterial = 0
        self.temperature = None
        self.path = 'C:/Users/tmevans/Documents/MATLAB/ParaPower/ARLParaPower2.0/ARLParaPower/'
        # self.eng = self.init_matlab()

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

    def run_parapower(self):
        #temp = self.eng.ImportTest()
        # self.eng.workspace['test_md'] = self.eng.ImportPSModuleDesign(json.dumps(self.to_dict()), nargout=1)
        # self.eng.save('test_md_file.mat', 'test_md')
        return

    def save_parapower(self):
        fname = self.path + 'Test_MD_JSON.json'
        with open(fname, 'w') as outfile:
            json.dump(self.to_dict(), outfile)




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

if __name__ == '__main__':
    pass

    # import simplejson as json

    '''
    class MDEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__
    '''
