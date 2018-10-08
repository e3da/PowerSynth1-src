import subprocess
from time import gmtime, strftime

from math import *
class HSPICE:
    def __init__(self, env,file):
        '''

        :param env: env dir
        :param file: file dir
        '''
        self.file = file
        self.env=env

    def run(self):
        args = [self.env, self.file]
        print args

        p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print stdout,stderr

    def ac_lin(self, fmin, fmax, nump):
        return ".ac lin {0} {1}Hz {2}Hz".format(nump, fmin, fmax)

    def operatingpoint(self):
        return ".op"
    def write2(self, circuit, frange):
        all_elements = circuit.element
        probe = '.print'
        Kid=0
        with open(self.file, 'w') as f:
            f.write(strftime("* %Y-%m-%d %H:%M:%S", gmtime()) + '\n')
            for e in all_elements:

                if e[0] != 'M':
                    pnode ='n'+ str(circuit.pnode[e])
                    nnode = 'n' + str(circuit.nnode[e])
                    if str(circuit.nnode[e])=='0':
                        nnode ='gnd'
                    value = str(circuit.value[e])
                    if e[0] == 'R':
                        line = [e, pnode, nnode, value]
                    elif e[0] == 'V':
                        line = [e, pnode, nnode, 'DC','0','AC', value]
                    elif e[0] == 'L':
                        line = [e, pnode, nnode, value]
                        probe+= ' I('+e+')'
                    elif e[0] == 'C':
                        line = [e, pnode, nnode, value + 'F']
                    line = " ".join(line)
                    line += '\n'
                    f.write(line)
                else:
                    Lname1 = circuit.Lname1[e]
                    Lname2 = circuit.Lname2[e]
                    Lval1=circuit.value[Lname1]
                    Lval2 = circuit.value[Lname2]
                    Mval = circuit.value[e]
                    kname = 'K'+ str(Kid)
                    Kid+=1
                    value = Mval/sqrt(Lval1*Lval2)
                    #print "netlist",Mval,Lname1,Lname2
                    line = [kname, Lname1, Lname2, str(value)]
                    line = " ".join(line)
                    line += '\n'
                    f.write(line)

            # write ac sim
            if frange[0]>=1000:
                sim_line = self.ac_lin(fmin=frange[0], fmax=frange[1], nump=1)
            else:
                sim_line = self.operatingpoint()
            line = sim_line + '\n'

            f.write(line)
            f.write('.option post=1\n')
            #f.write('.measure v(n1)\n')
            #probe+='\n'
            #f.write(probe)
            #f.write('.Print V(1) V(2) I(L1) I(L2) I(vs)\n')
            # end line:
            f.write('.end\n')



