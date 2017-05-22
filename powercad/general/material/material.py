'''@author: qmle
This is used by developers only to parse a material libary from Ansys and generate a .csv database for PowerSynth
'''
from powercad.design.library_structures import MaterialProperties
import csv
import re
class Material_lib:
    def __init__(self):
        self.mat_lib=[]

    def load_q3d(self,fdir):
        '''
        Read the *.amat libary from q3d, only take simple format file, all other material are neglected
        :param fdir:
        :return: list of material properties in PowerSynth using material properties class
        '''
        if fdir.endswith('.amat'):
            file=open(fdir,'rb')
        else:
            print "wrong file format"
            return
        file_data = file.readlines()
        print file_data
        check=[]
        for line in file_data:
            line=line.strip('\n').strip('\r')
            if "$begin" in line:
                # start to record a mateial
                check.append(1)
                line=line.split(' ',1)
                if line[0]=='$begin':
                    material = MaterialProperties()
                    if not ("base_index" in line[1]) and not ("$index$" in line[1]):
                        # save material name and id
                        material.name=line[1].strip("'")
                        material.id=material.name

                '''Thermal Constant'''
            elif "thermal_conductivity" in line and 'simple' in line:
                start=line.find('thermal_conductivity')+len('thermal_conductivity')+3
                stop=len(line)-1
                material.thermal_cond=float(line[start:stop])
            elif "specific_heat" in line and 'simple' in line:
                start=line.find('specific_heat')+len('specific_heat')+3
                stop=len(line)-1
                material.spec_heat_cap=float(line[start:stop])
                ''' Mechanical Constant'''
            elif "mass_density" in line and 'simple' in line:
                start = line.find('mass_density') + len('mass_density') + 3
                stop = len(line) - 1
                material.density = float(line[start:stop])
            elif "youngs_modulus" in line and 'simple' in line:
                start = line.find('youngs_modulus') + len('youngs_modulus') + 3
                stop = len(line) - 1
                material.young_mdl = float(line[start:stop])
            elif "poissons_ratio" in line and 'simple' in line:
                start = line.find('poissons_ratio') + len('poissons_ratio') + 3
                stop = len(line) - 1
                material.poi_rat = float(line[start:stop])
            elif "thermal_expansion_coeffcient" in line and 'simple' in line:
                start = line.find('thermal_expansion_coeffcient') + len('thermal_expansion_coeffcient') + 3
                stop = len(line) - 1
                material.expansion_coeff = float(line[start:stop])

                '''Electrical Constant'''
            elif "permittivity" in line and 'simple' in line:
                start=line.find('permittivity')+len('permittivity')+3
                stop=len(line)-1
                material.rel_permit=float(line[start:stop])
            elif "permeability" in line and 'simple' in line:
                start=line.find('permeability')+len('permeability')+3
                stop=len(line)-1
                material.rel_permeab=float(line[start:stop])
            elif "conductivity" in line and 'simple' in line and not('thermal_conductivity') in line:
                start=line.find('conductivity')+len('conductivity')+3
                stop=len(line)-1
                material.electrical_res=1/float(line[start:stop])

            elif "$end" in line:
                check.pop()
                if check == []:
                    self.mat_lib.append(material)

    def load_csv(self,fname=None):
        '''
        Load the material list from csv file
        :param fname:
        :return:
        '''
        if self.mat_lib==[]:
            print 'loading material from csv'
        else:
            self.mat_lib=[]
            print 'overwrite material list'
        with open(fname) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                material=MaterialProperties(name=row['name'],thermal_cond=row['thermal_cond'],spec_heat_cap=row['spec_heat_cap'],density=row['density']
                                            ,electrical_res=row['electrical_res'],rel_permit=row['rel_permit'],rel_permeab=row['rel_permeab'],id=row['q3d_id'],young_modulus=row['young_modulus']
                                            ,poissons_ratios=row['poissons_ratios'],thermal_expansion_coeffcient=row['thermal_expansion_coeffcient'])
                self.mat_lib.append(material)
            print self.mat_lib

    def save_csv(self,fname=None):
        '''
        Save the material list to csv file, if added material is already existed, it is updated
        :param fname:
        :return:
        '''
        with open(fname, 'wb') as csvfile:
            header=['name', 'thermal_cond', 'spec_heat_cap', 'density',
                     'electrical_res', 'rel_permit', 'rel_permeab','q3d_id', 'young_modulus','poissons_ratios'
                     ,'thermal_expansion_coeffcient']
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for material in self.mat_lib:

                data={'name':None, 'thermal_cond':None, 'spec_heat_cap':None, 'density':None,
                     'electrical_res':None, 'rel_permit':None, 'rel_permeab':None,'q3d_id':None, 'young_modulus':None,'poissons_ratios':None
                     ,'thermal_expansion_coeffcient':None}
                data['name']=material.name
                data['q3d_id']=material.id
                data['thermal_cond']=material.thermal_cond
                data['spec_heat_cap']=material.spec_heat_cap
                data['density']=material.density
                data['electrical_res']=material.electrical_res
                data['rel_permit']=material.rel_permit
                data['rel_permeab']=material.rel_permeab
                data['young_modulus']=material.young_mdl
                data['poissons_ratios']=material.poi_rat
                data['thermal_expansion_coeffcient']=material.expansion_coeff
                if material.name!=None:
                    writer.writerow(data)

    def add_mat(self,material):
        '''
        Add new row in material list
        :return:
        '''
        self.mat_lib.append(material)
        print "add one material to the list:", material.name

    def remove_mat(self,mat_name):
        '''
        Remove a material by its name
        :param mat_name: a string reprent mateial name
        :return:
        '''
        if self.mat_lib!=[]:
            id=0
            for material in self.mat_lib:
                if material.name==mat_name:
                    self.mat_lib.pop(id)
                else:
                    id+=1

    def get_mat(self,mat_name):
        '''
        Get a material from lib by its name
        :param mat_name:
        :return: material properties object
        '''
        if self.mat_lib != []:
            for material in self.mat_lib:
                if material.name == mat_name:
                    return material

if __name__ == "__main__":
    ML=Material_lib()
    csv_dir='C://Users//Quang//Google Drive//MSCAD PowerSynth Archives//Internal//MDK//Layer Stack Quang//Materials.csv'
    ML.load_q3d('C://Users//Quang//Google Drive//MSCAD PowerSynth Archives//Internal//MDK//Layer Stack Quang//Materials.amat')
    ML.save_csv(csv_dir)
    ML.load_csv(csv_dir)
    new_mat=MaterialProperties(name='Pb_Sn solder',thermal_cond=35.8,spec_heat_cap=130,density=11020,id='Pb_Sn solder')
    ML.add_mat(new_mat)
    ML.save_csv(csv_dir)