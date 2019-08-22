"""
Created on Wednesday, 17th of August 2019

author: Mert Unsal

Contains the functions for analyzing electrophysiological data, specifically finding out if there's a modulation between spindles and spike trains.
"""

import numpy as np
from matplotlib import pyplot as plt
from analysis_utils import *
import yasa

'''
This function takes output of the find_spindles function (pandas dataFrame that has spindle data), phase intervals of the histogram, sampling frequency, and spike train in order to
produce phase histogram data of spindles added on top of each other. Output of the function can be fed into plot_barchart and plot_polarbarchart function in order to plot the histograms.
'''

def spindle_phase_hist(sp, phase, fs, spike_train):
    phase_hist_spike_trains = {}
    time_spike_trains = {}
    bins = []
    heights = []
    flag = True
    index = 0

    for freq in sp.loc[:,"Frequency"]:
        start_index = int(sp.loc[index,"Start"] * fs)
        end_index = int(sp.loc[index,"End"] * fs)
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
This function takes output of the find_spindles function (pandas dataFrame that has spindle data), phase intervals of the histogram, sampling frequency, and spike train in order to
produce phase histogram data of spindle envelope added on top of each other. Output of the function can be fed into plot_barchart and plot_polarbarchart function in order to plot these histograms.
'''

def spindle_envelope_phase_hist(sp, phase, fs, spike_train):
    phase_hist_spike_trains = {}
    bins = []
    heights = []
    flag = True
    index = 0

    for freq in sp.loc[:,"Frequency"]:
        start_index = int(sp.loc[index,"Start"] * fs)
        end_index = int(sp.loc[index,"End"] * fs)
        duration = float(sp.loc[index,"Duration"])
        freq = 1/duration
        phase_histogram = phase_hist(spike_train[start_index:end_index], freq, phase, fs)
        phase_hist_spike_trains[str(index)] = phase_histogram
        if flag:
            bins = phase_histogram[1]
            heights = phase_histogram[0]
            flag = False
        else:
            heights = np.add(heights, phase_histogram[0])

        index += 1

    return [heights, bins, phase_hist_spike_trains]

'''
This function takes a data and its sampling frequency in order to produce a pandas Dataframe showing detected spindles.
'''

def find_spindles(data, fs):
    return yasa.spindles_detect(data, fs)

'''
This function is for plotting the spindles on the top of raw data in a specific time limit, taking data, time, sampling frequency, xlabel, ylabel, title, and time limit as input.
'''

def plot_spindles(data, times, fs, sp, xlabel, ylabel, title, time_limit):
    bool_spindles = yasa.get_bool_vector(data, fs, sp)
    spindles_highlight = data * bool_spindles
    spindles_highlight[spindles_highlight == 0] = np.nan

    plt.plot(times, data, 'k')
    plt.plot(times, spindles_highlight, 'indianred')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(time_limit)
    plt.title(title)
    plt.show()
