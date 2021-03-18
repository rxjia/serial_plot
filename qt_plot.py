from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
# from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

import plot_widget
from data_plot import DataPlot


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self._widget = plot_widget.PlotWidget()
        # self._data_plot = DataPlot(self._widget)
        #
        # # disable autoscaling of X, and set a sane default range
        # self._data_plot.set_autoscale(x=False)
        # self._data_plot.set_autoscale(y=DataPlot.SCALE_EXTEND | DataPlot.SCALE_VISIBLE)
        # # self._data_plot.set_autoscale(DataPlot.SCALE_VISIBLE)
        # self._data_plot.set_xlim([0, 10.0])
        #
        # self._widget.switch_data_plot_widget(self._data_plot)

        self.setCentralWidget(self._widget)
        # self.graphWidget = pg.PlotWidget()
        # self.setCentralWidget(self.graphWidget)

        # hour = [1,2,3,4,5,6,7,8,9,10]
        # temperature_1 = [30,32,34,32,33,31,29,32,35,45]
        # temperature_2 = [50,35,44,22,38,32,27,38,32,44]
        #
        # #Add Background colour to white
        # self.graphWidget.setBackground('w')
        # # Add Title
        # self.graphWidget.setTitle("Your Title Here", color="b", size="30pt")
        # # Add Axis Labels
        # styles = {"color": "#f00", "font-size": "20px"}
        # self.graphWidget.setLabel("left", "Temperature (°C)", **styles)
        # self.graphWidget.setLabel("bottom", "Hour (H)", **styles)
        # #Add legend
        # self.graphWidget.addLegend()
        # #Add grid
        # self.graphWidget.showGrid(x=True, y=True)
        # #Set Range
        # self.graphWidget.setXRange(0, 10, padding=0)
        # self.graphWidget.setYRange(20, 55, padding=0)
        #
        # self.plot(hour, temperature_1, "Sensor1", 'r')
        # self.plot(hour, temperature_2, "Sensor2", 'b')

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=plotname, pen=pen, symbol='+', symbolSize=30, symbolBrush=(color))


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
