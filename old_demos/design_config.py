'''
Author:      Brett Shook; bxs003@uark.edu

Desc:        System design geometry, constraints, and properties

Created:     Apr 25, 2011
Last Change: May 25, 2011

Copyright: 2011 University of Arkansas Board of Trustees 
'''

import tfsm
from util import Rect

#-------------------------------------------------------
#----------------- Thermal Parameters ------------------
#-------------------------------------------------------

ratio = [0.0025, 0.0154, 0.125, 0.25, 0.5, 0.75, 1.0]
die_scale_temp = [49.92, 49.54, 51.64, 56.38, 68.41, 81.25, 103.16]
trace_scale_temp = [8.16, 12.44, 27.93, 40.31, 59.34, 77.58, 102.03]

iso_top_avg_temp = 8.1414
sub_res = 0.203535
t_amb = 22.0
die_power = 40.0
#die_res = 0.0
die_res = 0.2165

# Flux through isolation top
iso_top_flux = [1.0472, 0.8459, 0.6849, 0.5329, 0.3952, 0.2616, 0.1568, 0.0218]
iso_top_flux_w = [2.7315, 3.6798, 4.6314, 5.6152, 6.6991, 7.7830, 8.8669, 21.4034]
iso_top_flux_h = [2.3702, 2.9790, 3.5881, 4.1985, 4.8089, 5.8033, 8.1433, 19.4231]
iso_top_flux_rects = tfsm.build_contour_rects(iso_top_flux, iso_top_flux_w, iso_top_flux_h)

flux_eff_w = iso_top_flux_w[-1]
flux_eff_h = iso_top_flux_h[-1]

# Trace top theta temp. dist.
trace_top_temps = [56.2244027073332, 32.0368637098486, 15.5212421591135, 11.6427563525046, 10.1437215058235, 9.28938454630535, 8.69460268983079, 8.24440177674724, 7.89893388393914, 7.63886084645984, 7.48052069715610]
trace_top_w = [2.06576206257589, 7.94202589925679, 12.7108317235656, 17.5375555983441, 22.4675264103677, 27.2702515477122, 31.9136435031933, 36.2133055880290, 40.1125366450244, 43.3681905346427, 44.8876950354610]
trace_top_h = [1.20000000000000, 6.54000000000000, 11.8800000000000, 17.2200000000000, 22.5600000000000, 27.9000000000000, 33.2400000000000, 38.5800000000000, 43.9200000000000, 49.2600000000000, 54.6000000000000]
trace_temp_rects = tfsm.build_contour_rects(trace_top_temps, trace_top_w, trace_top_h)

trace_char_w = 83.83
trace_char_h = 54.6
trace_char_dim = [trace_char_w, trace_char_h]

thermal_features = tfsm.ThermalFeatures(iso_top_flux_rects, iso_top_avg_temp, trace_temp_rects,
                                        ratio, die_scale_temp, trace_scale_temp, die_power,
                                        die_res, sub_res, t_amb, trace_char_dim)

#-------------------------------------------------------
#----------------- Geometry Parameters -----------------
#-------------------------------------------------------

die_w = 4.8
die_h = 2.4

#die_locs = [[8.6, 3.5], [8.6, 15.5], [8.6, 27.5], [8.6, 3.5], [8.6, 15.5], [8.6, 27.5]]

#initial_die_placements = [[[3.0,3.5], [2.0, 2.5]],
#                         [[3.0,3.5], [5.0,5.5]],
#                         [[3.0,3.5], [8.0,8.5]],
#                         [[3.0,3.5], [11.0,11.5]],
#                         [[3.0,3.5], [14.0,14.5]],
#                         [[3.0,3.5], [17.0,17.5]],
#                         ]

die_locs = [[8.6, 3.5], [8.6, 15.5], [8.6, 27.5]]
initial_die_placements = [[[3.0,3.5], [2.0, 2.5]],
                         [[3.0,3.5], [5.0,5.5]],
                         [[3.0,3.5], [8.0,8.5]]
                         ]

num_dies = len(initial_die_placements)

sub_w = 83.83
sub_h = 54.6

# Traces
trace_top = Rect(31.0, 24.0, 6.75, 13.5)
trace_mid = Rect(19.0, 12.0, 6.75, 13.5)
trace_bot = Rect(7.0, 0.0, 6.75, 13.5)
trace_left = Rect(31.0, 0.0, 0.0, 6.75)
trace_rects = [trace_top, trace_mid, trace_bot, trace_left]
#main = Rect(31.2, 0.0, 0.0, 24.0)
#trace_rects = [main]


# DRC Related
min_die_die_space = 0.2 #mm
min_die_edge_space = 0.1 #mm

