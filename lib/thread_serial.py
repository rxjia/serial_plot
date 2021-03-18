import threading
import time
from queue import Queue, Empty

import serial
import serial.tools.list_ports


class ComThread():
    def __init__(self, com, bps, timeout):
        """初始化"""
        self.port = com
        self.bps = bps
        self.timeout = timeout
        self.is_open = False
        self.alive = False
        self.thread_read = None
        self.ser = None
        self.q_in = Queue(20)
        try:
            # 打开串口，并得到串口对象
            self.ser = serial.Serial(self.port, self.bps, timeout=self.timeout)
            # 判断是否打开成功
            self.is_open = self.ser.is_open
        except Exception as e:
            print("---异常---：", e)
            return

        if self.is_open:
            print(f"Open serial \"{self.ser.port}\" success!")
        else:
            print(f"Open serial {self.ser.port} failed!")

    def print_cur_info(self):
        """打印设备基本信息"""
        print(self.ser.name)  # 设备名字
        print(self.ser.port)  # 读或者写端口
        print(self.ser.baudrate)  # 波特率
        print(self.ser.bytesize)  # 字节大小
        print(self.ser.parity)  # 校验位
        print(self.ser.stopbits)  # 停止位
        print(self.ser.timeout)  # 读超时设置
        print(self.ser.writeTimeout)  # 写超时
        print(self.ser.xonxoff)  # 软件流控
        print(self.ser.rtscts)  # 软件流控
        print(self.ser.dsrdtr)  # 硬件流控
        print(self.ser.interCharTimeout)  # 字符间隔超时

    def open(self):
        """打开串口"""
        if not self.is_open:
            self.open()
            self.is_open = self.ser.is_open

    def close(self):
        """关闭串口"""
        if self.ser.is_open:
            self.ser.close()

    @staticmethod
    def print_list_ports():
        """打印可用串口列表"""
        port_list = list(serial.tools.list_ports.comports())
        print("list_ports: {}".format(port_list))

    def readbytes(self, size):
        """从串口读size个字节。如果指定超时，则可能在超时后返回较少的字节；如果没有指定超时，则会一直等到收完指定的字节数。"""
        return self.ser.read(size=size)

    def readline(self):
        """
        接收一行数据
        使用readline()时应该注意：打开串口时应该指定超时，否则如果串口没有收到新行，则会一直等待。
        如果没有超时，readline会报异常。
        """
        return self.ser.readline()

    def send(self, data):
        """发数据"""
        return self.ser.write(data)

    # 更多示例
    # self.ser.write(chr(0x06).encode("utf-8")) # 十六制发送一个数据
    # print(self.ser.read().hex()) # # 十六进制的读取读一个字节
    # print(self.ser.read())#读一个字节
    # print(self.ser.read(10).decode("gbk"))#读十个字节
    # print(self.ser.readline().decode("gbk"))#读一行
    # print(self.ser.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
    # print(self.ser.in_waiting)#获取输入缓冲区的剩余字节数
    # print(self.ser.out_waiting)#获取输出缓冲区的字节数
    # print(self.ser.readall())#读取全部字符。

    def recieve(self, way):
        """
        接收数据
        @param way:     0: 一个字节一个字节的接收; 1: 整体接收
        """
        # 循环接收数据，此为死循环，可用线程实现
        print("开始接收数据：")
        while True:
            try:
                if self.ser.in_waiting:
                    if way == 0:
                        for i in range(self.ser.in_waiting):
                            print("接收ascii数据：" + str(self.readbytes(1)))
                            data1 = self.readbytes(1).hex()  # 转为十六进制
                            data2 = int(data1, 16)  # 转为十进制
                            if data2 == "exit":  # 退出标志
                                break
                            else:
                                print("收到数据十六进制：" + data1 + " 收到数据十进制：" + str(data2))

                    if way == 1:
                        # data = self.ser.read(self.ser.in_waiting).decode("utf-8")#方式一
                        data = self.ser.read_all()  # 方式二
                        if data == "exit":  # 退出标志
                            break
                        else:
                            print("接收ascii数据：", data)
            except Exception as e:
                print("异常报错：", e)

    # 多线程
    def run_read(self):
        """数据读取"""
        while self.alive:
            n = self.ser.inWaiting()
            if n:
                data = self.ser.read_all()
                self.q_in.put(data)
                # print("接收ascii数据：", data)
            time.sleep(0.001)

    def run_handle(self, datas_handle_func):
        """数据处理"""
        if datas_handle_func is not None:
            while self.alive:
                try:
                    datas = self.q_in.get(timeout=1)
                except Empty as e:
                    continue
                datas_handle_func(datas)
        else:
            while self.alive:
                try:
                    datas = self.q_in.get(timeout=1)
                except Empty as e:
                    continue
                print("Rec: {}".format(datas))

    def start_read(self, datas_handle_func=None):
        while not self.q_in.empty():
            self.q_in.get()

        self.open()
        self.alive = True

        self.thread_handle = threading.Thread(target=self.run_handle, args=(datas_handle_func,))
        self.thread_handle.setDaemon(True)
        self.thread_handle.start()

        self.thread_read = threading.Thread(target=self.run_read)
        self.thread_read.setDaemon(True)
        self.thread_read.start()

    def stop_read(self):
        if self.alive:
            self.alive = False
            self.thread_handle.join()
            self.thread_read.join()
        if self.ser.is_open:
            self.close()


def datas_handle(datas):
    print("datas: {}".format(''.join(['%02x ' % b for b in datas])))


if __name__ == "__main__":
    ComThread.print_list_ports()

    # ser = ComThread("/dev/ttyACM0", 921600, 0.5)
    ser = ComThread("/dev/ttyUSB0", 115200, 0.5)
    if ser.is_open:
        ser.start_read(datas_handle)
        print(f"Start reading.")

        while True:
            time.sleep(1)
