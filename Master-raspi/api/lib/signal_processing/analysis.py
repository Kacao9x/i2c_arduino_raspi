import numpy as np
from numpy.fft import fft, ifft, rfft, irfft
from scipy import signal
import math

# Calculate mean
def mean(numbers):
    return float(sum(numbers.real)) / max(len(numbers.real), 1)

def find_echo_features( capture, first_echo_range = (30, 150), corr_freq = 300000, period_range = 1.5, feature_span = 20, impulse_offset = 8, echo_search_window = 6.0, debug = False ):

    def get_feature_position( sub_capture, max = True, peak = False):

        upsampling_rate = 100
        sub_capture_up = signal.resample_poly(sub_capture, up=upsampling_rate, down=1)

        # Looking for transitions
        if max:
            position = np.argmax(sub_capture_up)
            if not peak:
                while sub_capture_up[position] >= 0.0 and position > 0:
                    position -= 1
        else:
            position = np.argmin(sub_capture_up)
            if not peak:
                while sub_capture_up[position] <= 0.0 and position > 0:
                    position -= 1

        position = position/float(upsampling_rate)

        return position


    sub_capture = capture[first_echo_range[0]:first_echo_range[1]]
    position = get_feature_position(sub_capture, max = False)
    echo_1_center = position + float(first_echo_range[0])
    echo_delta = (echo_1_center - impulse_offset)

    echo_2_center_apprx = echo_1_center+echo_delta
    sub_capture = capture[int(echo_2_center_apprx-echo_search_window*2):int(echo_2_center_apprx+echo_search_window*2)]
    position = get_feature_position(sub_capture, max = True)
    echo_2_center = position + int(echo_2_center_apprx-echo_search_window*2)
    echo_delta = echo_2_center - echo_1_center

    echo_3_center_apprx = echo_2_center + echo_delta
    sub_capture = capture[int(echo_3_center_apprx-echo_search_window):int(echo_3_center_apprx+echo_search_window)]
    position = get_feature_position(sub_capture, max = False)
    echo_3_center = position + int(echo_3_center_apprx-echo_search_window)
    echo_delta = (echo_3_center - echo_1_center)*0.5

    echo_4_center_apprx = echo_3_center + echo_delta
    sub_capture = capture[int(echo_4_center_apprx-echo_search_window):int(echo_4_center_apprx+echo_search_window)]
    position = get_feature_position(sub_capture, max = True)
    echo_4_center = position + int(echo_4_center_apprx-echo_search_window)
    echo_delta = (echo_4_center - echo_1_center)/3.0

    output = {}
    output['echo-1-center'] = echo_1_center
    output['echo-2-center'] = echo_2_center
    output['echo-3-center'] = echo_3_center
    output['echo-4-center'] = echo_4_center

    return output