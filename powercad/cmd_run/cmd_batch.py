import sys, os

# Set relative location
cur_path =sys.path[0] # get current path (meaning this file location)
cur_path = cur_path[0:-16] #exclude "power/cmd_run"
sys.path.append(cur_path)
from powercad.cmd_run.cmd import Cmd_Handler
import os,glob
import fileinput

if __name__ == "__main__":
    # print("----------------------PowerSynth Version 1.4: Command line version------------------")
    
    path = 'D:\Demo\\New_Flow_w_Hierarchy\Imam_journal\Cmd_flow_case\Imam_journal\Batch'
    macro_files=[]
    #macro_files =glob.glob("D:\Demo\\New_Flow_w_Hierarchy\Imam_journal\Cmd_flow_case\Imam_journal\Batch\macro_?.txt")
    #macro_files = [f for f in os.listdir(path) if f.endswith('.txt')]
    for f in os.listdir(path) :
        if  f.endswith('.txt') and 'macro_' in f:
            file=os.path.join(path,f)
            for line in fileinput.input(file, inplace=True):
                # for line in file:
                line = line.replace('Layout_script: .\\full_bridge_pm_V6_kelvin.txt', 'Layout_script: .\\full_bridge_pm_V6_flexible.txt')
                sys.stdout.write(line)
            for line in fileinput.input(file, inplace=True):
                # for line in file:
                line = line.replace('Bondwire_setup: .\half_bridge_pm_bondwire_lead_Kelvin.txt', 'Bondwire_setup: .\half_bridge_pm_bondwire_lead_flexible.txt')
                sys.stdout.write(line)
            for line in fileinput.input(file, inplace=True):
                # for line in file:
                line = line.replace('Flexible_Wire: 0', 'Flexible_Wire: 1')
                sys.stdout.write(line)
            macro_files.append(file) 
    print(macro_files)
    for file in macro_files:
        print (file)
        
        debug = True
        if debug: # you can mannualy add the argument in the list as shown here
            
            args = ['python','cmd.py','-m','D:/Demo/New_Flow_w_Hierarchy/Imam_journal/Cmd_flow_case/Imam_journal/half_bridge_pm_macro.txt','-settings',"D:/Demo/New_Flow_w_Hierarchy/Journal_Case/settings.info"]
            #D:/Demo/New_Flow_w_Hierarchy/Journal_Case/Journal_Result_collection/Cmd_flow_case/Half_Bridge_Layout/half_bridge_pm_macro.txt
            #D:\Demo\New_Flow_w_Hierarchy/Imam_journal/Cmd_flow_case/Imam_journal/half_bridge_pm_macro.txt
            #D:/Demo/New_Flow_w_Hierarchy/Journal_Case/Testing_Journal_case_w_Py_3/Cmd_flow_case/Half_Bridge_Layout/half_bridge_pm_macro.txt
            
            #D:/Demo/New_Flow_w_Hierarchy/Journal_Case/Journal_Result_collection/Cmd_flow_case/Half_Bridge_Layout/half_bridge_pm_macro_data_collection_final.txt
            
            #macro_files = [f for f in os.listdir(path) if f.endswith('.txt')]
            
            args[3]=file
            cmd = Cmd_Handler(debug=False)

            cmd.cmd_handler_flow(arguments= args)

        else:
            cmd.cmd_handler_flow(arguments=sys.argv) # Default