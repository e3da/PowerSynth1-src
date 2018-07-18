DEFAULT_FUNCTIONS=['max()','min()','abs()','avg()','std_dev()','sqrt()']
import parser
import re
class CostFunction():
    def __init__(self,name, formula,numvar):
        '''
        :param type: default types
        :param inpt_var: list of varialbe from interface
        '''
        self.name=name
        self.formula=formula
        self.numvar=numvar
        self.var=[]
        self.var_id=[]
        self.units='no unit assigned yet-- to be updated'
        self.measure=[]
    def validate(self):
        '''
        read the formua in the input and see if the formula is correct
        :return: True or False
        '''
        valid=True
        regex=r'm[0-9]'
        regex_2=r'm[1-9][0-9]'

        v_list=re.findall(regex,self.formula)
        v_list1 = re.findall(regex_2, self.formula)
        v_list+=v_list1
        for var in v_list:
            var_id=int(var[1:])
            self.var_id.append(var_id)
            if var_id>self.numvar:
                valid=False
        if valid:
            self.var_id=list(set(self.var_id))
            self.var=list(set(v_list))
        return valid

    def evalfunc(self,list_of_value):
        try:
            for i in range(len(self.var)):
                variable=str(self.var[i])+'='+str(list_of_value[i])
                print variable
                exec(variable)
                exec('print {0}'.format(self.var[i]))
        except:
            print "fail"
        res=0
        out='res='+self.formula
        exec(out)
        return res
