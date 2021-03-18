import copy
import threading
from time import sleep

import numpy as np

from lib.parser import DataParser
from lib.thread_serial import ComThread


class ComData(object):
    """
    Subscriber to ROS topic that buffers incoming data
    """

    def __init__(self, start_idx, size=8):
        self.start_idx = start_idx
        self.size = 8
        self.idx = 0
        self.error = None

        self.lock = threading.Lock()
        # self.buff_x = []
        # self.buff_y = []
        self.buff_x = np.empty((0), np.int)
        self.buff_y = np.empty((0, self.size), np.int16)

        self.ser = None

    def open(self, port, baud):
        self.data_parser = DataParser()
        self.ser = ComThread(port, baud, 0.5)
        if self.ser.is_open:
            self.ser.start_read(self.datas_handle)
            print(f"Start reading.")
            return True
        else:
            print(f"start failed.")
            return False

    def datas_handle(self, raw_bytes):
        data_lists = []
        for byte in raw_bytes:
            if self.data_parser.parser_put_data(byte):
                data_pack = self.data_parser.get_data()
                data_lists.append(data_pack)
        if data_lists:
            data_all = np.array(data_lists)
            try:
                self.lock.acquire()
                idx_end = self.idx + data_all.shape[0]
                self.buff_y = np.concatenate((self.buff_y, data_all), axis=0)
                self.buff_x = np.concatenate((self.buff_x, np.arange(self.idx, idx_end)), axis=0)
                self.idx = idx_end
            except:
                pass
            finally:
                self.lock.release()

    def next(self):
        """
        Get the next data in the series

        :returns: [xdata], [ydata]
        """
        if self.error:
            raise self.error
        try:
            self.lock.acquire()
            buff_x = copy.deepcopy(self.buff_x)
            buff_y = copy.deepcopy(self.buff_y)
            self.buff_x = np.empty((0), np.int)
            self.buff_y = np.empty((0, self.size), np.int16)
        finally:
            self.lock.release()
        return buff_x, buff_y

    def close(self):
        if self.ser:
            self.ser.stop_read()
            self.ser = None

    def reset_idx(self):
        try:
            self.lock.acquire()
            self.idx = 0
            self.buff_x = np.empty((0), np.int)
            self.buff_y = np.empty((0, self.size), np.int16)
        except:
            pass
        finally:
            self.lock.release()

if __name__ == "__main__":

    comdata = ComData(0)

    while True:
        sleep(1)
