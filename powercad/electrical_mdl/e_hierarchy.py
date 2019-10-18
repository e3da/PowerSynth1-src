from powercad.general.data_struct.Tree import *
import warnings
warnings.filterwarnings("ignore")


class EHier():
    # Convert the E module design to hierachy tree representation
    def __init__(self, module):
        self.module = module
        self.tree = None
        self.isl_group = []
        self.sheet = []
        self.isl_group_data = {}

    # Form tree based on sheet + plate intersection
    def __del__(self):
        #print "delete hier object"
        del self.isl_group_data
        self.module =None
        for sh in self.sheet:
            sh.__del__()
        del self.sheet
        for isl_node in self.isl_group:
            isl_node.__del__()
        del self.isl_group
        self.tree.__del__()

    def update_module(self,new_module):
        #form new hierarchy.
        self.module=new_module
    def update_hierarchy(self):
        '''
        *THIS DOESNT WORK FOR REU BRANCH NEEDS TO MERGE AND TEST
        Since the hierarchy is the same for all layout, need to update hierarchy data
        :return:
        '''
        print "UPDATING HIERARCHY"
        for isl in self.module.group:
            for trace in self.module.group[isl]:
                trace_node_name = trace.name
                trace_node = self.tree.get_node_by_name(trace_node_name)
                # update trace node data, rank and name should be the same
                trace_node.data = trace
                trace.node =trace_node
                for sh in self.module.sheet:
                    sheet_node_name = sh.net
                    sheet_node = self.tree.get_node_by_name(sheet_node_name)
                    sheet_node.data =sh
                    sh.node = sheet_node


    def form_hierachy(self):
        '''
        Form the hierachy the first time
        :return: update the hierarchy structure
        '''
        self.tree =Tree()
        for isl in self.module.group:
            isl_node = T_Node(name=str(isl), type='isl', tree=self.tree)
            self.tree.root.add_child(isl_node)
            self.isl_group.append(isl_node)
            if self.module.layer_stack != None:
                layer_id = self.module.group_layer_dict[isl]  # GET LAYER ID FOR EACH GROUP
                self.isl_group_data[isl_node] = {'thick': self.module.layer_stack.thick[layer_id], 'mat':
                    self.module.layer_stack.mat[layer_id]}
            isl_node.update_rank()
            for trace in self.module.group[isl]:
                trace_node = T_Node(name=trace.name, data=trace, type='plate', tree=self.tree)
                isl_node.add_child(trace_node)
                trace_node.update_rank()
                trace.node = trace_node
                for sh in self.module.sheet:
                    sh_node = T_Node(name=sh.net, type='sheet', data=sh, tree=self.tree)
                    sh.node = sh_node
                    if trace.include_sheet(sh):
                        trace_node.add_child(sh_node)
                        sh_node.update_rank()
                        self.sheet.append(sh_node)

                        # Test plot of the hierarchy
                        # self.tree.print_tree()
