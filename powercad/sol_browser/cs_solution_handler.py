from powercad.corner_stitch.cs_solution import CornerStitchSolution
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import glob

def pareto_solutions(solutions):
    all_data={}
    pareto_data={}
    solutions.sort(key=lambda x: x.index, reverse=False)
    for solution in solutions:
        keys=solution.params.keys()

    for key in keys:
        pareto_data.setdefault(key,[])

    for solution in solutions:
        ret=[]
        key=solution.index
        for k,v in solution.params.items():
            ret.append(v)
        all_data[key]=ret
    pareto_front=pareto_frontiter2D(data_in=all_data)
    return pareto_front

def pareto_frontiter2D(data_in=None, MinX=True, MinY=True):
        '''

        :param data: nx2 nd array for the data [f1,f2]
        :param MinX: If find minX
        :param MinY: If find minY
        :return: pareto frontier
        '''
        # Display only the pareto front solution
        # ID=data[:, 0].tolist()
        data_1 = data_in.values()
        data=np.array(data_1)
        X = data[:, 0].tolist()
        Y = data[:, 1].tolist()

        raw_list = [[X[i], Y[i]] for i in range(len(X))]
        data_list = sorted(raw_list, reverse=not (MinX))
        p_front = [data_list[0]]
        for pair in data_list[1:]:
            if MinY:
                if pair[1] <= p_front[-1][1]:  # Look for higher values of Y
                    p_front.append(pair)  # and add them to the Pareto frontier

            else:
                if pair[1] >= p_front[-1][1]:  # Look for lower values of Y
                    p_front.append(pair)  # and add them to the Pareto frontie

        #print "No of Solutions on Pareto-front", len(p_front)
        #print "Total solutions", len(data_1)
        pareto_data = np.array(p_front)

        plot = False
        if plot:

            plt.scatter(pareto_data[:, 0], pareto_data[:, 1])
            plt.show()
        p_data = {}
        for k,v in data_in.items():

            if v in p_front:
                p_data[k]=v

        return p_data


def export_solutions(solutions=None,directory=None,pareto_data=None):
    sol_path = directory + '/Layout_Solutions'
    if pareto_data!=None:
        pareto_path = directory + '/Pareto_Solutions'
    if not os.path.exists(sol_path):
        os.makedirs(sol_path)

    if len(solutions) > 1000:
        print "Thousands of csv files are going to be generated"

    # export to eagle format
    for i in range(len(solutions)):
        item = solutions[i].name
        file_name = sol_path + '/' + item + '.txt'
        with open(file_name, 'wb') as my_file:
            for k, v in solutions[i].abstract_info[item]['rect_info'].items():
                if k[0]=='T' :
                    x1=v.x/1000.0
                    x2=(v.x+v.width)/1000.0
                    y1=v.y/1000.0
                    y2=(v.y+v.height)/1000.0
                    print >> my_file, '<rectangle x1="{}" y1="{}" x2="{}" y2="{}" layer="1"/>'.format(str(x1),str(y1),str(x2),str(y2))
            for k, v in solutions[i].abstract_info[item]['rect_info'].items():
                if k=='Substrate':
                    x1 = v.x / 1000.0
                    x2 = (v.x + v.width) / 1000.0
                    y1 = v.y / 1000.0
                    y2 = (v.y + v.height) / 1000.0
                    print >> my_file, '<rectangle x1="{}" y1="{}" x2="{}" y2="{}" layer="16"/>'.format(str(x1), str(y1),str(x2), str(y2))
                    break



        my_file.close()

    params=solutions[0].params
    performance_names=params.keys()
    #print"perf_names",performance_names
    for i in range(len(solutions)):
        item = solutions[i].name
        file_name = sol_path + '/' + item + '.csv'
        with open(file_name, 'wb') as my_csv:
            csv_writer = csv.writer(my_csv, delimiter=',')
            csv_writer.writerow(["Size", performance_names[0], performance_names[1]])
            # for k, v in _fetch_currencies.iteritems():
            Size = solutions[i].abstract_info[item]['Dims']
            Perf_1 = solutions[i].params[performance_names[0]]
            Perf_2 =  solutions[i].params[performance_names[1]]
            data = [Size, Perf_1, Perf_2]
            csv_writer.writerow(data)
            csv_writer.writerow(["Component_Name", "x_coordinate", "y_coordinate", "width", "length"])
            for k, v in solutions[i].abstract_info[item]['rect_info'].items():
                layout_data = [k, v.x, v.y, v.width, v.height]
                csv_writer.writerow(layout_data)
        my_csv.close()

    if pareto_data!=None:
        if not os.path.exists(pareto_path):
            # print "path doesn't exist. trying to make"
            os.makedirs(pareto_path)
        for i in range(len(solutions)):
            if solutions[i].index in pareto_data.keys():
                item = solutions[i].name
                file_name = pareto_path + '/' + item + '.csv'
                with open(file_name, 'wb') as my_csv:
                    csv_writer = csv.writer(my_csv, delimiter=',')
                    csv_writer.writerow(["Size", performance_names[0], performance_names[1]])
                    # for k, v in _fetch_currencies.iteritems():
                    Size = solutions[i].abstract_info[item]['Dims']
                    Perf_1 = solutions[i].params[performance_names[0]]
                    Perf_2 = solutions[i].params[performance_names[1]]
                    data = [Size, Perf_1, Perf_2]
                    csv_writer.writerow(data)
                    csv_writer.writerow(["Component_Name", "x_coordinate", "y_coordinate", "width", "length"])
                    for k, v in solutions[i].abstract_info[item]['rect_info'].items():
                        layout_data = [k, v.x, v.y, v.width, v.height]
                        csv_writer.writerow(layout_data)
                my_csv.close()


def plot_solutions(file_location=None):
    '''

    :param file: a csv file that has solution information. Will read the line where size, inductance, and temp is available
    :return:
    '''
    files = glob.glob(file_location+'/'+'*.csv')
    all_data={}
    for file in files:

        head, tail = os.path.split(file)
        name=tail.strip('.csv')
        data={}
        with open(file) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if row[0]=='Size':
                    print row
                    key1=row[1]
                    key2=row[2]
                    key3=row[0]
                    continue
                if row[0]=='Component_Name':
                    break
                else:
                    #print row[0],row[1],row[2]

                    data[key1]=(float(row[1])) # inductance (nH)
                    data[key2]=(float(row[2])) # Temperature (K)
                    data[key3]=(row[0]) # size [w,h]
            all_data[name]=data
    print all_data
    file_name = head + '/' + 'plot_data' + '.csv'
    with open(file_name, 'wb') as my_csv:
        csv_writer = csv.writer(my_csv, delimiter=',')
        for k, v in all_data.items():
            keys = v.keys()
            csv_writer.writerow(["Layout_ID", keys[0],keys[1],keys[2]])
            break
    my_csv.close()

    with open(file_name, 'a') as my_csv:
        csv_writer = csv.writer(my_csv, lineterminator='\n')
        #csv_writer = csv.writer(my_csv, delimiter=',')
        for k, v in all_data.items():
            keys = v.keys()
            val=v.values()
            data=[k,val[0],val[1],val[2]]

            csv_writer.writerow(data)
    my_csv.close()



    '''
    x=[]
    y=[]
    z=[]
    for k,v in all_data.items():
        keys=v.keys()
        x.append(v[keys[0]])
        y.append(v[keys[1]])
        z.append(v[keys[3]])
    
    '''





if __name__ == '__main__':

    plot_solutions('D:\Demo\New_Flow_w_Hierarchy\Journal_Case\Final_Version\Solution\\60X60\Layout_Solutions')
    '''
    
    sol_data={}
    file='D:\Demo\New_Flow_w_Hierarchy\Journal_Case\Version_6\Solution_NSGA\\35X35\Layout_Solutions\plot_data.csv'
    with open(file) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if row[0]=='Layout_ID':
                continue
            else:
                sol_data[row[0]]=([float(row[2]), float(row[3])])
    #sol_data = np.array(sol_data)
    print sol_data
    pareto_data = pareto_frontiter2D(sol_data)
    print len(pareto_data)
    file_name='D:\Demo\New_Flow_w_Hierarchy\Journal_Case\Version_6\Solution_NSGA\\35X35\Pareto_Solutions\plot_pareto_data.csv'
    with open(file_name, 'wb') as my_csv:
        csv_writer = csv.writer(my_csv, delimiter=',')
        for k,v in pareto_data.items():
            data=[k,v[0],v[1]]
            csv_writer.writerow(data)
    my_csv.close()
    
    '''




    '''
    solutions=[]
    for i in range((10)):
        sol=CornerStitchSolution(index=i)
        sol.params={'inductance':i+2.4,'temp':50-i}
        print sol.params
        solutions.append(sol)
    print solutions

    pareto_solutions(solutions)

    
    
    '''
