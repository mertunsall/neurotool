"""
Created on Wednesday, 18th of August 2019

author: Mert Unsal

Contains the functions for analyzing electrophysiological data, specifically finding out if there's a modulation between slow waves and spike trains.
"""

import numpy as np
from matplotlib import pyplot as plt
from analysis_utils import *
import yasa

'''
This function takes output of the find_slowwave function (pandas dataFrame that has slow wave data), phase intervals of the histogram,
sampling frequency, and spike train in order to produce phase histogram data of slow waves added on top of each other. Output of the
function can be fed into plot_barchart and plot_polarbarchart function in order to plot the histograms.
'''

def slowwave_phase_hist(sw, phase, fs, spike_train):
    phase_hist_spike_trains = {}
    time_spike_trains = {}
    bins = []
    heights = []
    flag = True
    index = 0

    for freq in sw.loc[:,"Frequency"]:
        start_index = int(sw.loc[index,"Start"] * fs)
        end_index = int(sw.loc[index,"End"] * fs)
        time_spike_trains[str(index)] = spike_train[start_index:end_index]
        phase_histogram = phase_hist(spike_train[start_index:end_index], freq, phase, fs)
        phase_hist_spike_trains[str(index)] = phase_histogram
        if flag:
            bins = phase_histogram[1]
            heights = phase_histogram[0]
            flag = False
        else:
            heights = np.add(heights, phase_histogram[0])

        index += 1

    return [heights, bins, phase_hist_spike_trains, time_spike_trains]

'''
This function takes a data and its sampling frequency in order to produce a pandas Dataframe showing detected slow waves.
'''

def find_slowwave(data, fs):
    return yasa.sw_detect(data, fs)

'''
This function is for plotting the slow waves on the top of raw data in a specific time limit, taking data, time, sampling frequency, xlabel, ylabel, title, and time limit as input.
'''

def plot_slowwave(data, times, fs, sw, xlabel, ylabel, title, time_limit):
    bool_sw = yasa.get_bool_vector(data, fs, sw)
    sw_highlight = data * bool_sw
    sw_highlight[sw_highlight == 0] = np.nan

    plt.plot(times, data, 'k')
    plt.plot(times, sw_highlight, 'indianred')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(time_limit)
    plt.title(title)
    plt.show()
