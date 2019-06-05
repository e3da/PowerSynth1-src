

class CornerStitchSolution:

    def __init__(self, name='', index=None, params=None):
        """Describes a solution saved from the Solution Browser

        Keyword arguments:
        name -- solution name
        index -- cs solution index
        params -- list of objectives in tuples (name, unit, value)
        layout_info -- dictionary holding layout_info for a solution with key=size of layout
        """
        self.name = name
        self.index = index
        self.params = params
        self.layout_info={}
