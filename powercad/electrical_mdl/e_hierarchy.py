from powercad.general.data_struct.Tree import *


class EHier():

    # Convert the E module design to hierachy tree representation
    def __init__(self, module):
        self.module = module
        self.tree = Tree()
        self.isl_group=[]
        self.sheet =[]
        self.isl_group_data={}
    # Form tree based on sheet + plate intersection
    def form_hierachy(self):
        E_module = self.module
        group = E_module.group
        all_sheet = E_module.sheet
        for isl in group:
            self.isl_node = T_Node(name = 'isl_'+str(isl),type='isl',tree=self.tree)
            self.tree.root.add_child(self.isl_node)
            self.isl_group.append(self.isl_node)
            if E_module.layer_stack!=None:
                layer_id = E_module.group_layer_dict[isl] # GET LAYER ID FOR EACH GROUP
                data={}
                data['thick'] = E_module.layer_stack.thick[layer_id]
                data['mat']= E_module.layer_stack.mat[layer_id]
                self.isl_group_data[self.isl_node]=data

            self.isl_node.update_rank()
            for trace in group[isl]:
                self.trace_node = T_Node(name=trace.name,data=trace,type='plate', tree=self.tree)
                self.isl_node.add_child(self.trace_node)
                self.trace_node.update_rank()
                trace.node=self.trace_node
                for sh in all_sheet:
                    self.sh_node = T_Node(name=sh.net, type='sheet', data=sh, tree=self.tree)
                    sh.node = self.sh_node
                    if trace.include_sheet(sh):
                        self.trace_node.add_child(self.sh_node)
                        self.sh_node.update_rank()
                        self.sheet.append(self.sh_node)

        # Test plot of the hierarchy
        #self.tree.print_tree()
