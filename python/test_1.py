import serial
import time
from datetime import datetime
import threading
import queue

q = queue.Queue()
ser = serial.Serial('/dev/ttyUSB0', baudrate=115200)
time.sleep(5)
MOVE = 50000
MOVE_DOWN = f"mov{MOVE}\n".encode()
MOVE_UP = f"mov-{MOVE}\n".encode()

i = iter(
    [

    (0.1, 1.0),
        (0.25, 1.0),
        (0.5, 1.0),
        (1, 1.0),

        (0.1, 1.25),
        (0.25, 1.25),
        (0.5, 1.25),
        (1, 1.25),

        (0.1, 1.5),
        (0.25, 1.5),
        (0.5, 1.5),
        (1, 1.5),

        (0.1, 1.75),
        (0.25, 1.75),
        (0.5, 1.75),
        (1, 1.75),

        (0.1, 2.0),
        (0.25, 2.0),
        (0.5, 2.0),
        (1, 2.0),

        (0.1, 2.25),
        (0.25, 2.25),
        (0.5, 2.25),
        (1, 2.25),

        (0.1, 2.5),
        (0.25, 2.5),
        (0.5, 2.5),
        (1, 2.5),

        (0.1, 2.75),
        (0.25, 2.75),
        (0.5, 2.75),
        (1, 2.75),

        (0.1, 3.0),
        (0.25, 3.0),
        (0.5, 3.0),
        (1, 3.0),

        (0.1, 3.25),
        (0.25, 3.25),
        (0.5, 3.25),
        (1, 3.25),

        (0.1, 3.5),
        (0.25, 3.5),
        (0.5, 3.5),
        (1, 3.5),

        (0.1, 3.75),
        (0.25, 3.75),
        (0.5, 3.75),
        (1, 3.75),

        (0.1, 4.0),
        (0.25, 4.0),
        (0.5, 4.0),
        (1, 4.0),

        (0.1, 4.25),
        (0.25, 4.25),
        (0.5, 4.25),
        (1, 4.25),

        (0.1, 4.5),
        (0.25, 4.5),
        (0.5, 4.5),
        (1, 4.5),

        (0.1, 4.75),
        (0.25, 4.75),
        (0.5, 4.75),
        (1, 4.75),

        (0.1, 5.0),
        (0.25, 5.0),
        (0.5, 5.0),
        (1, 5.0),

        (0.1, 5.25),
        (0.25, 5.25),
        (0.5, 5.25),
        (1, 5.25),

        (0.1, 5.5),
        (0.25, 5.5),
        (0.5, 5.5),
        (1, 5.5),

        (0.1, 5.75),
        (0.25, 5.75),
        (0.5, 5.75),
        (1, 5.75),

        (0.1, 6.0),
        (0.25, 6.0),
        (0.5, 6.0),
        (1, 6.0),            ]
)

DATA = None
file = open("test_data.csv", "a")
file.write("zero,is_flow_start,diff_pa_aver,press_shift_pa,press_aim_pa,time")
file.write("\n")


class ReadingThread(threading.Thread):
    def run(self):
        global file
        while True:
            try:
                data = ser.read_all().decode().strip().split(" ")
                if len(data) > 1 and DATA is not None:
                    k = ",".join(data + DATA + [datetime.now().strftime("%H:%M:%S.%f")[:-3]])
                    print(k)
                    file.write(k)
                    file.write("\n")
            except KeyboardInterrupt:
                file.close()

class WritingThread(threading.Thread):
    def run(self):

        while True:
            try:
                global DATA, i, MOVE_UP, MOVE_DOWN

                shift, value = next(i)
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
            time.sleep(30)
            ser.write(b"pid0\n")
            time.sleep(3)
            ser.write(MOVE_DOWN)
            time.sleep(10)
            ser.write(b"snd0\n")
            ser.write(MOVE_UP)
            time.sleep(10)


if __name__ == "__main__":
    reading = ReadingThread()
    writing = WritingThread()
    reading.start()
    writing.start()
    reading.join()
    writing.join()
