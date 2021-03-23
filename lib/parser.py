from enum import unique, Enum
from queue import Queue

import numpy as np

from lib.circular_queue import CircularQueue
from lib.crc16 import crc16

import logging

logger = logging.getLogger(__file__)
logger.setLevel(logging.WARNING)
"""
    数据头：   7F FE
    数据长度： 05
    数据正文： 01 02 03 04 05
    校验：    93 04
"""

data_header = [0x7f, 0xfe]


@unique
class ParserResult(Enum):
    FALSE = 0
    TRUE = 1


@unique
class ParseState(Enum):
    WaitHeader = 0
    WaitDLC = 1
    WaitData = 2
    WaitCheck = 3


class DataParser:
    def __init__(self, _data_header=data_header):
        self._data_header = data_header
        self._header_size = len(self._data_header)
        self.dlc = 0

        self.parser_queue = CircularQueue(256)
        self.data_len_all = 0
        self.idx = 0

        self.result_pointer_index = 0
        self.parserResult = False
        self.state = ParseState.WaitHeader

        self.data = None  # one pack

    def parser_put_data(self, data):
        # self.data_all = None  # multi pack  (m packs, n data)

        # self.queue[self.idx] = data
        # self.idx += 1
        # if self.idx == 256:
        #     self.idx = 0
        #     print("err: data buf full")
        self.parser_queue.enqueue(data)
        # logger.info(f"byte: {data:02X}, all: {self.parser_queue.showhex(False)}")

        while True:
            cur_len = self.parser_queue.cur_len()
            if self.state == ParseState.WaitHeader:
                if cur_len < self._header_size:
                    return False

                check = True
                for i in range(self._header_size):
                    if self.parser_queue[i] != self._data_header[i]:
                        self.parser_queue.remove(i + 1)  # remove wrong header
                        check = False
                        break

                if check:
                    self.state = ParseState.WaitDLC  # header check success
                    logger.info(f"ParseState.WaitDLC, {self.parser_queue.showhex(False)}")
            elif self.state == ParseState.WaitDLC:
                if cur_len < self._header_size + 1:
                    return False

                self.dlc = self.parser_queue[self._header_size]
                self.data_len_all = self._header_size + 1 + self.dlc + 2  # 2: data for check
                self.data = np.zeros(int(self.dlc / 2), np.int16)
                self.state = ParseState.WaitData
                logger.info("ParseState.WaitData")
            elif self.state == ParseState.WaitData:
                if cur_len < self.data_len_all:
                    return False

                logger.info("ParseState checkdata")
                if cur_len == self.data_len_all:
                    idx_s = self._header_size + 1

                    # crc check -----
                    raw_datas = np.zeros(self.dlc, np.uint8)
                    for i in range(self.dlc):
                        raw_datas[i] = self.parser_queue[idx_s + i]
                    crc_read = np.uint16(
                        self.parser_queue[self.data_len_all - 2] << 8 | self.parser_queue[self.data_len_all - 1])
                    crc_cal = crc16(raw_datas, self.dlc)
                    # print(f"0x{crc_read:X}, 0x{crc_cal:X}")
                    # print("raw_datas: {}".format(''.join(['%02X ' % b for b in raw_datas])))

                    if crc_read == crc_cal:
                        for i in range(int(self.dlc / 2)):
                            self.data[i] = np.int16(
                                (self.parser_queue[idx_s + i * 2] << 8) + self.parser_queue[idx_s + i * 2 + 1])

                        self.state = ParseState.WaitHeader
                        self.parser_queue.remove(self.data_len_all)
                        logger.info(f"crc ok, cur_len:{self.parser_queue.cur_len()}")
                        return True
                    else:
                        logger.warning(
                            f"crc fail, len: {self.parser_queue.cur_len()},  raw_datas: {''.join(['%02X ' % b for b in raw_datas])}")

                        self.parser_queue.remove(2)
                        self.state = ParseState.WaitHeader
                        continue

                elif cur_len > self.data_len_all:
                    # remove header
                    logger.warning(f"len > all, remove header,{self.parser_queue.showhex(False)}")

                    self.parser_queue.remove(2)
                    self.state = ParseState.WaitHeader
                    continue

    def get_data(self):
        return self.data.copy()

    def parser_get_data(self, index):
        return self.parser_queue[self.result_pointer_index + index]

    def get_int16_data(self, index):
        return np.int16((self.parser_get_data(index * 2) << 8) + self.parser_get_data(index * 2 + 1))
