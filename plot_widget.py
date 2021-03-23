#!/usr/bin/env python

# Copyright (c) 2011, Dorian Scholz, TU Darmstadt
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#   * Neither the name of the TU Darmstadt nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
import copy
import logging
import os
import time

# from python_qt_binding.QtCore import Qt

# from python_qt_binding import loadUi
# from python_qt_binding.QtCore import Qt, QTimer, qWarning, Slot
# from python_qt_binding.QtGui import QIcon
# from python_qt_binding.QtWidgets import QAction, QMenu, QWidget
from datetime import datetime

import numpy as np
from PyQt5.QtCore import QTimer, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QBrush, QColor
from PyQt5.QtWidgets import QWidget, QMenu, QListWidgetItem
from PyQt5.uic import loadUi
from scipy import signal

from com_data import ComData
from data_plot import DataPlot


class PlotWidget(QWidget):
    _redraw_interval = 40

    def __init__(self, initial_topics=None, start_paused=False):
        super(PlotWidget, self).__init__()
        self.setObjectName('PlotWidget')

        self._initial_topics = initial_topics

        ui_file = os.path.join('.', 'resource', 'plot.ui')
        loadUi(ui_file, self)

        # self.subscribe_topic_button.setIcon(QIcon.fromTheme('list-add'))
        # self.remove_topic_button.setIcon(QIcon.fromTheme('list-remove'))

        self.pause_button.setIcon(QIcon.fromTheme('media-playback-pause'))
        self.clear_button.setIcon(QIcon.fromTheme('edit-clear'))
        self.btn_setting.setIcon(QIcon.fromTheme('configure'))
        self.data_plot = None
        self.filter_plot = None

        # self.subscribe_topic_button.setEnabled(False)
        if start_paused:
            self.pause_button.setChecked(True)

        self._start_time = time.time()
        self._plotdata = {}
        self.filter_name = {}
        self._comdata = ComData(0)
        self.channels = 8

        self._remove_topic_menu = QMenu()

        self.yMinSpinBox.setValue(0)
        self.yMaxSpinBox.setValue(1000)

        for i in range(8):
            self._plotdata[f"CH{i}"] = i
            self.filter_name[i] = f"CH{i}_filter"

        self.csvFile = None

        b, a = signal.butter(40, 2 * 40 / 200, 'lowpass')
        self.filter_b = b
        self.filter_a = a
        self.filter_zi = signal.lfilter_zi(self.filter_b, self.filter_a)
        self.filter_zi = np.tile(self.filter_zi, (8, 1)).transpose()
        self.filter_zf = self.filter_zi

        # init and start update timer for plot
        self._update_plot_timer = QTimer(self)
        self._update_plot_timer.timeout.connect(self.update_plot)

        # Data Plot ---------------------------
        _data_plot = DataPlot(self)

        # disable autoscaling of X, and set a sane default range
        _data_plot.set_autoscale(x=False)
        _data_plot.set_autoscale(y=DataPlot.SCALE_EXTEND | DataPlot.SCALE_VISIBLE)
        _data_plot.set_xlim([0, 10.0])

        self.switch_data_plot_widget(_data_plot)

    def switch_data_plot_widget(self, data_plot):
        self.enable_timer(enabled=False)

        self.plotLayout.removeWidget(self.data_plot)
        if self.data_plot is not None:
            self.data_plot.close()

        self.data_plot = data_plot
        self.data_plot.autoscroll(self.autoscroll_checkbox.isChecked())

        # data_x, data_y_all = self._comdata.next()
        # while data_x.shape[0] == 0:
        #     time.sleep(0.1)
        #     data_x, data_y_all = self._comdata.next()
        data_x = np.empty(0, np.int)
        data_y = np.empty(0, np.int16)
        for topic_name, data_idx in self._plotdata.items():
            # data_y = data_y_all[:, data_idx]
            self.data_plot.add_curve(topic_name, topic_name, data_x, data_y)

            self.listWidgetChannels.addItem(topic_name)
            self.listWidgetChannels.item(data_idx).setForeground(QBrush(self.data_plot._curves[topic_name]['color']))

        for _, data_idx in self._plotdata.items():
            topic_name = self.filter_name[data_idx]
            self.data_plot.add_curve(topic_name, topic_name, data_x, data_y)

            self.listWidgetChannels.addItem(topic_name)
            self.listWidgetChannels.item(self.channels + data_idx).setForeground(
                QBrush(self.data_plot._curves[topic_name]['color']))

        self.enable_timer(self._plotdata)
        self.data_plot.redraw()

        self.plotLayout.addWidget(self.data_plot)

    @pyqtSlot(bool)
    def on_btn_open_clicked(self, checked):
        if checked:
            port = self.edit_port.text()
            baud = self.edit_baudrate.text()
            if not self._comdata.open(port, baud):
                self.btn_open.setChecked(False)
            else:
                self.btn_open.setText("Close")
        else:
            self._comdata.close()
            self.btn_open.setText("Open")

    @pyqtSlot()
    def on_btn_save_clicked(self):
        timer_status = self._update_plot_timer.isActive()
        if timer_status:
            self.enable_timer(False, wait=True)
        buff_y = None

        x_limit = [np.inf, -np.inf]
        for curve_id, data_idx in self._plotdata.items():
            curve = self.data_plot._get_curve(curve_id)
            if len(curve['x']) > 0:
                x_limit[0] = min(x_limit[0], curve['x'].min())
                x_limit[1] = max(x_limit[1], curve['x'].max())

        for curve_id, data_idx in self._plotdata.items():
            curve = self.data_plot._get_curve(curve_id)
            start_index = curve['x'].searchsorted(x_limit[0])
            end_index = curve['x'].searchsorted(x_limit[1])
            region = curve['y'][start_index:end_index]

            if buff_y is None:
                buff_y = [region.copy()]
            else:
                buff_y = np.concatenate((buff_y, [region.copy()]), axis=0)
        if timer_status:
            self.enable_timer(True)

        if buff_y is not None and buff_y.size != 0:
            dir = "save_data"
            os.makedirs(dir, exist_ok=True)
            name = f'{datetime.now().strftime("%m%d%Y_%H%M%S")}.csv'
            file_path = os.path.abspath(os.path.join(dir, name))
            np.savetxt(file_path, buff_y.T, fmt="%d", delimiter=',')
            self.label_status.setText(f"save {buff_y.shape[-1]} data to: {file_path}")

    @pyqtSlot(bool)
    def on_pause_button_clicked(self, checked):
        self.enable_timer(not checked)

    @pyqtSlot(bool)
    def on_autoscroll_checkbox_clicked(self, checked):
        self.data_plot.autoscroll(checked)
        if checked:
            self.data_plot.redraw()

    @pyqtSlot(bool)
    def on_autoscroll_checkbox_clicked(self, checked):
        self.data_plot.autoscroll(checked)
        if checked:
            self.data_plot.redraw()

    @pyqtSlot(int)
    def on_yMinSpinBox_valueChanged(self, value):
        if not self.cbox_autoscale_y.isChecked():
            self.manual_scale_y()

    @pyqtSlot(int)
    def on_yMaxSpinBox_valueChanged(self, value):
        if not self.cbox_autoscale_y.isChecked():
            self.manual_scale_y()

    def manual_scale_y(self):
        y_min = self.yMinSpinBox.value()
        y_max = self.yMaxSpinBox.value()
        self.data_plot.set_ylim([y_min, y_max])
        self.data_plot.redraw()

    @pyqtSlot(bool)
    def on_cbox_autoscale_y_clicked(self, checked):
        if checked:
            self.data_plot.set_autoscale(y=DataPlot.SCALE_EXTEND | DataPlot.SCALE_VISIBLE)
            self.data_plot.redraw()
        else:
            self.data_plot.set_autoscale(y=0)
            self.manual_scale_y()

    @pyqtSlot()
    def on_clear_button_clicked(self):
        self.clear_plot()

    @pyqtSlot()
    def on_btn_setting_clicked(self):
        self.data_plot.doSettingsDialog()

    @pyqtSlot(QListWidgetItem)
    def on_listWidgetChannels_itemDoubleClicked(self, item):
        curve_id = item.text()

        if self.data_plot.visible(curve_id):
            self.data_plot.set_visible(curve_id, False)
            item.setBackground(Qt.color1)
        else:
            self.data_plot.set_visible(curve_id, True)
            item.setBackground(Qt.color0)

    @pyqtSlot()
    def on_btn_showall_clicked(self):
        for curve_id, data_idx in self._plotdata.items():
            self.data_plot.set_visible(curve_id, True)
            self.listWidgetChannels.item(data_idx).setBackground(Qt.color0)

    @pyqtSlot()
    def on_btn_hideall_clicked(self):
        for curve_id, data_idx in self._plotdata.items():
            self.data_plot.set_visible(curve_id, False)
            self.listWidgetChannels.item(data_idx).setBackground(Qt.color1)

    def update_plot(self):
        if self.data_plot is not None:
            needs_redraw = False

            data_x, data_y_all = self._comdata.next()
            if len(data_y_all.shape) == 1:
                data_y_all = data_y_all.reshape(-1, 8)
            if data_x.shape[0] != 0:
                data_filtered, self.filter_zf = signal.lfilter(self.filter_b, self.filter_a, data_y_all, axis=0,
                                                               zi=self.filter_zf)

                for topic_name, data_idx in self._plotdata.items():
                    data_y = data_y_all[:, data_idx]
                    self.data_plot.update_values(topic_name, data_x, data_y)

                    self.data_plot.update_values(self.filter_name[data_idx], data_x, data_filtered[:, data_idx])
                needs_redraw = True

            if needs_redraw:
                self.data_plot.redraw()

    def clear_plot(self):
        self.enable_timer(False, wait=True)
        self._comdata.reset_idx()
        for topic_name, idx in self._plotdata.items():
            self.data_plot.clear_values(topic_name)
            self.data_plot.clear_values(self.filter_name[idx])
        self.data_plot.redraw()
        self.enable_timer(self._plotdata)

    def enable_timer(self, enabled=True, wait=False):
        if enabled:
            self._update_plot_timer.start(self._redraw_interval)
        else:
            self._update_plot_timer.stop()
            if wait:
                while self._update_plot_timer.isActive():
                    time.sleep(0.01)
