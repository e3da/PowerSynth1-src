from powercad.general.data_struct.Tree import *


class Hier_E():
    # Convert the E module design to hierachy tree representation
    def __init__(self, module):
        self.module = module
        self.tree = Tree()
        self.isl_group=[]
        self.sheet =[]
    # Form tree based on sheet + plate intersection
    def form_hierachy(self):
        E_module = self.module
        group = E_module.group
        all_sheet = E_module.sheet
        for isl in group:
            isl_node = T_Node(name = 'isl_'+str(isl),type='isl',tree=self.tree)
            self.tree.root.add_child(isl_node)
            self.isl_group.append(isl_node)
            isl_node.update_rank()
            for trace in group[isl]:
                trace_node = T_Node(name=trace.name,data=trace,type='plate', tree=self.tree)
                isl_node.add_child(trace_node)
                trace_node.update_rank()
                for sh in all_sheet:
                    if trace.include_sheet(sh):
                        sh_node =T_Node(name=sh.net,type='sheet',data=sh, tree=self.tree)
                        trace_node.add_child(sh_node)
                        sh_node.update_rank()
                        self.sheet.append(sh_node)