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

import os
import time

# from python_qt_binding import loadUi
# from python_qt_binding.QtCore import Qt, QTimer, qWarning, Slot
# from python_qt_binding.QtGui import QIcon
# from python_qt_binding.QtWidgets import QAction, QMenu, QWidget
from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.QtGui import QIcon, QBrush
from PyQt5.QtWidgets import QWidget, QMenu
from PyQt5.uic import loadUi

from com_data import ComData


class PlotWidget(QWidget):
    _redraw_interval = 40

    def __init__(self, initial_topics=None, start_paused=False):
        super(PlotWidget, self).__init__()
        self.setObjectName('PlotWidget')

        self._initial_topics = initial_topics

        ui_file = os.path.join('.', 'resource', 'plot.ui')
        loadUi(ui_file, self)
        self.subscribe_topic_button.setIcon(QIcon.fromTheme('list-add'))
        self.remove_topic_button.setIcon(QIcon.fromTheme('list-remove'))
        self.pause_button.setIcon(QIcon.fromTheme('media-playback-pause'))
        self.clear_button.setIcon(QIcon.fromTheme('edit-clear'))
        self.data_plot = None

        self.subscribe_topic_button.setEnabled(False)
        if start_paused:
            self.pause_button.setChecked(True)

        self._start_time = time.time()
        self._plotdata = {}
        self._comdata = ComData(0)

        self._remove_topic_menu = QMenu()

        for i in range(8):
            self._plotdata[f"CH{i}"] = i

        # init and start update timer for plot
        self._update_plot_timer = QTimer(self)
        self._update_plot_timer.timeout.connect(self.update_plot)

    def switch_data_plot_widget(self, data_plot):
        self.enable_timer(enabled=False)

        self.plotLayout.removeWidget(self.data_plot)
        if self.data_plot is not None:
            self.data_plot.close()

        self.data_plot = data_plot
        self.plotLayout.addWidget(self.data_plot)
        self.data_plot.autoscroll(self.autoscroll_checkbox.isChecked())

        data_x, data_y_all = self._comdata.next()
        while data_x.shape[0] == 0:
            time.sleep(0.1)
            data_x, data_y_all = self._comdata.next()

        for topic_name, data_idx in self._plotdata.items():
            data_y = data_y_all[:, data_idx]
            self.data_plot.add_curve(topic_name, topic_name, data_x, data_y)

            self.listWidgetChannels.addItem(topic_name)
            self.listWidgetChannels.item(data_idx).setForeground(QBrush(self.data_plot._curves[topic_name]['color']))

        self.enable_timer(self._plotdata)
        self.data_plot.redraw()

        # # setup drag 'n drop
        # self.data_plot.dropEvent = self.dropEvent
        # self.data_plot.dragEnterEvent = self.dragEnterEvent
        #
        # if self._initial_topics:
        #     for topic_name in self._initial_topics:
        #         self.add_topic(topic_name)
        #     self._initial_topics = None
        # else:
        #     for topic_name, rosdata in self._rosdata.items():
        #         data_x, data_y = rosdata.next()
        #         self.data_plot.add_curve(topic_name, topic_name, data_x, data_y)
        #
        # self._subscribed_topics_changed()

    #
    # @Slot('QDragEnterEvent*')
    # def dragEnterEvent(self, event):
    #     # get topic name
    #     if not event.mimeData().hasText():
    #         if not hasattr(event.source(), 'selectedItems') or \
    #                 len(event.source().selectedItems()) == 0:
    #             qWarning(
    #                 'Plot.dragEnterEvent(): not hasattr(event.source(), selectedItems) or '
    #                 'len(event.source().selectedItems()) == 0')
    #             return
    #         item = event.source().selectedItems()[0]
    #         topic_name = item.data(0, Qt.UserRole)
    #         if topic_name == None:
    #             qWarning('Plot.dragEnterEvent(): not hasattr(item, ros_topic_name_)')
    #             return
    #     else:
    #         topic_name = str(event.mimeData().text())
    #
    #     # check for plottable field type
    #     plottable, message = is_plottable(topic_name)
    #     if plottable:
    #         event.acceptProposedAction()
    #     else:
    #         qWarning('Plot.dragEnterEvent(): rejecting: "%s"' % (message))
    #
    # @Slot('QDropEvent*')
    # def dropEvent(self, event):
    #     if event.mimeData().hasText():
    #         topic_name = str(event.mimeData().text())
    #     else:
    #         droped_item = event.source().selectedItems()[0]
    #         topic_name = str(droped_item.data(0, Qt.UserRole))
    #     self.add_topic(topic_name)
    #
    #
    @pyqtSlot(bool)
    def on_pause_button_clicked(self, checked):
        self.enable_timer(not checked)

    @pyqtSlot(bool)
    def on_autoscroll_checkbox_clicked(self, checked):
        self.data_plot.autoscroll(checked)
        if checked:
            self.data_plot.redraw()

    @pyqtSlot()
    def on_clear_button_clicked(self):
        self.clear_plot()

    def update_plot(self):
        if self.data_plot is not None:
            needs_redraw = False

            data_x, data_y_all = self._comdata.next()
            if data_x.shape[0] != 0:
                for topic_name, data_idx in self._plotdata.items():
                    data_y = data_y_all[:, data_idx]
                    self.data_plot.update_values(topic_name, data_x, data_y)
                needs_redraw = True

            if needs_redraw:
                self.data_plot.redraw()

    # def add_topic(self, topic_name):
    #     topics_changed = False
    #     for topic_name in get_plot_fields(topic_name)[0]:
    #         if topic_name in self._rosdata:
    #             qWarning('PlotWidget.add_topic(): topic already subscribed: %s' % topic_name)
    #             continue
    #         self._rosdata[topic_name] = ROSData(topic_name, self._start_time)
    #         if self._rosdata[topic_name].error is not None:
    #             qWarning(str(self._rosdata[topic_name].error))
    #             del self._rosdata[topic_name]
    #         else:
    #             data_x, data_y = self._rosdata[topic_name].next()
    #             self.data_plot.add_curve(topic_name, topic_name, data_x, data_y)
    #             topics_changed = True
    #
    #     if topics_changed:
    #         self._subscribed_topics_changed()
    #
    # def remove_topic(self, topic_name):
    #     self._rosdata[topic_name].close()
    #     del self._rosdata[topic_name]
    #     self.data_plot.remove_curve(topic_name)
    #
    #     self._subscribed_topics_changed()
    #
    def clear_plot(self):
        for topic_name, _ in self._plotdata.items():
            self.data_plot.clear_values(topic_name)
        self.data_plot.redraw()

    # def clean_up_subscribers(self):
    #     for topic_name, rosdata in self._rosdata.items():
    #         rosdata.close()
    #         self.data_plot.remove_curve(topic_name)
    #     self._rosdata = {}
    #
    #     self._subscribed_topics_changed()

    def enable_timer(self, enabled=True):
        if enabled:
            self._update_plot_timer.start(self._redraw_interval)
        else:
            self._update_plot_timer.stop()
