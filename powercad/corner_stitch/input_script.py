

class Parts():
    def __init__(self,name=None,type=None,info_file=None,layout_component_id=None):
        """

        :param name: part name : signal_lead, power_lead, MOS, IGBT, Diode
        :param type: signal_lead:0, power_lead:1, MOS:2, IGBT:3, Diode:4
        :param info_file: technology file for each part
        :param layout_component_id: 1,2,3.... id in the layout information

        """

        self.name=name
        self.type=type
        self.info_file=info_file
        self.layout_component_id=layout_component_id

        