from scipy.fftpack import fft, fftshift, ifft
from scipy.fftpack import fftfreq
import numpy as np
import matplotlib.pyplot as plt

datas = np.loadtxt("/home/rs/Programs/city-sensor/serial_plot/save_data/03182021_223014_200hz.csv", delimiter=",",
                   skiprows=0)
y = datas[:, 7]
fs = 200  # frequence Hz

# fft
Y = fft(y)

# the positive part of fft, get from fft
pos_Y_from_fft = Y[:Y.size // 2]

# plot the figures
plt.figure(figsize=(10, 12))

plt.subplot(211)
plt.plot(y, lw=0.5)
y_fft = np.abs(pos_Y_from_fft)
x_fft = np.arange(0, len(y_fft)) * fs / 2. / len(y_fft)

plt.subplot(212)
plt.plot(x_fft[1:], np.log10(y_fft[1:]), lw=0.5)

plt.show()
