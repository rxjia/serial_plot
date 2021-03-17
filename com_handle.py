import datetime
import threading
from time import sleep
import numpy as np
from scipy import signal

import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)-12s [l:%(lineno)-4d] %(levelname)-7s %(message)s')

from lib.parser import DataParser, ParserResult
from lib.thread_serial import ComThread

data_parser = DataParser()


def write_infos(datas, name):
    np.save(name, datas)


def async_write(datas, filename):
    name = "./loginfos/" + filename + ".npy"
    np_datas_raw = np.array(datas)
    thread_handle = threading.Thread(target=write_infos, args=(np_datas_raw, name))
    thread_handle.setDaemon(True)
    thread_handle.start()


# Move sum
n_sum_move = 20

# record
record_start = 0
record_t_start = 0
record_end = None

time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
name = "./loginfos/" + time + ".npy"


def datas_handle(raw_bytes):
    global out_signal_last, record_start, record_t_start, record_end
    global record_datas, record_count
    # print("raw_datas: {}".format(''.join(['%02X ' % b for b in raw_bytes])))

    for byte in raw_bytes:
        if data_parser.parser_put_data(byte):
            data_pack = data_parser.get_data()

            # logging.info("data ready: {}".format(data_pack))
            # data_package = np.zeros(shape=(6,16), dtype= np.int16)
            # data_real = np.empty_like(data_package)
            # time_now = datetime.datetime.now()
            # # 每次数据有6组16通道
            # for n_batch in range(6):
            #     for n_ch in range(16):
            #         data_package[n_batch][n_ch] = data_parser.get_int16_data(16*n_batch + n_ch)
            #     record_datas.append(data_package[n_batch][0:4])
            #     record_count += 1
            #
            #     # 对每组数据进行处理
            #     data_cur = data_package[n_batch][2]
            #
            #     data_read, data_filtered, out_signal = fir_filter.single_filter(data_cur)
            #     if out_signal != out_signal_last:
            #         # TODO: output
            #         if out_signal == SIGNAL.Standup:
            #             out_start = fir_filter.data_count
            #             record_start = max(0, out_start - 1500)
            #             record_t_start = time_now - datetime.timedelta(seconds=(out_start - record_start) / 1000.)
            #
            #         if out_signal == SIGNAL.Sitdown:
            #             record_end = fir_filter.data_count + 1500
            #             pass
            #
            #     # record
            #     if (record_end is not None) and fir_filter.data_count > record_end:
            #         time = record_t_start.strftime("%Y%m%d_%H%M%S_%f")
            #         record_data = fir_filter.datas_raw[record_start:record_end]
            #         async_write(record_data, time + "_action")
            #         async_write(fir_filter.datas_raw, time + "_action")
            #         print("data_count:{}".format(fir_filter.data_count))
            #         record_end = None
            #
            #     out_signal_last = out_signal
            #
            #     if record_count % 500 == 0:
            #         y = np.array(record_datas)
            #         if y.shape[0] < 2000:
            #             y_vec = y[:, 2]
            #             size = y_vec.shape[0]
            #             x_vec = np.linspace(0,size,size+1)[0:-1]
            #             lv_ploter.live_plotter(x_vec, y_vec)
            #         else:
            #             size = 2000
            #             x_vec = np.linspace(0,size,size+1)[0:-1]
            #             y_vec = y[-2000:, 2]
            #             lv_ploter.live_plotter(x_vec, y_vec)
            # # 每5min清空一次数据
            # if record_count > 1000*60*5:
            #     time = time_now.strftime("%Y%m%d_%H%M%S_%f")
            #     async_write(np.array(record_datas), time + "_all")
            #     record_datas=[]
            #     record_count=0


if __name__ == "__main__":
    ComThread.print_list_ports()

    # ser = ComThread("/dev/pts/8", 115200, 0.5)
    # ser = ComThread("/dev/pts/9", 230400, 0.5)

    ser = ComThread("/dev/ttyUSB0", 230400, 0.5)
    if ser.is_open:
        ser.start_read(datas_handle)
        print(f"Start reading.")

        while True:
            sleep(1)
