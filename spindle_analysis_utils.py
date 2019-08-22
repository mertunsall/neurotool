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

def find_spindles(data, fs, thresh={'rel_pow': 0.2, 'corr': 0.65, 'rms': 1.5}):
    return yasa.spindles_detect(data, fs, thresh = thresh)

'''
This function is for plotting the spindles on the top of raw data in a specific time limit, taking data, time, sampling frequency, xlabel, ylabel, title, and time limit as input.
'''

def plot_spindles(data, times, fs, sp, xlabel, ylabel, title, time_limit):
    bool_spindles = yasa.get_bool_vector(data, fs, sp)
    spindles_highlight = data * bool_spindles

    plt.plot(times, data, 'k')
    plt.plot(times, spindles_highlight, 'indianred')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(time_limit)
    plt.title(title)
    plt.show()

'''
This function takes all raw data, its sampling frequency, and the spindle dataFrame as input in order to save raw data of each spindle.
It will save the raw data for each spindle, in the following format: {'0': [spindle0rawdata], '1': [spindle1rawdata], ....}
'''

def save_spindles(data0, fs, sp):
    spindle_dict = {}
    index = 0
    for start in sp.loc[:,"Start"]:
        start_index = int(start * fs)
        end_index = int(sp.loc[index,"End"] * fs)
        spindle_dict[str(index)] = data0[start_index:end_index]
        index += 1
    return spindle_dict

'''
This function takes the spindle dataframe, spike_train of every unit, sampling frequency, a time interval in seconds (dt)
as input to output the following information about for each unit:
[Average firing rate of the unit in the following time interval [start - dt:start],
Average firing rate of the unit in the following time interval [spindle duration],
Average firing rate of the unit in the following time interval [end : end + dt]]
You can access this information by indexing the output array[unit_index]
'''

def firing_rate_spindle(sp, spike_train, sf, dt):
    sphist = []
    index = 0
    for i in range(len(spike_train)):
        ind = 0
        frs = 0
        frb = 0
        fra = 0
        for freq in sp.loc[:,"Frequency"]:
            start_index = int(sp.loc[ind,"Start"] * sf)
            end_index = int(sp.loc[ind,"End"] * sf)
            duration = sp.loc[ind,"Duration"]
            for j in spike_train[i][start_index:end_index]:
                if j == 1:
                    frs += (1/duration)
            for j in spike_train[i][int(start_index - dt * sf):start_index]:
                if j == 1:
                    frb += (1/dt)
            for j in spike_train[i][end_index:int(end_index + dt * sf)]:
                if j == 1:
                    fra += (1/dt)
            ind += 1

        sphist.append([frb/ ind, frs/ ind, fra/ ind])
        index += 1

    return np.asarray(sphist)

'''
This function takes the spike train of all units, its samplng frequency, spindle dataFrame, and phase intervals as the input
in order to output the following:
[num_spikes, phase_hist_spike_trains, time_spike_trains, unit_hist_arrays]

1. num_spikes is an array showing how many spikes in total are found in spindles, for each unit. You can access the data by indexing the array with unit_index
2. phase_hist_spike_trains is a dictionary which holds the phase histograms of each spindle, for each unit. To access the data, first you should index the
unit_index in dictionary, (e.g. arr[str(unit_index)]) then the spindle number.
3. time_spike_trains is a dictionary which holds time aligned spike trains in spindles, for each unit. Data can be accessed as demonstrated in
phase_hist_spike_trains explanation
4. unit_hist_arrays is a dictionary holding sums of the phase histogram arrays for all spindles, for each unit.
You can access the data by indexing the array with unit_index
'''

def spindle_all_units(sp, phase, sf, spike_train):
    num_spikes = []
    phase_hist_spike_trains = {}
    time_spike_trains = {}
    unit_hist_arrays = {}

    for i in range(len(spike_train)):
        hist = spindle_phase_hist(sp, phase, sf, spike_train[i])
        phase_hist_spike_trains[str(i)] = hist[2]
        time_spike_trains[str(i)] = hist[3]
        arr = hist[0:2]
        unit_hist_arrays[str(i)] = arr
        s = np.sum(arr[0])
        num_spikes.append(s)

    num_spikes = np.asarray(num_spikes)
    return [num_spikes, phase_hist_spike_trains, time_spike_trains, unit_hist_arrays]

'''
This function takes the spike train of all units, its samplng frequency, spindle dataFrame, and phase intervals as the input
in order to output the following:
[phase_hist_envelope_spike_trains, unit_hist_envelope_arrays]


1. phase_hist_envelope_spike_trains is a dictionary which holds the phase histograms of each spindle envelope, for each unit.
To access the data, first you should index the unit_index in dictionary, (e.g. arr[str(unit_index)]) then the spindle number.
2. unit_hist_arrays is a dictionary holding sums of the phase histogram arrays for all spindles, for each unit.
You can access the data by indexing the array with unit_index
'''

def spindle_envelope_all_units(sp, phase, sf, spike_train):
    phase_hist_spike_trains = {}
    unit_hist_arrays = {}

    for i in range(len(spike_train)):
        hist = spindle_envelope_phase_hist(sp, phase, sf, spike_train[i])
        phase_hist_spike_trains[str(i)] = hist[2]
        arr = hist[0:2]
        unit_hist_arrays[str(i)] = arr

    return [phase_hist_spike_trains, unit_hist_arrays]
