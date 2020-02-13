#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
TITAN Web Interface
See Github repo for documentation
'''

import unittest

import os.path
import pickle
import numpy as np
from numpy import convolve as np_convolve
from scipy.signal import fftconvolve, lfilter, filtfilt, firwin, upfirdn
from scipy.signal import convolve as sig_convolve
from scipy.ndimage import convolve1d
import datetime, sys

class echoes_dsp(object):
    '''
    echoes_signals contains signal processing algorithms for the EchOES platform
    '''

    # Debug variables
    _class = None
    _debug = None
    _debug_level = None

    sampling_frequency = None
    nyquist_frequency = None

    def __init__(self, sample_rate = 7200000.0, debug = False, debug_level = 1):
        '''
        Constructor
        '''

        self._debug = debug
        self._debug_level = debug_level
        self._class = self.__class__.__name__

        self.sampling_frequency = float(sample_rate)
        self.nyquist_frequency = self.sampling_frequency * 0.5;

        self.dprint("Initializing signal processing algorithms; sampling frequency set to "+str(sample_rate)+"Hz")
  
    def close(self):
        return True


    # Sets the sampling rate
    def set_sampling_frequency(self, fs):

        self.dprint("Updating sampling rate to "+str(sample_rate)+"Hz")


        self.sampling_frequency = float(fs)
        self.nyquist_frequency = self.sampling_frequency * 0.5;
        return True


    # Returns the sampling rate
    def get_sampling_frequency(self):
        return self.sampling_frequency


    def remove_bad_reads( self, adc_captures_float, high_end=0.15, low_end=0.01 ):
        START_DATA_PTS = 58                                                     #evaluate signal after 8us

        new_adc_captures = []

        idx = []
        for index, adc_capture in enumerate(adc_captures_float):

            keep = True

            # Discard empty array
            if not adc_capture:
                self.dprint("Discarding null value - no data present")


            # Looking for long period of the same value
            if keep:
                last_val        = -100000.0
                duplicate_cnt   = 0
                longest_run     = 0
                current_run     = 0

                # --- Find the longest period of same value --- #
                for i in range(0, len(adc_capture)):
                    if adc_capture[i] == last_val:
                        duplicate_cnt   += 1
                        current_run     += 1
                    else:
                        if longest_run < current_run:
                            longest_run = current_run
                        current_run = 0

                    last_val = adc_capture[i]
                # --- End loop here --- #

                longest_run_ratio = float(longest_run)/float(len(adc_capture))
                if longest_run_ratio > 0.5:
                    self.dprint("Discarding {} - too many same \
                        sequential value".format(index))
                    keep = False

                duplicate_cnt_ratio = float(duplicate_cnt)/float(len(adc_capture))
                if duplicate_cnt_ratio > 0.9:
                    self.dprint("Discarding {} - too many duplicate".format(index))
                    keep = False


            # Look for unusual standard deviations:
            if keep:
                data_std = np.std(adc_capture[START_DATA_PTS:], ddof=1, axis=0)
                self.dprint("\nidx:{}, data_std {}".format(index, data_std))
                
                if data_std > high_end or data_std < low_end:
                    keep = False
                    self.dprint("\nBAD  idx:{}, data_std {}".format(index, data_std))

            # New array of data after discarding bad reads
            if keep:
                new_adc_captures.append(adc_capture)
            else:
                idx.append(index)                                               # save bad index for statistic
        
        # --- End main loop here --- #


        print("Keeping {}/{} samples".format(len(new_adc_captures), 
                                                    len(adc_captures_float)))

        return new_adc_captures, idx
        # return adc_captures_float, idx 


    # Creates filter coefficients for an FIR filter
    def create_fir_filter( self, cutoffHz, taps, type ):

        if type == "lowpass":
            cutoffHz = float(cutoffHz)
            b = firwin(taps, cutoffHz / self.nyquist_frequency,  window = "hamming" )     
        elif type == "highpass":
            cutoffHz = float(cutoffHz)
            b = firwin(taps, cutoffHz / self.nyquist_frequency, window = "hamming", pass_zero=False)     
        elif type == "bandpass":
            cutoffHz = [float(a) / self.nyquist_frequency for a in cutoffHz]
            b = firwin(taps, cutoffHz, pass_zero=False, window = "hamming")     

        return b    


    # Applies an FIR filter
    def apply_fir_filter(self, x, b):

        filterlen = len(b)
        
        y = filtfilt(b, 1.0, x)
        
        return y


    # Upsamples by an integer amount
    def upsample(self, x, upsampling_rate):

        self.sampling_frequency *= upsampling_rate;
        self.nyquist_frequency *= upsampling_rate;

        filterlen = 101
        b = firwin(101, 1.0 / upsampling_rate ) 
        y = upfirdn(b, x, up=upsampling_rate)

        y = [i*upsampling_rate for i in y]

        y = y[filterlen/2:len(y)-filterlen/2]
        return y


    # Creates an amplitude envelope of the current signal
    def create_envelope( self, x ):        
        filterlen = 101
        out = [0]*(len(x))
        indx = 0
        for s in x:
            out[indx] = abs(2.0*s)
            indx += 1

        b = self.create_fir_filter( 101, filterlen, "lowpass")
        x = self.apply_fir_filter(out, b) 

        return x


    # Applies a bandpass with a new created fir filter
    def apply_bandpass_filter(self, x, low_end, high_end, filterlen=51):
        b = self.create_fir_filter( [ float(low_end), float(high_end)], filterlen, "bandpass")
        y = self.apply_fir_filter(x, b)
        return y


    # Applies a bandpass with a given filter
    def apply_bandpass_filter_fir(self, x, filter):
        return self.apply_fir_filter(x, filter)


    # Removes the DC offset from a signal
    def remove_dc_offset(self, x):

        avg = sum(x)/float(len(x))
            
        x[:] = [i - avg for i in x]
    
        return x

    # Normalizes the signal
    def normalize(self, x):

        # Find the max absolute value
        xabs = map(abs, x)
        maxval = max(xabs)

        # Prevent normalizing an empty signal with just noise
        if maxval < 0.05:
            maxval = 0.05
        if maxval > 0:
            indx = 0
            for s in x:
                x[indx] = s / maxval
                indx+=1
        return x 


    def upsample_custom(self, s, n, phase=0):
        return np.roll(np.kron(s, np.r_[1, np.zeros(n-1)]), phase)


    def interpolation(self, s, r, l=4, alpha=0.5):
        '''
        s: signal
        r: ratio
        '''
        b = signal.firwin(2*l*r+1, alpha/r)
        a = 1
        return r*signal.lfilter(b, a, self.upsample_custom(s,r))[r*l+1:-1]

    
    # Prints messages with function and class
    def dprint(self, txt, timestamp=False, error=False, level = 1):

        if level <= self._debug_level:
            if self._debug or error:
                function_name = sys._getframe(1).f_code.co_name
                if timestamp:
                    print("  "+str(datetime.datetime.now())+" "+self._class+":"+function_name+"(): "+txt)  
                else:
                    print("  "+self._class+":"+function_name+"(): "+txt)         

class Test(unittest.TestCase):

    def testIt(self):

        return


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()        