from powercad.general.data_struct.Tree import *
from collections import OrderedDict
import warnings
warnings.filterwarnings("ignore")


class EHier():

    # Convert the E module design to hierachy tree representation
    def __init__(self, module):
        self.module = module
        self.tree = Tree()
        self.isl_group=[]
        self.sheet =[]
        self.isl_group_data= OrderedDict()
    # Form tree based on sheet + plate intersection
    def __del__(self):
        self.isl_group_data.clear()
        del self.module
        del self.sheet
        del self.isl_group
        self.tree.__del__()
    def form_hierachy(self):
        for isl in self.module.group:
            self.isl_node = T_Node(name = 'isl_'+str(isl),type='isl',tree=self.tree)
            self.tree.root.add_child(self.isl_node)
            self.isl_group.append(self.isl_node)
            if self.module.layer_stack!=None:
                layer_id = self.module.group_layer_dict[isl] # GET LAYER ID FOR EACH GROUP
                self.isl_group_data[self.isl_node]={'thick': self.module.layer_stack.thick[layer_id],'mat':
                    self.module.layer_stack.mat[layer_id]}
            self.isl_node.update_rank()
            for trace in self.module.group[isl]:
                self.trace_node = T_Node(name=trace.name,data=trace,type='plate', tree=self.tree)
                self.isl_node.add_child(self.trace_node)
                self.trace_node.update_rank()
                trace.node=self.trace_node
                for sh in self.module.sheet:
                    self.sh_node = T_Node(name=sh.net, type='sheet', data=sh, tree=self.tree)
                    sh.node = self.sh_node
                    if trace.include_sheet(sh):
                        self.trace_node.add_child(self.sh_node)
                        self.sh_node.update_rank()
                        self.sheet.append(self.sh_node)

        # Test plot of the hierarchy
        self.tree.print_tree()
