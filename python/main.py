import serial
import time

def run():
    ser = serial.Serial('/dev/ttyUSB0')
    print("Starting cycle")

    while True:
        print("Moving forward")
        ser.write(b"1")
        ser.write(b"3")
        time.sleep(20)
        print("Moving backward")
        ser.write(b"0")
        ser.write(b"2")
        time.sleep(20)

    ser.close()

if __name__ == "__main__":
    run()
