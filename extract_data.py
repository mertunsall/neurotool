"""
Created on Wednesday, 17th of August 2019

author: Mert Unsal

Contains the functions for analyzing electrophysiological data, specifically finding out if there's a modulation between spindle, slow waves and spike trains.
This file specifically includes functions to derive data from different types of files.
"""

import numpy as np


'''

'''

def get_data(mainpath, ff, unit):
    data = []

    #converting values to MicroVolts
    if unit == "MiliVolts":
        data *= (10**3)
    elif unit == "MicroVolts":
        pass
    else:
        data *= (10**6)
    return []

def get_spike_train_data(mainpath, ff):

    return []
