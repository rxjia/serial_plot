import matplotlib
import numpy as np
from scipy import signal
from scipy.fftpack import fft, ifft
import matplotlib.pyplot as plt

from filter.helper import fft_xy

matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.sans-serif'] = 'SimHei'

# Load data
y_all = np.loadtxt("/home/rs/Programs/city-sensor/serial_plot/save_data/03182021_223014_200hz.csv", delimiter=",",
                   skiprows=0)
n_chs = y_all.shape[1]
y = y_all[:, 6]
x = np.arange(len(y))

# Filter params --------------------------------------------
# FIR low pass  ~40Hz
b = [-0.00431402930730817, -0.0130913216218316, -0.0165150877272552, -0.00643058443337602, 0.00981787626662569,
     0.0108018802381368, -0.00656741371282849, -0.0168048296226863, 0.000653253913101169, 0.0224712800873412,
     0.0101471314679486, -0.0256577409885416, -0.0265589606190970, 0.0230483928540287, 0.0503852903895158,
     -0.00929120358802463, -0.0879185034417772, -0.0337703300143186, 0.187334796517400, 0.401505729847994,
     0.401505729847994, 0.187334796517400, -0.0337703300143186, -0.0879185034417772, -0.00929120358802463,
     0.0503852903895158, 0.0230483928540287, -0.0265589606190970, -0.0256577409885416, 0.0101471314679486,
     0.0224712800873412, 0.000653253913101169, -0.0168048296226863, -0.00656741371282849, 0.0108018802381368,
     0.00981787626662569, -0.00643058443337602, -0.0165150877272552, -0.0130913216218316, -0.00431402930730817]
a = 1

# butter filter
b, a = signal.butter(40, 2 * 40 / 200, 'lowpass')  # 配置滤波器 8 表示滤波器的阶数

# Filter, single channel ----------------------------
# Filter Init
# zi = signal.lfilter_zi(b, a)
# zf = zi
#
# y_filtered=[]
# for i in range(len(y)):
#     data_read = np.array([y[i]])
#     data_filtered, zf = signal.lfilter(b, a, data_read, axis=0, zi=zf)
#     y_filtered.append(data_filtered)
# =====

# Filter, multi channels ----------------------------
# -- single step filter --
# Filter Init
zi = signal.lfilter_zi(b, a)
zi = np.tile(zi, (n_chs, 1)).transpose()  # zi shape:  (jieshu, 8chs)
zf = zi

y_filtered = []
for i in range(len(y)):
    data_read = y_all[[i], :]  # (1,8chs)
    data_filtered, zf = signal.lfilter(b, a, data_read, axis=0, zi=zf)  # (1,8chs)
    y_filtered.append(data_filtered)
# =====

# Filter, filter all
ch6_filtered = signal.filtfilt(b, a, y)

plt.figure()
plt.subplot(211)
# plt.plot(x, y, lw=0.5)
plt.plot(x, np.array(y_filtered)[:, 0, :], lw=0.5)
plt.legend(('raw', 'filter'), loc='best')
plt.grid(True)

plt.subplot(212)
plt.plot(x, y, lw=0.5)
plt.plot(x, np.array(ch6_filtered), lw=0.5)
plt.legend(('raw', 'CH6_filtered'), loc='best')
plt.grid(True)
plt.show()

# plt.figure()
# plt.subplot(311)
# x_,y_=fft_xy(y, 200)
# plt.plot(x_,y_, lw=0.5)
# plt.legend(('raw', 'Signal Output'), loc='best')
# # plt.xlabel('Time (s)')
# # plt.ylabel('CH3 Raw')
# plt.grid(True)
#
# plt.subplot(312)
# x_,y_=fft_xy(y_filtered, 200)
# plt.plot(x_,y_, lw=0.5)
# plt.legend(('raw', 'Signal Output'), loc='best')
# # plt.xlabel('Time (s)')
# # plt.ylabel('CH3 Raw')
# plt.grid(True)
#
# plt.subplot(313)
# x_,y_=fft_xy(y_filtered_b, 200)
# plt.plot(x_,y_, lw=0.5)
# plt.legend(('raw', 'Signal Output'), loc='best')
# # plt.plot(x, np.array(y_filtered), lw=0.5)
# # plt.xlabel('Time (s)')
# # plt.ylabel('CH3 Filtered')
# # plt.grid(True)
# plt.show()
