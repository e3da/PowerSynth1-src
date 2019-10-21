from powercad.cmd_run.cmd import Cmd_Handler
import argparse
import os
import sys
import objgraph
from pympler import muppy,summary
import types
from datetime import datetime
import psutil

def run_test():
    test_cases_dirs={
    'Quang_Journal_S_para': 'D:\Demo\POETS_ANNUAL_MEETING_2019\\testcases_setup\Test\Layout_Cases\Case1_S-param\Layout1_macro.txt'
    }

    # Loop through
    #orig_stdout = sys.stdout
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
    #f = open(dt_string+'.log', 'w')
    #sys.stdout = f

    for k in test_cases_dirs.keys():
        cmd_run = Cmd_Handler()
        cmd_run.new_mode=0
        cmd_run.setup_file(os.path.abspath(test_cases_dirs[k]))
        filename = os.path.basename(cmd_run.macro)
        # change current directory to workspace
        work_dir = cmd_run.macro.replace(filename, '')
        os.chdir(work_dir)
        cmd_run.run_parse()
        all_objects = muppy.get_objects()
        my_types = muppy.filter(all_objects, Type=types.DictType)
        sum1 = summary.summarize(my_types)
        summary.print_(sum1)

    #sys.stdout = orig_stdout
    #f.close()

run_test()


# NOTE -- DONT DELETE THIS
# cd to src
# mprof run powercad\recursive_suite\perf_test.py --> RUN THE Memory profiler on the top level
# mprof plot --> plot the data




















