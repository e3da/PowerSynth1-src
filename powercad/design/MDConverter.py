

class Feature(object):
    def __init__(self, FeatureInstance):
        self.geometry = None
        self.material_properties = None
        self.boundary_conditions = None
        self.FeatureInstance = FeatureInstance

    def get_geometry(self):
        pass


class Geometry(object):
    def __init__(self, xyz_vector, wlh_vector):
        self.xyz = xyz_vector
        self.wlh = wlh_vector


class MaterialProperties(object):
    def __init__(self, properties):
        properties_dictionary = vars(properties)
        for key, value in properties_dictionary.items():
            setattr(self, key, value)

    def toJSON(self):
        return json.dumps(self, default=lambda o: vars(o), sort_keys=True, indent=4)


class BasePlate_v1(object):
    def __init__(self, MDBaseplate):
        self.bp = MDBaseplate
        self.width, self.length, self.height = float(self.bp.dimensions)
        self.startx


class MD_General_v1(object):
    def __init__(self, module_design):
        self.md = module_design


if __name__ == '__main__':
    pass

    # import simplejson as json

    '''
    class MDEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__
    '''
