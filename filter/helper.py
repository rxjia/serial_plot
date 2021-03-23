import numpy as np
from scipy import fft


def fft_xy(y, fs):
    Y = fft(y)
    # the positive part of fft, get from fft
    pos_Y_from_fft = Y[:Y.size // 2]

    y_fft = np.abs(pos_Y_from_fft)
    x_fft = np.arange(0, len(y_fft)) * fs * 0.5 / len(y_fft)
    return x_fft[1:], np.log10(y_fft[1:])
