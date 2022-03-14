import serial
import time


def run():
    data = []
    print("Started at ", time.strftime("%H:%M:%S:%m"))
    with open("data.csv", "a") as f:
        # f.write("valve,flow,direction,step,touch,epoch,time\n")

        with serial.Serial('/dev/ttyUSB0', baudrate=115200) as ser:
            valve_str = "val{}\n"
            for valve in range(219, 231, 1):
                print(f"VALVE: {valve}")
                ser.write(b"val225\n")
                time.sleep(5)
                ser.write(b"val0\n")
                time.sleep(3)
                ser.write(valve_str.format(valve).encode())
                time.sleep(3)
                z_counter = 5
                while z_counter != 0:

                    step = 0
                    direction = "f"
                    while step != 20:
                        ser.write(b"low1000\n")
                        time.sleep(0.2)
                        ser.write(b"flow\n")
                        flow = ser.read_all().decode().strip()
                        if step >= 10:
                            touch = 1
                        else:
                            touch = 0
                        x = (valve, flow, direction, step, touch, z_counter, time.strftime("%H:%M:%S:%m"))
                        f.write(",".join([f'{j}' for j in x]))
                        f.write("\n")
                        step += 1
                        print(x)

                    direction = "b"
                    while step != 40:
                        ser.write(b"top1000\n")
                        time.sleep(0.2)
                        ser.write(b"flow\n")
                        flow = ser.read_all().decode().strip()
                        if step <= 30:
                            touch = 1
                        else:
                            touch = 0
                        x = (valve, flow, direction, step, touch, z_counter, time.strftime("%H:%M:%S:%m"))
                        f.write(", ".join([f'{j}' for j in x]))
                        f.write("\n")

                        step += 1
                        print(x)

                    z_counter -= 1
    return data


if __name__ == "__main__":
    d = run()



"""
"led_on"
"led_off"
"get_steps"
"do_init" - init каретку
"get_velocity"
"flow" - get flow
"vel" - set_velocity
"val"
"top"
"low"


"""