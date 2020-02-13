import matplotlib.pyplot as plt
import glob
import pandas as pd
import pycwt as wavelet
import thLib as th
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import math
from numpy import array
from scipy import signal
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import os
import fractions
from scipy.interpolate import interp1d


# ********** Reads all files from folder(adreess) and returns data in files as datafram columns*********** #
def retrieve_dat_files_in_folder_as_dataframe():
    address = th.ui.getdir('Pick your directory')  # prompts user to select folder
    file_name = pd.DataFrame()
    for filename in glob.glob(os.path.join(address, "*.dat")):
        my_file = open(filename)
        y_str = my_file.read()
        y_str = y_str.splitlines()
        data = []
        for num in y_str:
            data.append(float(num))
        data = pd.DataFrame(data)
        file_name = pd.concat([file_name, data], axis=1, ignore_index=True)
    return file_name


# ************** Reads all csv files from specified path(addr), returns data in files as dataframe columns************ #
# ****************down_sample: boolean to enable downsampling, down_spl_val: downsampling rate *************** #
def retrieve_csv_files_in_folder_as_dataframe(down_sample, down_spl_val):
    addr = th.ui.getdir('Pick your directory') # prompts user to select folder
    dtf = pd.DataFrame()
    for filename in glob.glob(os.path.join(addr, "*.csv")):
        my_file = open(filename)
        data = pd.read_csv(my_file, header=4, sep=r',', error_bad_lines=False, engine='python')
        dtf = pd.concat([dtf, data], axis=1, ignore_index=True)
    if down_sample:
        dtf = dtf.iloc[::down_spl_val, :]
    return dtf


def select_csv_data_file():
    file, path = th.ui.getfile('*', 'Select a file') # prompts user to select file
    data = pd.read_csv(path + "/" + file)
    return data


# **************** Get wavelet transform scales corresponding to frequencies freq1 and freq2 **************** #
def get_scales_bandpass(freq1, freq2, delta_t):
    mh_ctr_freq = 0.25  # Mexican Hat wavelet center frequency
    scale1 = round(mh_ctr_freq/(delta_t*freq1))
    scale2 = round(mh_ctr_freq/(delta_t*freq2))
    return scale1, scale2


# **************** Get wavelet transform scale corresponding to frequency freq1 **************** #
def get_scales_highpass(freq1, delta_t):
    mh_ctr_freq = 0.25  # Mexican Hat wavelet center frequency
    scale = round(mh_ctr_freq/(delta_t*freq1))
    return scale


# *************** create 3d plots of wavelet transforms of time series ********************* #
# ***** x: numpy ndarray reprensenting x axis, widths: numpy ndarray reprensenting wavelet transform scale range ***** #
# *********** cwt: 2d array (widths * N:number of samples) returned by scipy.cwt *********** #
def create_3d_plots(x, widths, cwt):
    x, widths = np.meshgrid(x, widths)
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(x, widths, cwt, rstride=1, cstride=1, cmap='viridis', linewidth=0, antialiased=False)
    ax.view_init(elev=10., azim=100)
    ax.set_zlim(-2.5, 2.5)
    ax.set_xlabel('Translation')
    ax.set_ylabel('Scale')
    ax.set_zlabel('Amplitude')
    #ax.set_title("bottom view", y=0.05)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(x, widths, cwt, rstride=1, cstride=1, cmap='viridis', linewidth=0, antialiased=False)
    ax.view_init(elev=0., azim=90)
    ax.set_zlim(-3, 3)
    ax.set_xlabel('Translation')
    ax.set_ylabel('Scale')
    ax.set_zlabel('Amplitude')
    plt.suptitle("Wavelet Transform of Difference", fontsize=16)
    plt.show()

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(x, widths, cwt, rstride=1, cstride=1, cmap='viridis', linewidth=0, antialiased=False)
    ax.view_init(elev=0., azim=0)
    ax.set_zlim(-1, 1)
    ax.set_xlabel('Translation')
    ax.set_ylabel('Scale')
    ax.set_zlabel('Amplitude')
    plt.show()


# **************** create 2d plots of time series ************** #
# ********** if two_plots is False, plots dat against x. If two_plots is True, plots dat and dat2 against x ********* #
def create_2d_plot(x, dat, dat2, two_plots):
    plt.plot(x, dat)
    plt.suptitle("Signal in time domain", fontsize=16)
    plt.xlabel('Time(s)')
    plt.ylabel('Voltage(V)')
    if two_plots:
        plt.plot(x, dat2, 'r')
        plt.legend(['original signal', 'reconstructed signal'])
    plt.show()


# ******** Normalizes values in arr between 0 and 1 by dividing them by the highest value in arr ****** #
def normalize(arr):
    maxim = max(arr)
    arr = [x / maxim for x in arr]
    return arr


# ******** takes a window from 200 to 1000 of time series before normalizing ********** #
# **** returns windowed and normalized time series, time shift for time accurate plotting, length of processed ts **** #
def window_and_normalize(ts):  # ts: time series
    ts = ts[200:1000]
    maxim = max(ts)
    loc = ts.index(maxim)
    ts = ts[loc-20:loc+500]
    n = len(ts)
    ts = [x / maxim for x in ts]
    temp = ts[:loc]

    time_shift = len(temp) + 180
    return ts, time_shift, n


# ******* returns the highest value in a row of a ndarray passed by np.apply_along_axis() function ****** #
def get_highest_val(a):
    arr = []
    for v in a:
        arr.append(v)
    arr = np.sort_complex(np.array(arr))
    if len(arr) != 0:
        ret = arr[-1]
    else:
        ret = 0
    return ret


# locates first and second echoes in time and scale by returning scale_echo1, time_echo1, scale_echo2, time_echo2 #
# ***** returns "not found" if echo was not found ****** #
# arr: 2d array representing wavelet transform of time series
# leng: number of samples in time series
# p : integer representing an estimate of the latest possible time(see below) of the occurrence of the 1st echo
# echo2_min_pos : integer representing time(see below) of earliest possible occurrence of 2nd echo
# echo2_max_pos : integer representing time(see below) of latest possible occurrence of 2nd echo
# time expressed in number of samples in windowed time series
def locate_echoes(arr, p, echo2_max_pos):

    ar = arr[:, 0:p]
    b = np.apply_along_axis(get_highest_val, 1, ar)  # find highest value in each row of ar and store it in b
    coeffs1 = []
    coeffs2 = []

    for x in b:
        coeffs1.append(x)

    echo1 = max(coeffs1)
    scale_and_pos1 = np.where(ar == echo1)
    scale_echo1 = scale_and_pos1[0][0]
    time_echo1 = scale_and_pos1[1][0]

    ar1 = arr[:, p:echo2_max_pos]
    c = np.apply_along_axis(get_highest_val, 1, ar1)

    for v in c:
        coeffs2.append(v)

    if coeffs2:
        echo2 = max(coeffs2)
        scale_and_pos2 = np.where(arr == echo2)
        scale_echo2 = scale_and_pos2[0][0]
        time_echo2 = scale_and_pos2[1][0]

    # arr[pos_echo1-20:pos_echo1+20, pos_echo2-10:pos_echo2+10] = np.zeros((40, 20))
    if coeffs1 and coeffs2:
        return scale_echo1, time_echo1, scale_echo2, time_echo2
    else:
        return scale_echo1, time_echo1, "not found", "not found"


# ***** selects the frequencies needed in the wavelet transform ****** #
# **** wav_trsfrm: wavelet transform to extract frequencies from ***** #
# **** w: width(scale range passed to cwt function) **** #
# **** band: boolean saying if function acts as a bandpass filter ***** #
# **** high: boolean saying if function acts as a highpass filter ***** #
# **** freq1: lowest frequency needed **** #
# **** freq1: highest frequency needed, its default value is 1 if functions acts as a highpass filter **** #
def select_frequencies(wav_trsfrm, w, band, high, delta_t, freq1, freq2=1):

        if band:
            scl1, scl2 = get_scales_bandpass(freq1, freq2, delta_t)
            print(scl1)
            print(scl2)
            if scl1 <= w and scl2 <= w:
                wav_trsfrm = wav_trsfrm[scl2:scl1, :]
                wav_trsfrm = np.pad(wav_trsfrm, ((scl2, abs(w-scl1)), (0, 0)), 'constant')
            else:
                print("Try larger scale range")

        if high:
            sc = get_scales_highpass(freq1)
            if sc <= w:
                wav_trsfrm = wav_trsfrm[0:sc, :]
                wav_trsfrm = np.pad(wav_trsfrm, ((0, abs(w-sc)), (0, 0)), 'constant')
            else:
                print("Try larger scale range")

        return wav_trsfrm


def interp_1d(ys, mul):
    # linear extrapolation for last (mul - 1) points
    ys = list(ys)
    ys.append(2*ys[-1] - ys[-2])
    # make interpolation function
    xs = np.arange(len(ys))
    fn = interp1d(xs, ys, kind="cubic")
    # call it on desired data points
    new_xs = np.arange(len(ys) - 1, step=1./mul)
    return fn(new_xs)


def upsample(s, n, phase=0):
    """Increase sampling rate by integer factor n  with included offset phase.
    """
    return np.roll(np.kron(s, np.r_[1, np.zeros(n-1)]), phase)


def interp(s, r, l=4, alpha=0.5):
    """Interpolation - increase sampling rate by integer factor r. Interpolation
    increases the original sampling rate for a sequence to a higher rate. interp
    performs lowpass interpolation by inserting zeros into the original sequence
    and then applying a special lowpass filter. l specifies the filter length
    and alpha the cut-off frequency. The length of the FIR lowpass interpolating
    filter is 2*l*r+1. The number of original sample values used for
    interpolation is 2*l. Ordinarily, l should be less than or equal to 10. The
    original signal is assumed to be band limited with normalized cutoff
    frequency 0=alpha=1, where 1 is half the original sampling frequency (the
    Nyquist frequency). The default value for l is 4 and the default value for
    alpha is 0.5.
    """
    b = signal.firwin(2*l*r+1, alpha/r);
    a = 1
    return r*signal.lfilter(b, a, upsample(s, r))[r*l+1:-1]


# ****** Remove selected frequencies from time series passed as columns of a dataframe *****#
# ****** Saves processed time series as a csv in selected folder. Saved folder name is new_dtfrm.csv ***#
# ****** dtfrm: dataframe whose columns are the time series to be processed ******#
# ****** band_pass: boolean. If True, a band pass filtering will be performed on time series ****#
# ****** high_pass: boolean. If True, a high pass filtering will be performed on time series ****#
# ***** low_freq_limit :lowest frequency to keep in processed signal *******#
# ***** high_freq_limit:highest frequency to keep in processed signal. Default value is 1 if high pass filtering ******#
# ***** width: range of scales to use in wavelet transform ******#
# ***** delta_t: sampling rate ******#
def remove_frequencies_and_save_to_csv(dtfrm, band_pass, high_pass, low_freq_limit, high_freq_limit, width, delta_t):
    [row, column] = dtfrm.shape
    frame = pd.DataFrame()

    i = 0
    while i < column:
        y = dtfrm.iloc[:, i].tolist()

        wave, scales, freqs, coi, fft, fftfreqs = wavelet.cwt(y, delta_t, J=width-1, wavelet=u'mexicanhat')
        wave = select_frequencies(wave, width, band_pass, high_pass, delta_t, low_freq_limit, high_freq_limit)
        xrec = wavelet.icwt(wave, scales, delta_t, wavelet=u'mexicanhat')

        xrec = normalize(xrec)

        xrec = pd.Series(xrec)
        frame = pd.concat([frame, xrec], axis=1, ignore_index=True)

        i = i + 1

    print("Select a folder")
    path = th.ui.getdir('Select a directory to save the csv file') # prompts user to select folder
    frame.to_csv(path + "/" + "new_dtfrm.csv")


factor = 10
fs = 7200000*factor
dt = 1 / fs
retrievedData = retrieve_dat_files_in_folder_as_dataframe()
# row1 = list(retrievedData)
# retrievedData = retrievedData.iloc[50:1000, :]
remove_frequencies_and_save_to_csv(retrievedData, factor, True, False, 200000, 3500000, 100, dt)
