import serial
import time
from datetime import datetime
import threading
import queue

q = queue.Queue()
ser = serial.Serial('/dev/ttyUSB0', baudrate=115200)
time.sleep(5)
MOVE = 70_400
MOVE_DOWN = f"mov{MOVE}\n".encode()
MOVE_UP = f"mov-{MOVE}\n".encode()
EPOCH = 0

i = iter(
    [

        (0.25, 1.0),
        (0.25, 1.25),
        (0.25, 1.5),
        (0.25, 1.75),
        (0.25, 2.0),
        (0.25, 2.25),
        (0.25, 2.5),
        (0.25, 2.75),
        (0.25, 3.0),
        (0.25, 3.25),
        (0.25, 3.5),
        (0.25, 3.75),
        (0.25, 4.0),
        (0.25, 4.25),
        (0.25, 4.5),
        (0.25, 4.75),
        (0.25, 5.0),
        (0.25, 5.25),
        (0.25, 5.5),
        (0.25, 5.75),
        (0.25, 6.0),
    ]
)

DATA = None
file = open("test_data_025_125_20_sharp_needle_soap.csv", "a")
file.write("epoch,mkm_passed,zero,steps,diff_pa_aver,press_shift_pa,press_aim_pa,time")
file.write("\n")


class ReadingThread(threading.Thread):
    def run(self):
        global file, EPOCH
        while True:
            try:
                data = ser.read_all().decode().strip().split(" ")
                if len(data) > 1 and DATA is not None:
                    mkm = str(int(data[1]) * 10 / 64)
                    k = ",".join([str(EPOCH), mkm] + data + DATA + [datetime.now().strftime("%H:%M:%S.%f")[:-3]])
                    print(k)
                    file.write(k)
                    file.write("\n")
            except KeyboardInterrupt:
                file.close()

class WritingThread(threading.Thread):
    def run(self):
        counter = 0
        while counter < 20:
            try:
                global DATA, i, MOVE_UP, MOVE_DOWN, EPOCH

                shift, value = 0.25, 1.25  # next(i)
                DATA = [str(shift), str(value)]

                data = ("thr%s\n" % value).encode()
                shift_data = ("bnd%s\n" % shift).encode()

                ser.write(data)
                time.sleep(2)
                ser.write(shift_data)
                time.sleep(2)

            except StopIteration:
                break
            ser.write(b"snd1\n")
            time.sleep(15)
            ser.write(b"pid0\n")
            time.sleep(3)
            ser.write(MOVE_DOWN)
            time.sleep(25)
            ser.write(b"snd0\n")

            ser.write(MOVE_UP)
            time.sleep(5)
            ser.write(b"val255\n")
            time.sleep(5)
            ser.write(b"val0\n")
            time.sleep(10)
            counter += 1
            EPOCH += 1
        print("End")

if __name__ == "__main__":
    reading = ReadingThread()
    writing = WritingThread()
    reading.start()
    writing.start()
    reading.join()
    writing.join()
