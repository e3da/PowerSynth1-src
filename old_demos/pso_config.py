'''
Author:      Brett Shook; bxs003@uark.edu
Desc:        Configuration for the PSO algorithm
Created:     Apr 6, 2011
Last Change: May 25, 2011

Copyright: 2011 University of Arkansas Board of Trustees 
'''

import design_config

num_particles = 100
max_iterations = 850
dimensions = design_config.num_dies*2

init_vel_range = [-10.0, 10.0]

wV0 = 1.0
wV1 = 0.3
wV_delta = wV0 - wV1
wP = 2.02
wG = 2.02

x_max = 35.0
v_max = 30.0

write_data = False
data_file_loc = 'C:/Users/shook/Documents/pmlst/data/data.txt'