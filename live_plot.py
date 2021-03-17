import math
import time

import matplotlib.pyplot as plt
import numpy as np


class LivePlot:
    def __init__(self):
        self.lines = []
        self.len_lines = 0

    def live_plotter(self, x_vec, y_vec, pause_time=0.001):
        """
        :param x_vec: x轴数据
        :param y_data:  y轴数据
        :param pause_time:
        :return:
        """
        y_vec = y_vec.copy()
        for i in range(y_vec.shape[-1]):
            y_vec[:, i] += 200 * ((y_vec.shape[-1]) / 2. - i - 0.5)

        if self.lines == []:
            # this is the call to matplotlib that allows dynamic plotting
            plt.ion()
            # fig = plt.figure(figsize=(13, 8))
            fig, ax = plt.subplots()
            self.ax = ax
            if y_vec.ndim == 1:
                rows = 1
                self.lines = [None] * rows
                ax = fig.add_subplot(rows, 1, 1)
                self.lines[0], = ax.plot(x_vec, y_vec, '-', lw=0.8, alpha=0.8)
            else:
                self.lines = ax.plot(x_vec, y_vec, '-', lw=0.8, alpha=0.8)
                plt.legend(('CH0', 'CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7'), loc='upper right')
                plt.ylim(-1000, 1000)

                # plt.title('Title: {}'.format(identifier))
            # update plot label/title
            plt.show()
            self.len_lines = len(self.lines)

        # after the figure, axis, and line are created, we only need to update the y-data
        if self.len_lines == 1:
            self.lines[0].set_ydata(y_vec)
        else:
            plt.xlim(x_vec[0], x_vec[-1] + 1e-15)
            for i in range(self.len_lines):
                self.lines[i].set_xdata(x_vec)
                self.lines[i].set_ydata(y_vec[:, i])

        # adjust limits if new data goes beyond bounds
        # for line in self.lines:
        #     if np.min(y_vec) <= line.axes.get_ylim()[0] or np.max(y_vec) >= line.axes.get_ylim()[1]:
        #         plt.ylim([np.min(y_vec) - np.std(y_vec), np.max(y_vec) + np.std(y_vec)])
        # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
        plt.pause(pause_time)


if __name__ == "__main__":
    size = 2000
    x_vec = np.linspace(0, size, size + 1)[0:-1]
    y_vec = np.random.randn(len(x_vec), 4) * 1000
    lines = []
    point = 500
    es_time = np.zeros([point])
    lv_ploter = LivePlot()
    for t in range(point):
        t0 = time.time()
        rand_val = np.random.randn(4) * 1000
        y_vec[-1, :] = rand_val
        lv_ploter.live_plotter(x_vec, y_vec)
        y_vec = np.vstack([y_vec[1:, :], y_vec[[0], :]])
        x_vec += 1
        es_time[t] = 1000 * (time.time() - t0)

    print(np.average(es_time))
    plt.figure()
    plt.plot(es_time)
    plt.show(-1)
