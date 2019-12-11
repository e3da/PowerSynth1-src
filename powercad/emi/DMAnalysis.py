#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt

def current_source(amplitude, frequency, max_frequency, t_fall, duty_cycle):
    # Switching period
    tau = 1./frequency
    # On-time
    t_on = duty_cycle * tau
    # Number of harmonics
    num_harmonics = int(max_frequency // frequency) + 1
    n = np.arange(0, num_harmonics)
    frequencies = frequency*n + frequency
    
    # Initialize output arrays
    I_n = np.zeros(num_harmonics)
    for i in xrange(0, num_harmonics):
        # Simplifications
        n_pi = n[i] * np.pi
        
        if n_pi == 0:
            term_1 = 1.
            term_2 = 1.
        else:
            # Term 1
            term_1 = np.sin(n_pi*t_on*frequency) / (n_pi*t_on*frequency)
            # Term 2
            term_2 = np.sin(n_pi*t_fall*frequency) / (n_pi*t_fall*frequency)
            
        result = 2 * amplitude * duty_cycle * np.abs(term_1) * np.abs(term_2)
        
        I_n[i] = result

    return np.array([frequencies, I_n])

def dBuV_line(frequency_range, levels, freq_eval):
    freqs = frequency_range
    m = (levels[0]-levels[-1])/((np.log10(freqs[0])-(np.log10(freqs[-1]))))
    # print m
    b = levels[0] - m*np.log10(freqs[0])
    # print b
    y = m*np.log10(freq_eval) + b
    return y

class EMI_Standards(object):
    def __init__(self, frequency_data):
        self.frequency_data = frequency_data
        self.standards = {
            'MIL': [
                ['MIL-STD-461F CE102 Peak Limits'],
                [1e4, 1e7]
            ],
            'VDE_A': [
                ['VDE 0871 Group A'],
                [1e4, 3e7]
            ],
            'CISPR_Group_2_HP': [
                ['CISPR/EN 55011 Class A Group 2 HP Quasi Peak'],
                [0.15e6, 3e7]
            ],
            'CISPR_Group_2_LP': [
                ['CISPR/EN 55011 Class A Group 2 LP Quasi Peak'],
                [0.15e6, 3e7]
            ],
            'CISPR_Group_1': [
                ['CISPR/EN 55011 Class A Group 1 Quasi Peak'],
                [0.15e6, 3e7]
            ],
            'CISPR_Group_2_LP_HF': [
                ['CISPR/EN 55011 Class A Group 2 LP Quasi Peak (HF region only)'],
                [5e6, 3e7]
            ]
        }
        self.standard_keys = self.show_available()
        self.frequencies = None
        self.limit_line = None
        self.extents = None
        self.freq_indices = None
        self.name = None
    
    def show_available(self):
        standard_keys = []
        for std in self.standards:
            standard_keys.append([std])
        return standard_keys
            
    def apply_standard(self, standard='MIL'):
        f_range = self.standards[standard][1]
        self.extents = f_range
        f_min = f_range[0]
        f_max = f_range[1]
        f = self.frequency_data
        self.freq_indices = np.where((f >= f_min) & (f <= f_range[1]))

        self.frequencies = f[self.freq_indices]
        self.limit_line = self.limit_definition(standard, self.frequencies)
        self.name = self.standards[standard][0]
                             
    def limit_definition(self, standard, frequencies):
        f = frequencies
        standard_limits = {
            'MIL': [
                [f < 1e4, (f >= 1e4) & (f < 5e5), f >= 5e5],
                [np.nan, lambda x: dBuV_line([1e4, 5e5], [104, 70], x), 70.]
            ],
            'VDE_A': [
                [f < 1e4, (f >= 1e4) & (f < 1.5e5), (f >= 1.5e5) & (f < 5e5), f >= 5e5],
                [np.nan, lambda x: dBuV_line([1e4, 1.5e5], [91, 70], x), 66., 60.]
            ],
            'CISPR_Group_2_HP': [
                [f < 0.5e6, (f >= 0.5e6) & (f < 5e6), (f >= 5e6)],
                [130., 125., 115.]  
            ],
            'CISPR_Group_2_LP': [
                [f < 0.5e6, (f >= 0.5e6) & (f < 5e6), (f >= 5e6) & (f <= 3e7), f > 3e7],
                [100., 86., lambda x: dBuV_line([5e6, 3e7], [90., 73.], x), 73.]
            ],
            'CISPR_Group_1': [
                [f < 0.5e6, f >= 0.5e6],
                [79., 73.]
            ],
            'CISPR_Group_2_LP_HF': [
                [(f < 5e6), (f >= 5e6) & (f <= 3e7), f > 3e7],
                [np.nan, lambda x: dBuV_line([5e6, 3e7], [90., 73.], x), 73.]
            ],
        }
        
        level = np.piecewise(f, standard_limits[standard][0], standard_limits[standard][1])
        return level
        

def corner_line(frequencies, k, m=40.):
    y = m * np.log10(frequencies) + k
    return y

def solve_db_line_zero(frequencies, levels):
    y = levels
    x = frequencies
    m = (y[1] - y[0])/(np.log10(x[1]) - np.log10(x[0]))
    b = y[1] - m*np.log10(x[1])
    y0 = 0
    x0 = 10**(-b/m)
    return (x0, y0)

def data_gte_zero(freq, noise):
    '''
    gtez = np.where((noise >= 0))[0]
    if gtez[0] > 0:
        ind1 = gtez[0]
        ind2 = gtez[0]
    else:
        ind1 = 0
        ind2 = 1
    freq0, noise0 = solve_db_line_zero([freq[ind1], freq[ind2]], [noise[ind1], noise[ind2]])
    freq = np.insert(freq, ind1, freq0)
    noise = np.insert(noise, ind1, noise0)
    '''
    gtez = np.where((noise >= 0))
    return freq[gtez], noise[gtez]
        
def corner_frequency(frequencies, attenuation_req, cutoff_slope=40.):
    # Start by checking to make sure there is a zero point for comparison
    f, att = data_gte_zero(frequencies, attenuation_req)
    #f = frequencies
    #att = attenuation_req
    m = cutoff_slope
    k = 1.
    y = corner_line(f, k, m)
    
    difference = y - att
    ind = np.argmin(difference)
    
    new_k = k - difference[ind]
    intersection = [f[ind], att[ind]]
    # new_k = k - np.min((y[ind]-noise_req[ind]))
    # print new_k
    fc = 10**(-new_k/m)
    new_y = corner_line(f, new_k, m)
    
    return fc, f, att, new_y, intersection


def noise_analysis(frequency_data, noise, standard='CISPR_Group_2_LP', offset=3., lw=3, plot=True, fig_name='Fig1.png'):
    # Data handling
    fd = frequency_data
    fd, noise = data_gte_zero(fd, noise)
    standard_def = EMI_Standards(fd)
    standard_def.apply_standard(standard)
    freq = standard_def.frequencies
    limit = standard_def.limit_line
    indices = standard_def.freq_indices
    #limit, extent, std_name = emi_standard(f, standard=standard)
    attenuation_req = noise[indices] - limit + offset
    #plt.semilogx(frequency_data[indices], attenuation_req)
    #plt.show()
    fc, freq_new, att_new, fc_line, intersection = corner_frequency(freq, attenuation_req)
    
    if plot:
        noise_max = max(noise) + 10
        att_max = max(att_new) + 10

        fig, (ax1, ax2) = plt.subplots(2, 1, facecolor='white', sharey=False, sharex=False, figsize=(14,8))

        ax1.semilogx(fd, noise, c='navy', linewidth=lw, label='DM Noise')
        ax1.semilogx(freq, limit, '--', c='darkorange', linewidth=lw, label=standard+' Limit Line')
        ax2.semilogx(freq_new, att_new, c='navy', linewidth=lw, label='Required Attenuation')
        ax2.semilogx(freq_new, fc_line, '--', c='darkorange', linewidth=lw, label='40dB/dec Line')
        ax2.semilogx([fc, freq_new[0]], [0, fc_line[0]], '--', c='darkorange', linewidth=lw)
        ax2.scatter(fc, 0, s=70, c='green')
        ax2.annotate('Cutoff\nFrequency\n' + format(fc, '.3E') + 'Hz', fontsize=14,
                     xy=(fc, 0.), xytext=(0.01, 0.3), textcoords='axes fraction', 
                     arrowprops=dict(facecolor='black', shrink=0.05)
                    )
        ax2.scatter(intersection[0], intersection[1], s=70, c='red')
        ax2.annotate('Intersection\nPoint\n' + format(intersection[0], '.3E') + 'Hz' +
                     '\n(' + format(intersection[1], '.2g') +' dB)', fontsize=14,
                     xy=(intersection[0], intersection[1]), xytext=(0.8, 0.3), textcoords='axes fraction', 
                     arrowprops=dict(facecolor='black', shrink=0.05)
                    )

        #ax1.set_xlim(extent[0], extent[1])
        ax1.set_ylim(0, noise_max)
        #ax2.set_xlim(extent[0], extent[1])
        ax2.set_ylim(-10, att_max)
        ax1.grid(which='both', axis='both')
        ax2.grid(which='both', axis='both')
        fig.suptitle('Differential Mode Noise Analysis', fontsize=22, fontweight='bold')
        ax1.set_title(standard_def.name[0], fontsize=18)
        ax1.set_ylabel('Noise Level (dBuV)', fontsize=16)
        ax1.set_xlabel('Frequency (Hz)', fontsize=16)
        ax2.set_ylabel('Attenuation (dBuV)', fontsize=16)
        ax2.set_xlabel('Frequency (Hz)', fontsize=16)
        ax2.set_title('Required Attenuation and Cutoff Frequency', fontsize=18)
        ax1.tick_params(axis='both', labelsize=14)
        ax2.tick_params(axis='both', labelsize=14)
        plt.subplots_adjust(hspace=0.4)
        plt.savefig(fig_name, dpi=200)
        plt.show()
    
    return fc


#noise_analysis()



