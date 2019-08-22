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

    plt.plot(times, data, 'k')
    plt.plot(times, sw_highlight, 'indianred')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(time_limit)
    plt.title(title)
    plt.show()

'''
This function takes all raw data, its sampling frequency, and the slow wave dataFrame as input in order to save raw data of each slow wave.
It will save the raw data for each slow wave, in the following format: {'0': [slowwave0rawdata], '1': [slowwave1rawdata], ....}
'''

def save_slowwave(data0, fs, sw):
    sw_dict = {}
    index = 0
    for start in sw.loc[:,"Start"]:
        start_index = int(start * fs)
        end_index = int(sw.loc[index,"End"] * fs)
        sw_dict[str(index)] = data0[start_index:end_index]
        index += 1
    return sw_dict

'''
This function takes the slow wave dataframe, spike_train of every unit, sampling frequency, a time interval in seconds (dt)
as input to output the following information about for each unit:
[Average firing rate of the unit in the following time interval [start - dt:start],
Average firing rate of the unit in the following time interval [slowwave duration],
Average firing rate of the unit in the following time interval [end : end + dt]]
You can access this information by indexing the output array[unit_index]
'''

def firing_rate_sw(sw, spike_train, sf, dt):
    swhist = []
    index = 0
    for i in range(len(spike_train)):
        ind = 0
        frs = 0
        frb = 0
        fra = 0
        for freq in sw.loc[:,"Frequency"]:
            start_index = int(sw.loc[ind,"Start"] * sf)
            end_index = int(sw.loc[ind,"End"] * sf)
            duration = sw.loc[ind,"Duration"]
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

        swhist.append([frb/ ind, frs/ ind, fra/ ind])
        index += 1

    return np.asarray(swhist)

'''
This function takes the spike train of all units, its sampling frequency, slow wave dataFrame, and phase intervals as the input
in order to output the following:
[num_spikes, phase_hist_spike_trains, time_spike_trains, unit_hist_arrays]

1. num_spikes is an array showing how many spikes in total are found in slow waves, for each unit. You can access the data by indexing the array with unit_index
2. phase_hist_spike_trains is a dictionary which holds the phase histograms of each slow wave, for each unit. To access the data, first you should index the
unit_index in dictionary, (e.g. arr[str(unit_index)]) then the slow wave number.
3. time_spike_trains is a dictionary which holds time aligned spike trains in slow wave, for each unit. Data can be accessed as demonstrated in
phase_hist_spike_trains explanation
4. unit_hist_arrays is a dictionary holding sums of the phase histogram arrays for all slow waves, for each unit.
You can access the data by indexing the array with unit_index
'''

def sw_all_units(sw, phase, sf, spike_train):
    num_spikes = []
    phase_hist_spike_trains = {}
    time_spike_trains = {}
    unit_hist_arrays = {}

    for i in range(len(spike_train)):
        hist = slowwave_phase_hist(sw, phase, sf, spike_train[i])
        phase_hist_spike_trains[str(i)] = hist[2]
        time_spike_trains[str(i)] = hist[3]
        arr = hist[0:2]
        unit_hist_arrays[str(i)] = arr
        s = np.sum(arr[0])
        num_spikes.append(s)

    num_spikes = np.asarray(num_spikes)
    return [num_spikes, phase_hist_spike_trains, time_spike_trains, unit_hist_arrays]
