# -*- coding: utf-8 -*-
import math
import sys
import time
import serial
from serial.tools import list_ports

import datetime
import os

import threading

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from io import StringIO
# import pandas as pd

import tkinter as tk
import tkinter.ttk as ttk
from random import randint

# import tkinter.font as tkfont

vbox = False  # Включает режим отладки с задержками для меня в VirtualBox-e. False - реальное оборудование True - отладка без плат
is_graph_update_run = True
is_pid_update_run = True
points_num = 20  # количество точек на графике
graph_update_delay_sec = 0.01  # при построении графика давления добавляется задержка помимо времени на запрос

is_flow_start = False  # флаг показывает, запущен ли поток газа через датчик или нет
is_measurement_start = False  # флаг показывает, начали ли мы измерение касания жидкости
is_touch_surface = False  # флаг касания жидкости

measurement_step = 500  # количество шагов, совершаемых между проверкой давления в датчике при движении иглы вниз
surface_TOTAL_STEPS = 0  # абсолютного положения поверхности жидкости, которая была определена касанием иглы

# --------- Инициализация плат ------------------
def get_usb_ports_list_macos():
    """get all available serial ports in MacOS and return which consists 'usbserial' path"""
    try:
        ports_list = [
            i.device for i in list_ports.comports() if "usb" in i.device
        ]
        return ports_list
    except Exception as e:
        # "ls /dev/tty*" lists all the devices; the one we need is ttyUSB0 or the one with "usbserial"
        print("Error get_serail_ports_list_macos:\t{}".format(e))
        raise Exception(e)


if not vbox:
    port_list = get_usb_ports_list_macos()  # определяю порты

else:
    # работаю в VirtualBox порты назначаю
    port_list = []

# определяем Арудино
arduino_device = serial.Serial(port_list[0], 115200, timeout=5)

# ---------------------- Окно: ------------------------
win = tk.Tk()
win.title('Стенд касания поверхности жидкости')
win.geometry("{0}x{1}+2+3".format(int(win.winfo_screenwidth() * 0.8), int(win.winfo_screenheight() * 0.9)))


def on_closing():
    plt.close("all")  # вместе с окном закрываем матплотлиб
    win.destroy()  # иначе программа не выходит из цикла mainloop


win.protocol("WM_DELETE_WINDOW", on_closing)  # вместе с окном закрываем матплотлиб

# Сюда будем сыпать сообщения
message = tk.StringVar()
messages = tk.Message(master=win, textvariable=message, aspect=10000, anchor='nw', relief='ridge', borderwidth=2)
messages.pack(side='top', anchor='nw', fill='x', padx=5, pady=2)  # expand = 'x')
message.set('ГОТОВ   ' + str(port_list))


# --------------- Раздел « Query Commands » -----------------
frame2 = tk.LabelFrame(master=win, text=' Query Commands ', bd=2)
frame2.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)


def led_on():
    command = 'led_on'
    arduino_device.write(("%s\n" % command).encode('utf-8'))
    # print("command", command)
    return


button2_1 = ttk.Button(master=frame2, text='led_on', command=led_on)
button2_1.pack(side='left', anchor='nw', padx=5, pady=2)


def led_off():
    command = 'led_off'
    arduino_device.write(("%s\n" % command).encode('utf-8'))
    # print("command", command)
    return


button2_2 = ttk.Button(master=frame2, text='led_off', command=led_off)
button2_2.pack(side='left', anchor='nw', padx=5, pady=2)

label2_1 = ttk.Label(master=frame2, text='Параметр:')
label2_1.pack(side='left', anchor='nw', padx=5, pady=2)

entry2_1 = ttk.Entry(master=frame2, width=10)
entry2_1.pack(side='left', anchor='nw', padx=5, pady=4)


def top000():
    param = int(entry2_1.get())
    command = 'top{}'.format(param)
    arduino_device.write(("%s\n" % command).encode('utf-8'))
    print("command", command)


button_2_3 = ttk.Button(master=frame2, text='top000', command=top000)
button_2_3.pack(side='left', anchor='nw', padx=5, pady=2)


def low000():
    param = int(entry2_1.get())
    command = 'low{}'.format(param)
    arduino_device.write(("%s\n" % command).encode('utf-8'))
    print("command", command)


button_2_3 = ttk.Button(master=frame2, text='low000', command=low000)
button_2_3.pack(side='left', anchor='nw', padx=5, pady=2)


def vel000():
    param = int(entry2_1.get())
    command = 'vel{}'.format(param)
    arduino_device.write(("%s\n" % command).encode('utf-8'))


button_2_4 = ttk.Button(master=frame2, text='vel000', command=vel000)
button_2_4.pack(side='left', anchor='nw', padx=5, pady=2)


def val000():
    param = int(entry2_1.get())
    command = 'val{}'.format(param)
    arduino_device.write(("%s\n" % command).encode('utf-8'))


button_2_5 = ttk.Button(master=frame2, text='val000', command=val000)
button_2_5.pack(side='left', anchor='nw', padx=5, pady=2)

##
# query commands #
##
frame4 = tk.LabelFrame(master=win, text=' query commands ', bd=2)
frame4.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)

query_param = tk.DoubleVar()
spinner4_1 = ttk.Spinbox(master=frame4, textvariable=query_param, from_=0.00, to=100000.00, increment=1, width=12)
spinner4_1.pack(side='left', anchor='nw', padx=5, pady=4)
query_param.set(0)


def get_steps(need_answer=False):
    command = 'get_steps'
    arduino_device.write(("%s\n" % command).encode('utf-8'))
    # получаем
    temp_str = arduino_device.readline().decode('utf-8').strip()
    param = int(temp_str)

    query_param.set(param)
    if need_answer:
        return param
    else:
        return


button_4_1 = ttk.Button(master=frame4, text='get_steps', command=get_steps)
button_4_1.pack(side='left', anchor='nw', padx=5, pady=2)


def get_velocity():
    command = 'get_velocity'
    arduino_device.write(("%s\n" % command).encode('utf-8'))
    # получаем
    temp_str = arduino_device.readline().decode('utf-8').strip()
    param = int(temp_str)

    query_param.set(param)
    return


button_4_2 = ttk.Button(master=frame4, text='get_velocity', command=get_velocity)
button_4_2.pack(side='left', anchor='nw', padx=5, pady=2)


def get_valve_value(need_answer=False):
    command = 'get_valve_value'
    arduino_device.write(("%s\n" % command).encode('utf-8'))
    # получаем
    temp_str = arduino_device.readline().decode('utf-8').strip()
    param = int(temp_str)

    query_param.set(param)
    if need_answer:
        return param
    else:
        return


button_4_3 = ttk.Button(master=frame4, text='get_valve_value', command=get_valve_value)
button_4_3.pack(side='left', anchor='nw', padx=5, pady=2)


label4_1 = ttk.Label(master=frame4, text='Усреднение давления:')
label4_1.pack(side='left', anchor='nw', padx=5, pady=2)

aver_param = tk.DoubleVar()
spinner4_2 = ttk.Spinbox(master=frame4, textvariable=aver_param, from_=1.00, to=100000.00, increment=1, width=6)
spinner4_2.pack(side='left', anchor='nw', padx=5, pady=4)
aver_param.set(2)


def get_flow_pa_aver000():
    param = int(aver_param.get())
    command = 'gfa{}'.format(param)
    arduino_device.write(("%s\n" % command).encode('utf-8'))
    # получаем
    temp_str = arduino_device.readline().decode('utf-8').strip()
    param = int(float(temp_str))

    query_param.set(param)
    return


button_4_4 = ttk.Button(master=frame4, text='get_flow_pa_aver000', command=get_flow_pa_aver000)
button_4_4.pack(side='left', anchor='nw', padx=5, pady=2)

##
# PID #
##
frame5 = tk.LabelFrame(master=win, text=' PID ', bd=2)
frame5.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)

label5_1 = ttk.Label(master=frame5, text='Среднее, Па')
label5_1.pack(side='left', anchor='nw', padx=5, pady=2)

aver_pressure_pa_param = tk.DoubleVar()
spinner5_1 = ttk.Spinbox(master=frame5, textvariable=aver_pressure_pa_param, from_=0.00, to=15.00, increment=0.1, width=6)
spinner5_1.pack(side='left', anchor='nw', padx=5, pady=4)
aver_pressure_pa_param.set(6)

label5_2 = ttk.Label(master=frame5, text='дельта, Па')
label5_2.pack(side='left', anchor='nw', padx=5, pady=2)

d_pressure_pa_param = tk.DoubleVar()
spinner5_2 = ttk.Spinbox(master=frame5, textvariable=d_pressure_pa_param, from_=0.00, to=5.00, increment=0.1, width=6)
spinner5_2.pack(side='left', anchor='nw', padx=5, pady=4)
d_pressure_pa_param.set(4.0)


def pid_flow_control(pressure_aver_pa):
    global is_flow_start
    value_aver_pressure_pa_param = float(aver_pressure_pa_param.get())
    value_d_pressure_pa_param = float(d_pressure_pa_param.get())

    # first fast opening valve
    if abs(pressure_aver_pa) < 1.0:
        is_flow_start = False
        # get current value valve
        valve_open_pwm_bit = get_valve_value(need_answer=True)
        # change opening of valve
        if valve_open_pwm_bit < 180:
            valve_open_pwm_bit = 180
        param = valve_open_pwm_bit + 2
        command = 'val{}'.format(param)
        arduino_device.write(("%s\n" % command).encode('utf-8'))
        # indicate new value in UI
        get_valve_value(need_answer=False)
        # print("PID fast")
        return
    else:
        is_flow_start = True

    # pressure too low
    if pressure_aver_pa < value_aver_pressure_pa_param - value_d_pressure_pa_param/2.:
        # get current value valve
        valve_open_pwm_bit = get_valve_value(need_answer=True)
        # change opening of valve
        param = valve_open_pwm_bit + 1
        command = 'val{}'.format(param)
        arduino_device.write(("%s\n" % command).encode('utf-8'))
        # indicate new value in UI
        get_valve_value(need_answer=False)
        # print("PID up")

    # pressure too high
    if pressure_aver_pa > value_aver_pressure_pa_param + value_d_pressure_pa_param / 2.:
        # get current value valve
        valve_open_pwm_bit = get_valve_value(need_answer=True)
        # change opening of valve
        param = valve_open_pwm_bit - 1
        command = 'val{}'.format(param)
        arduino_device.write(("%s\n" % command).encode('utf-8'))
        # indicate new value in UI
        get_valve_value(need_answer=False)
        # print("PID down")

    return

y_surface_ar_mm = []  # значения поверхности
def surface_control(pressure_aver_pa):
    """
    Функция должна сравнивать давление и если давление стало ниже 1 Па сообщать о факте касания поверхности.
    После этого выполняются необходимые шаги для извлечения иглы и очистки ее от жидкости, чтобы не началось пузырение
    и можно было начать очередное измерение
    :param pressure_aver_pa:
    :return:
    """
    global is_touch_surface, surface_TOTAL_STEPS, is_measurement_start, y_surface_ar_mm
    lift_up_steps = 10000  # на сколько поднимать иглу после касания
    # no surface
    if pressure_aver_pa > 1:
        return
    else:
        # there is sorface touch
        is_touch_surface = True
        # save surface steps
        surface_TOTAL_STEPS = get_steps(need_answer=True)
        print("surface_TOTAL_STEPS = {}\t{:.2f} mm".format(surface_TOTAL_STEPS, float(surface_TOTAL_STEPS/6400.)))
        # lift up the needle
        command = 'top{}'.format(lift_up_steps)
        arduino_device.write(("%s\n" % command).encode('utf-8'))

        # save valve value before cleaning
        valve_open_pwm_bit_work = get_valve_value(need_answer=True)
        # needle cleaning
        while True:
            # get pressure_aver
            param = int(aver_param.get())
            command = 'gfa{}'.format(param)
            arduino_device.write(("%s\n" % command).encode('utf-8'))
            # получаем valve value
            temp_str = arduino_device.readline().decode('utf-8').strip()
            pressure_aver_pa = float(temp_str)

            if pressure_aver_pa > 1:
                # needle is empty
                # change opening of valve
                param = valve_open_pwm_bit_work
                command = 'val{}'.format(param)
                arduino_device.write(("%s\n" % command).encode('utf-8'))
                # indicate new value in UI
                get_valve_value(need_answer=False)
                # print("needle is empty")
                break
            else:
                # the needle is still closed
                valve_open_pwm_bit = get_valve_value(need_answer=True)
                # change opening of valve
                param = valve_open_pwm_bit + 2
                command = 'val{}'.format(param)
                arduino_device.write(("%s\n" % command).encode('utf-8'))
                # indicate new value in UI
                get_valve_value(need_answer=False)
                # print("the needle is still closed")
            time.sleep(0.1)

        is_touch_surface = False
        is_measurement_start = False

        # --------- рисование графика -------------
        # y_ar.append(randint(0, 10))
        y_surface_ar_mm.append(float(surface_TOTAL_STEPS/6400.))

        figure_2.clf()  # затереть старые графики
        ax_f2 = figure_2.add_subplot(111)  # новая область рисования графика
        ax_f2.set_title("title name")

        ax_f2.plot(y_surface_ar_mm, marker='x')

        ax_f2.grid(which='major', linewidth=1.2)  # сетка
        ax_f2.tick_params(which='major', length=10, width=2)

        chart_2.draw()  # отрисовать

        return


def start_pid():
    go_down_steps = 640*0.5  # на сколько шагов двигаться вниз при поиске поверхности. 640 шагов - 0.1 мм
    try:
        global is_pid_update_run
        is_pid_update_run = True

        y_ar = []  # значения давления на графике
        y0_ar = []  # для нулевой линии на графике
        yhigh_ar = []
        ylow_ar = []

        time_pid_sec = time.time()  # время очередной проверки ПИД
        time_pid_delay_sec = 2  # как часто проверять ПИД
        while True:
            if not is_pid_update_run:
                return

            if is_measurement_start:
                # go down the needle
                command = 'low{}'.format(go_down_steps)
                arduino_device.write(("%s\n" % command).encode('utf-8'))
            # get pressure_aver
            param = int(aver_param.get())
            command = 'gfa{}'.format(param)
            arduino_device.write(("%s\n" % command).encode('utf-8'))
            # получаем
            temp_str = arduino_device.readline().decode('utf-8').strip()
            pressure_aver_pa = float(temp_str)

            # --------- рисование графика -------------
            # y_ar.append(randint(0, 10))
            y_ar.append(pressure_aver_pa)
            y0_ar.append(0)
            yhigh_ar.append(float(aver_pressure_pa_param.get()) + float(d_pressure_pa_param.get())/2)
            ylow_ar.append(float(aver_pressure_pa_param.get()) - float(d_pressure_pa_param.get())/2)
            if len(y_ar) > points_num:
                y_ar.pop(0)
                y0_ar.pop(0)
                yhigh_ar.pop(0)
                ylow_ar.pop(0)

            figure.clf()  # затереть старые графики
            ax = figure.add_subplot(111)  # новая область рисования графика
            ax.set_title("title name")

            ax.plot(y_ar, marker='x')
            ax.plot(y0_ar, marker='o')
            ax.plot(yhigh_ar, marker='.')
            ax.plot(ylow_ar, marker='.')

            ax.grid(which='major', linewidth=1.2)  # сетка
            ax.tick_params(which='major', length=5, width=2)

            chart.draw()  # отрисовать
            if is_measurement_start:
                surface_control(pressure_aver_pa)
            time.sleep(graph_update_delay_sec)

            if time.time() - time_pid_sec > time_pid_delay_sec or not is_measurement_start:
                pid_flow_control(pressure_aver_pa)
                time_pid_sec = time.time()  # время очередной проверки ПИД


    except Exception as e:
        print(e)


button_5_1 = ttk.Button(master=frame5, text='start_PID', command=lambda: threading.Thread(target=start_pid).start())
# button_5_1 = ttk.Button(master=frame5, text='start_PID', command=start_pid)
button_5_1.pack(side='left', anchor='nw', padx=5, pady=2)


def stop_pid():
    global is_pid_update_run
    is_pid_update_run = False
    return


button_5_2 = ttk.Button(master=frame5, text='stop_pid', command=stop_pid)
button_5_2.pack(side='left', anchor='nw', padx=5, pady=2)

label5_3 = ttk.Label(master=frame5, text='Только давление')
label5_3.pack(side='left', anchor='nw', padx=5, pady=2)


def start_pressure():
    try:
        global is_graph_update_run
        is_graph_update_run = True

        y_ar = []  # значения давления на графике
        y0_ar = []  # для нулевой линии на графике
        # for i in range(10):
        #     xar.append(i)
        # for i in range(10):
        #     yar.append(randint(0, 10))
        while True:

            if not is_graph_update_run:
                return

            # get pressure_aver
            param = int(aver_param.get())
            command = 'gfa{}'.format(param)
            arduino_device.write(("%s\n" % command).encode('utf-8'))
            # получаем
            temp_str = arduino_device.readline().decode('utf-8').strip()
            pressure_aver_pa = float(temp_str)

            # --------- рисование графика -------------
            # y_ar.append(randint(0, 10))
            y_ar.append(pressure_aver_pa)
            y0_ar.append(0)
            if len(y_ar) > points_num:
                y_ar.pop(0)
                y0_ar.pop(0)

            figure.clf()  # затереть старые графики
            ax = figure.add_subplot(111)  # новая область рисования графика
            ax.set_title("title name")

            ax.plot(y_ar, marker='x')
            ax.plot(y0_ar, marker='o')

            ax.grid(which='major', linewidth=1.2)  # сетка
            ax.tick_params(which='major', length=10, width=2)

            chart.draw()  # отрисовать

            time.sleep(graph_update_delay_sec)

    except Exception as e:
        print(e)


button_5_3 = ttk.Button(master=frame5, text='start_pressure', command=lambda: threading.Thread(target=start_pressure).start())
#button_5_3 = ttk.Button(master=frame5, text='start_pressure', command=start_pressure)
button_5_3.pack(side='left', anchor='nw', padx=5, pady=2)


def stop_pressure():
    global is_graph_update_run
    is_graph_update_run = False
    return


button_5_4 = ttk.Button(master=frame5, text='stop_pressure', command=stop_pressure)
button_5_4.pack(side='left', anchor='nw', padx=5, pady=2)


##
# measurement #
##
frame6 = tk.LabelFrame(master=win, text=' Measurement ', bd=2)
frame6.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)


def start_measurement():
    global is_measurement_start
    is_measurement_start = True
    return


button_6_1 = ttk.Button(master=frame6, text='start_measurement', command=start_measurement)
button_6_1.pack(side='left', anchor='nw', padx=5, pady=2)


def stop_measurement():
    global is_measurement_start
    is_measurement_start = False
    return


button_6_2 = ttk.Button(master=frame6, text='stop_measurement', command=stop_measurement)
button_6_2.pack(side='left', anchor='nw', padx=5, pady=2)

# # --------------- Раздел « Параметры эксперимента » -----------------
# frame1 = tk.LabelFrame(master=win, text=' Параметры эксперимента ', bd=2)
# frame1.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)
#
# label1 = ttk.Label(master=frame1, text='Образец:')
# label1.pack(side='left', anchor='nw', padx=5, pady=2)
#
# entry1 = ttk.Entry(master=frame1, width=25)
# entry1.pack(side='left', anchor='nw', padx=5, pady=4)
#
# label2 = ttk.Label(master=frame1, text='Напряжение питания электромагнита:')
# label2.pack(side='left', anchor='nw', padx=5, pady=2)
#
# em_voltage = tk.DoubleVar()  # переменная связанная со спиннером
# spinner1 = ttk.Spinbox(master=frame1, textvariable=em_voltage, from_=0.00, to=100.00, increment=0.01, width=8)
# spinner1.pack(side='left', anchor='nw', padx=5, pady=4)
#
# graph_param = tk.BooleanVar()
# graph_param.set(True)
# r_spros_1 = ttk.Radiobutton(frame1, text='Сырые данные', variable=graph_param, value=0).pack(side='left', anchor='nw',
#                                                                                              padx=1, pady=2)
# r_spros_2 = ttk.Radiobutton(frame1, text='Напряжение и поле', variable=graph_param, value=1).pack(side='left',
#                                                                                                   anchor='nw', padx=1,
#                                                                                                   pady=2)
#
# tabs = ttk.Notebook(master=win)  # Вкладки
#
# # Вкладка 1:
# tab1 = ttk.Frame(master=tabs)
# tabs.add(tab1, text='Графики на одной частоте')
#
# # ---------------- Раздел « Параметры плат Ардуино » -----------------
# frame2 = tk.LabelFrame(master=tab1, text=' Параметры плат Ардуино ', bd=2)
# frame2.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)
#
# label3 = ttk.Label(master=frame2, text='Частота генератора:')
# label3.pack(side='left', anchor='nw', padx=5, pady=2)
#
# freq_set = tk.DoubleVar()  # переменная связанная со спиннером spinner2
# spinner2 = ttk.Spinbox(master=frame2, textvariable=freq_set, from_=0.00, to=100000.00, increment=0.1, width=15)
# spinner2.pack(side='left', anchor='nw', padx=5, pady=4)
#
#
# def gen_freq_set(freq_set):
#     # установить частоту
#     generator.flushInput()  # сброс входного буфера
#     generator.flushOutput()
#
#     if exp_shift_period.get() == 0:
#         command = 'sf' + str(int(freq_set)).strip()
#     else:
#         command = 'sx' + str(int(freq_set)).strip()
#     generator.write(("%s\n" % command).encode('utf-8'))
#     # print("command", command)
#     win.after(100)  # задержка 0,1 сек.
#
#     # получаем отклик
#     response = generator.readline().decode(
#         'utf-8')  # В случае успешного выполнения команды плата вернет реально установленную частоту
#     win.after(100)  # задержка 0,1 сек.
#     ##generator.reset_input_buffer()  # сброс входного буфера
#     # print('response1',response)
#
#     # запрос частоты
#     generator.flushInput()  # сброс входного буфера
#     command = 'gf'
#     generator.write(("%s\n" % command).encode('utf-8'))
#     win.after(100)  # задержка 0,1 сек.
#     ##generator.reset_output_buffer() # сброс выходного буфера
#
#     # получаем реальную частоту
#     temp_str = generator.readline().decode('utf-8').strip()
#     # print("temp_str ", temp_str)
#     freq = float(temp_str)
#     # freq = float(generator.readline().decode('utf-8').strip())
#     win.after(100)  # задержка 0,1 сек.
#     ##generator.reset_input_buffer()  # сброс входного буфера
#
#     return freq
#
#
# def checkbutton_exp_shift_period():
#     ''' функция при смене чекбокса на Сдвиг включения '''
#     freq = 0
#     if freq_set.get() == 0:
#         freq = gen_freq_set(25)
#     else:
#         freq = gen_freq_set(freq_set.get())
#
#     # print('freq',freq)
#     freq_get.set(freq)
#     message.set('ПОЛУЧЕНА ЧАСТОТА  ' + str(freq) + ' HZ')
#
#
# exp_shift_period = tk.BooleanVar()
# exp_shift_period.set(0)
# c3 = ttk.Checkbutton(frame1, text="Сдвиг включения", variable=exp_shift_period, onvalue=1, offvalue=0,
#                      command=checkbutton_exp_shift_period).pack(side='left', anchor='nw', padx=10, pady=2)
#
#
# def button_set_clck():
#     ''' Процедура получения реальной частоты генератора '''
#     message.set('ОЖИДАНИЕ ПОЛУЧЕНИЯ ЧАСТОТЫ')
#     win.update_idletasks()
#
#     freq = gen_freq_set(freq_set.get())
#     # print('freq',freq)
#     freq_get.set(freq)
#     message.set('ПОЛУЧЕНА ЧАСТОТА  ' + str(freq) + ' HZ')
#
#
# button_set = ttk.Button(master=frame2, text='Установить', command=button_set_clck)
# button_set.pack(side='left', anchor='nw', padx=5, pady=0)
#
# label4 = ttk.Label(master=frame2, text='Реальная частота генератора:')
# label4.pack(side='left', anchor='nw', padx=5, pady=2)
#
# freq_get = tk.DoubleVar()  # переменная связанная со спиннером spinner3
# spinner3 = ttk.Spinbox(master=frame2, textvariable=freq_get, from_=0.00, to=100000.00, increment=0.01, width=15)
# spinner3.pack(side='left', anchor='nw', padx=5, pady=4)
#
# # ------------------ Раздел « Построить графики » --------------------
# frame3 = tk.LabelFrame(master=tab1, text=' Построить графики ', bd=2)
# frame3.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)
#
# ##graph_param = tk.BooleanVar()
# ##graph_param.set(True)
# ##r_spros_1 = ttk.Radiobutton(frame1, text='Сырые данные', variable=graph_param, value=0).pack(side='left', anchor = 'nw', padx=1, pady=2)
# ##r_spros_2 = ttk.Radiobutton(frame1, text='Напряжение и поле', variable=graph_param, value=1).pack(side='left', anchor = 'nw', padx=1, pady=2)
#
# saveinfile = tk.BooleanVar()
# saveinfile.set(1)
# c1 = ttk.Checkbutton(frame3, text="Сохранить в файл", variable=saveinfile, onvalue=1, offvalue=0).pack(side='left',
#                                                                                                        anchor='nw',
#                                                                                                        padx=10, pady=2)
#
# cut_time = tk.BooleanVar()
# cut_time.set(1)
# c2 = ttk.Checkbutton(frame3, text="Обрезать в период", variable=cut_time, onvalue=1, offvalue=0).pack(side='left',
#                                                                                                       anchor='nw',
#                                                                                                       padx=10, pady=2)
#
#
# def convert_array_df_PVDF(array):
#     temp_data = StringIO(array)  # строку в CSV
#     df_temp = pd.read_csv(temp_data, sep="\t")  # CSV в датафрейм
#     if graph_param.get() == 1:
#         df_temp['PVDF signal'] = df_temp['PVDF signal'].apply(lambda x: x * 0.5)
#         df_temp.rename(columns={'PVDF signal': 'PVDF signal, mV'}, inplace=True)
#     else:
#         df_temp.rename(columns={'PVDF signal': 'PVDF signal, ADC'}, inplace=True)
#     return df_temp
#
#
# def convert_array_df_ampermetr(array):
#     temp_data = StringIO(array)  # строку в CSV
#     df_temp = pd.read_csv(temp_data, sep="\t")  # CSV в датафрейм
#     if graph_param.get() == 1:
#         df_temp['current, mA'] = df_temp['current, mA'].apply(lambda x: x * 0.079)
#         df_temp.rename(columns={'current, mA': 'current, mT'}, inplace=True)
#     else:
#         df_temp.rename(columns={'current, mA': 'current, mA'}, inplace=True)
#
#     return df_temp
#
#
# def save_data_fix_freq(PVDF_df, ampermetr_df):
#     path_temp = os.path.join(path, "fix_freq/")
#     try:
#         os.makedirs(path_temp, exist_ok=True)
#     except Exception as e:
#         print(e)
#     file_name = "{}_{}V_{}Hz_{:%H_%M_%S}.txt".format(entry1.get(), spinner1.get(), freq_get.get(),
#                                                      datetime.datetime.now().time())  # имя файла
#     # print(file_name)
#     file_name = os.path.join(path_temp, file_name)
#     result = pd.concat([PVDF_df, ampermetr_df], axis=1)
#
#     if saveinfile.get() == 1:
#         result.to_csv(file_name, sep="\t", index=False, decimal=",")
#
#
# def save_data_res(res_df, series_df):
#     path_temp = os.path.join(path, "res/")
#     try:
#         os.makedirs(path_temp, exist_ok=True)
#     except Exception as e:
#         print(e)
#     file_name_res = "{:%H_%M_%S}_res_{}_{}V_{}-{}Hz.txt".format(datetime.datetime.now().time(), entry1.get(),
#                                                                 spinner1.get(), freq_start.get(),
#                                                                 freq_finish.get())  # имя файла
#     file_name_series = "{:%H_%M_%S}_series_{}_{}V_{}-{}Hz.txt".format(datetime.datetime.now().time(), entry1.get(),
#                                                                       spinner1.get(), freq_start.get(),
#                                                                       freq_finish.get())  # имя файла
#     # print(file_name)
#     file_name_res = os.path.join(path_temp, file_name_res)
#     file_name_series = os.path.join(path_temp, file_name_series)
#
#     res_df.to_csv(file_name_res, sep="\t", index=False, decimal=",")
#     series_df.to_csv(file_name_series, sep="\t", index=False, decimal=",")
#
#
# # функция вернет два df массива со значениями с датчиков без обрезки но уже с выбором Сырые или напряжение/поле
# def get_mes_arrays(freq):
#     if freq >= 20:
#         # "ampermetr" и "PVDF" в накопление данных в массив array
#         command = "set_arr"
#         PVDF.write(("%s\n" % command).encode('utf-8'))  # Установить режим в накопление данных в массив для PVDF
#         win.after(100)  # задержка 0,1 сек.
#         response = PVDF.readline().decode('utf-8')  # Получить отклик "ok"
#         win.after(100)  # задержка 0,1 сек.
#         # print('PVDF set_arr ',response)
#         ampermetr.write(
#             ("%s\n" % command).encode('utf-8'))  # Установить режим в накопление данных в массив для ampermetr
#         win.after(100)  # задержка 0,1 сек.
#         response = ampermetr.readline().decode('utf-8')  # Получить отклик "ok"
#         win.after(100)  # задержка 0,1 сек.
#         # print('ampermetr set_arr ',response)
#
#         # Запуска процесса измерений
#         ampermetr.flushInput()
#         PVDF.flushInput()
#         command = "synchron"
#         generator.write(("%s\n" % command).encode('utf-8'))  #
#         win.after(100)  # # задержка 0,1 сек.
#         response = generator.readline().decode('utf-8')  # Получить отклик "ok"
#         win.after(100)  # задержка 0,1 сек.
#         # print('generator synchron ',response)
#
#         win.after(1000)  # 1 СЕК. ТАЙМ-АУТ, ЧТОБ ДОЖДАТЬСЯ ОКОНЧАНИЯ ЭКСПЕРИМЕНТА
#
#         PVDF_array = PVDF.read(PVDF.inWaiting()).decode('utf-8').strip()  # Получить массив PVDF
#         ampermetr_array = ampermetr.read(ampermetr.inWaiting()).decode('utf-8').strip()  # прочитать массив ampermetr
#         win.after(100)  # задержка 0,1 сек.
#
#         df_PVDF = convert_array_df_PVDF(PVDF_array)
#         df_ampermetr = convert_array_df_ampermetr(ampermetr_array)
#
#         return df_PVDF, df_ampermetr
#
#     else:
#         message.set('ЧАСТОТА МЕНЬШЕ 20 режим непрерывного измерения')
#         # "ampermetr" и "PVDF" в накопление данных в массив array
#         command = "set_con"
#         PVDF.write(("%s\n" % command).encode('utf-8'))  # Установить режим в непрерывную отправку данных из PVDF
#         win.after(100)  # задержка 0,1 сек.
#         response = PVDF.readline().decode('utf-8')  # Получить отклик "ok"
#         win.after(100)  # задержка 0,1 сек.
#         # print('PVDF set_con ',response)
#         ampermetr.write(
#             ("%s\n" % command).encode('utf-8'))  # Установить режим в непрерывную отправку данных из ampermetr
#         win.after(100)  # задержка 0,1 сек.
#         response = ampermetr.readline().decode('utf-8')  # Получить отклик "ok"
#         win.after(100)  # задержка 0,1 сек.
#         # print('ampermetr set_con ',response)
#
#         # Запуска процесса измерений
#         ampermetr.flushInput()
#         PVDF.flushInput()
#         command = "synchron"
#         generator.write(("%s\n" % command).encode('utf-8'))  #
#         win.after(100)  # # задержка 0,1 сек.
#         response = generator.readline().decode('utf-8')  # Получить отклик "ok"
#         win.after(100)  # задержка 0,1 сек.
#         # print('generator synchron ',response)
#
#         win.after(2000)  # 2 СЕК. ТАЙМ-АУТ, ЧТОБ ДОЖДАТЬСЯ ОКОНЧАНИЯ ЭКСПЕРИМЕНТА
#
#         PVDF_array = PVDF.read(PVDF.inWaiting()).decode('utf-8').strip()  # Получить массив PVDF
#         ampermetr_array = ampermetr.read(ampermetr.inWaiting()).decode('utf-8').strip()  # прочитать массив ampermetr
#         win.after(100)  # задержка 0,1 сек.
#
#         df_PVDF = convert_array_df_PVDF(PVDF_array)
#         df_ampermetr = convert_array_df_ampermetr(ampermetr_array)
#
#         return df_PVDF, df_ampermetr
#
#
# def button_do_grapf_clck():
#     """Построить графики"""
#     command = 'gf'
#     generator.write(("%s\n" % command).encode('utf-8'))
#     win.after(100)  # задержка 0,1 сек.
#     freq = float(
#         generator.readline().decode('utf-8').strip())  # Запрашивается частота генератора. Сравнивается с числом 20 Гц
#     # print('ЧАСТОТА: ', freq)
#
#     df_PVDF, df_ampermetr = get_mes_arrays(freq)
#     # print(df_PVDF)
#     # print(df_ampermetr)
#
#     #  ----------- Обработка данных ----------------
#     # 1. Сырые данные
#     # freq = 100 # freq частота, Гц, 1/c
#     t = (1000000 / freq) * 1.1  # отсечка, мкс
#
#     if cut_time.get() == 1:
#         df_PVDF_cutoff = df_PVDF[df_PVDF['time, mcsec'] <= t]  # обрезаем датафреймы
#         df_ampermetr_cutoff = df_ampermetr[df_ampermetr['time, mcsec'] <= t]
#     else:
#         df_PVDF_cutoff = df_PVDF
#         df_ampermetr_cutoff = df_ampermetr
#
#     save_data_fix_freq(df_PVDF_cutoff, df_ampermetr_cutoff)
#     # --------- рисование графика -------------
#     PVDF_col_name = list(df_PVDF.columns.values)[1]  # 'PVDF signal, mV' или 'PVDF signal, ADC'
#     ampermetr_col_name = list(df_ampermetr.columns.values)[1]  # 'current, mT' или 'current, mA'
#
#     figure.clf()  # затереть старые графики
#     ax = figure.add_subplot(111)  # новая область рисования графика
#     ax.set_title('Сырые данные, частота ' + str(freq) + ' Гц, отсечка ' + str(int(t)) + ' мкс')
#
#     ax1 = df_PVDF_cutoff.plot(ax=ax, x='time, mcsec', y=PVDF_col_name, marker='x', linestyle=':')  # , legend=None)
#     ax1.legend([PVDF_col_name], loc='lower left')
#     ax1.set_ylabel(PVDF_col_name)
#
#     ax2 = ax1.twinx()  # совмещение 2 графиков по оси x
#
#     ax2 = df_ampermetr_cutoff.plot(ax=ax2, x='time, mcsec', y=ampermetr_col_name, color='r', marker='x', linestyle=':')
#     ax2.legend([ampermetr_col_name], loc='upper right')
#     ax2.set_ylabel(ampermetr_col_name)
#
#     ax.grid(which='major', linewidth=1.2)  # сетка
#     ax.tick_params(which='major', length=10, width=2)
#
#     chart.draw()  # отрисовать
#
#
# button_do_graph = ttk.Button(master=frame3, text='Построить графики', command=button_do_grapf_clck)
# button_do_graph.pack(side='left', anchor='nw', padx=5, pady=2)
#
# # Вкладка 2:
# tab2 = ttk.Frame(master=tabs)
# tabs.add(tab2, text='Резонанс')
# # tabs.pack(side='top', anchor='nw',expand=1, fill='both', padx=10, pady=10)
#
#
# # ---------------- Раздел «Параметры резонанса» -----------------
# frame4 = tk.LabelFrame(master=tab2, text=' Параметры резонанса ', bd=2)
# frame4.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)
#
# label5 = ttk.Label(master=frame4, text='Частота стартовая:')
# label5.pack(side='left', anchor='nw', padx=5, pady=2)
#
# freq_start = tk.DoubleVar()  # переменная связанная со спиннером spinner4
# spinner4 = ttk.Spinbox(master=frame4, textvariable=freq_start, from_=1.00, to=100000.00, increment=1, width=6)
# spinner4.pack(side='left', anchor='nw', padx=5, pady=4)
# freq_start.set(2)
#
# label6 = ttk.Label(master=frame4, text='Частота финишная:')
# label6.pack(side='left', anchor='nw', padx=5, pady=2)
#
# freq_finish = tk.DoubleVar()  # переменная связанная со спиннером spinner5
# spinner5 = ttk.Spinbox(master=frame4, textvariable=freq_finish, from_=1.00, to=100000.00, increment=1, width=6)
# spinner5.pack(side='left', anchor='nw', padx=5, pady=4)
# freq_finish.set(50)
#
# label7 = ttk.Label(master=frame4, text='Число шагов')
# label7.pack(side='left', anchor='nw', padx=5, pady=2)
#
# freq_steps = tk.DoubleVar()  # переменная связанная со спиннером spinner6
# spinner6 = ttk.Spinbox(master=frame4, textvariable=freq_steps, from_=3.00, to=100000.00, increment=1, width=6)
# spinner6.pack(side='left', anchor='nw', padx=5, pady=4)
# freq_steps.set(3)
#
# # ---------------- Раздел «Управление экспериментом» -----------------
# frame5 = tk.LabelFrame(master=tab2, text=' Управление экспериментом ', bd=2)
# frame5.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)
#
# is_res_experiment_run = 0
#
# # Сюда будем сыпать сообщения о шаге и частоте
# message2 = tk.StringVar()
# messages2 = tk.Message(master=frame5, textvariable=message2, aspect=10000, anchor='nw', relief='ridge', borderwidth=2)
# messages2.pack(side='right', anchor='nw', fill='x', padx=5, pady=2)  # expand = 'x')
# message2.set("шаг 0 из 0. Частота 00 Гц")
#
#
# def draw_graph_res():
#     try:
#
#         if is_res_experiment_run == 1:
#             return
#         x_col_name = list(res_value_df.columns.values)[0]  # 'freq'
#         PVDF_col_name = list(res_value_df.columns.values)[1]  # 'PVDF signal, mV' или 'PVDF signal, ADC'
#         ampermetr_col_name = list(res_value_df.columns.values)[2]  # 'current, mT' или 'current, mA'
#
#         figure.clf()  # затереть старые графики
#         ax = figure.add_subplot(111)  # новая область рисования графика
#         ax.set_title("амплитуда сигнала и тока от частоты")
#
#         ax1 = res_value_df.plot(ax=ax, x=x_col_name, y=PVDF_col_name, marker='x', linestyle=':')  # , legend=None)
#         ax1.legend([PVDF_col_name], loc='lower left')
#         ax1.set_ylabel(PVDF_col_name)
#         ax2 = ax1.twinx()  # совмещение 2 графиков по оси x
#
#         ax2 = res_value_df.plot(ax=ax2, x=x_col_name, y=ampermetr_col_name, color='r', marker='x', linestyle=':')
#         ax2.legend([ampermetr_col_name], loc='upper right')
#         ax2.set_ylabel(ampermetr_col_name)
#
#         ax.grid(which='major', linewidth=1.2)  # сетка
#         ax.tick_params(which='major', length=10, width=2)
#
#         chart.draw()  # отрисовать
#
#     except Exception as e:
#         print(e)
#
#
# def amplitude_get(freq):
#     global series_df
#     steps = 3  # количество измерений на одну фиксированную частоту
#     PVDF_amplitude = 0.0
#     ampermetr_amplitude = 0.0
#     for i in range(steps):
#         df_PVDF, df_ampermetr = get_mes_arrays(freq)
#         PVDF_col_name = list(df_PVDF.columns.values)[1]  # 'PVDF signal, mV' или 'PVDF signal, ADC'
#         ampermetr_col_name = list(df_ampermetr.columns.values)[1]  # 'current, mT' или 'current, mA'
#
#         PVDF_amplitude += abs(df_PVDF[PVDF_col_name].max() - df_PVDF[PVDF_col_name].min())
#         ampermetr_amplitude += abs(df_ampermetr[ampermetr_col_name].max() - df_ampermetr[ampermetr_col_name].min())
#
#         if i == 1:
#             df_PVDF.rename(columns={PVDF_col_name: PVDF_col_name + ', {}Hz'.format(int(freq))}, inplace=True)
#             df_ampermetr.rename(columns={ampermetr_col_name: ampermetr_col_name + ', {}Hz'.format(int(freq))},
#                                 inplace=True)
#             series_df = pd.concat([series_df, df_PVDF, df_ampermetr], axis=1)
#             # print(series_df)
#     PVDF_amplitude = PVDF_amplitude / steps
#     ampermetr_amplitude = ampermetr_amplitude / steps
#
#     # print("PVDF_amplitude = {}. ampermetr_amplitude = {}".format(PVDF_amplitude, ampermetr_amplitude))
#     # print("PVDF from {} to {}. Ampermetr from {} to {}".format(PVDF_min, PVDF_max, ampermetr_min, ampermetr_max))
#     return PVDF_amplitude, ampermetr_amplitude
#
#
# def start_resonance():
#     try:
#         global is_res_experiment_run, res_value_df, series_df
#         series_df = pd.DataFrame([])
#         is_res_experiment_run = 1
#         steps = int(freq_steps.get())
#         f_step = abs((freq_finish.get() - freq_start.get()) / (steps - 1))
#
#         res_value_list = []
#         freq_real_step = 0
#
#         for i in range(steps):
#             f_now = int(freq_start.get() + f_step * i)
#             # print("f_now", f_now)
#             if is_res_experiment_run == 0:
#                 message2.set("эксперимент прерван на шаге {}/{} Частота {}Гц".format(i + 1, steps, f_now))
#                 break
#
#             # ставим очередную частоту
#             freq_real_step = float(gen_freq_set(f_now))
#
#             message2.set("эксперимент идет на шаге {}/{} Частота {}Гц".format(i + 1, steps, freq_real_step))
#
#             # запускаем эксперимент
#             PVDF_amplitude, ampermetr_amplitude = amplitude_get(freq_real_step)
#             res_value_list.append([freq_real_step, PVDF_amplitude, ampermetr_amplitude])
#
#             # print("{} PVDF_amplitude = {}. ampermetr_amplitude = {}".format(freq_real_step, PVDF_amplitude, ampermetr_amplitude))
#
#             # time.sleep(1)
#
#         # print(res_value_list)
#
#         if graph_param.get() == 1:
#             res_value_df = pd.DataFrame(res_value_list, columns=["freq", "PVDF signal, mV", "current, mT"])
#         else:
#             res_value_df = pd.DataFrame(res_value_list, columns=["freq", "PVDF signal, ADC", "current, mA"])
#
#         # print(res_value_df)
#         save_data_res(res_value_df, series_df)
#
#         # draw_graph_res(res_value_df)
#         if (is_res_experiment_run == 1):
#             is_res_experiment_run = 0
#             message2.set("эксперимент окончен. Можно нарисовать график")
#
#     except Exception as e:
#         print(e)
#
#
# def stop_resonance():
#     message2.set("ожидаем окончания текущего шага")
#     global is_res_experiment_run
#     is_res_experiment_run = 0
#
#
# button_start_resonance = ttk.Button(master=frame5, text='Начать эксперимент',
#                                     command=lambda: threading.Thread(target=start_resonance).start())
# button_start_resonance.pack(side='left', anchor='nw', padx=5, pady=2)
#
# button_stop_resonance = ttk.Button(master=frame5, text='Прервать эксперимент', command=stop_resonance)
# button_stop_resonance.pack(side='left', anchor='nw', padx=5, pady=2)
#
# button_draw_resonance = ttk.Button(master=frame5, text='Нарисовать график резонанса', command=draw_graph_res)
# button_draw_resonance.pack(side='left', anchor='nw', padx=5, pady=2)
#
# # Вкладка 3:
# tab3 = ttk.Frame(master=tabs)
# tabs.add(tab3, text='Управление сдвигом')
# tabs.pack(side='top', anchor='nw', expand=1, fill='both', padx=10, pady=10)
#
# # ---------------- Раздел «Управление сдвигом» -----------------
# frame6 = tk.LabelFrame(master=tab3, text='Управление сдвигом', bd=2)
# frame6.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)
#
# label7 = ttk.Label(master=frame6,
#                    text='Параметр по умолчанию равен 10. \nЧем он больше, тем больше смещение при увеличении частоты')
# label7.pack(side='left', anchor='nw', padx=5, pady=2)
#
# exp_param = tk.DoubleVar()  # переменная связанная со спиннером spinner7
# spinner7 = ttk.Spinbox(master=frame6, textvariable=exp_param, from_=1.00, to=100000.00, increment=1, width=6)
# spinner7.pack(side='left', anchor='nw', padx=5, pady=4)
# exp_param.set(10)
#
#
# def exp_param_set_ard():
#     # установить частоту
#     generator.flushInput()  # сброс входного буфера
#     generator.flushOutput()
#
#     command = 'sp' + str(int(exp_param.get())).strip()
#     generator.write(("%s\n" % command).encode('utf-8'))
#     # print("command", command)
#     win.after(100)  # задержка 0,1 сек.
#
#     # получаем отклик
#     response = generator.readline().decode(
#         'utf-8')  # В случае успешного выполнения команды плата вернет реально установленную частоту
#     win.after(100)  # задержка 0,1 сек.
#     ##generator.reset_input_buffer()  # сброс входного буфера
#     # print('response1',response)
#
#     exp_param_get_ard()
#
#
# def exp_param_get_ard():
#     # запросить параметр
#     generator.flushInput()  # сброс входного буфера
#     generator.flushOutput()
#
#     # запрос
#     command = 'gp'
#     generator.write(("%s\n" % command).encode('utf-8'))
#     win.after(100)  # задержка 0,1 сек.
#     ##generator.reset_output_buffer() # сброс выходного буфера
#
#     # получаем реальную частоту
#     temp_str = generator.readline().decode('utf-8').strip()
#     # print("temp_str ", temp_str)
#     exp_param = float(temp_str)
#     # freq = float(generator.readline().decode('utf-8').strip())
#     win.after(100)  # задержка 0,1 сек.
#     ##generator.reset_input_buffer()  # сброс входного буфера
#
#     exp_param_get.set(exp_param)
#
#
# button_set_exp_param = ttk.Button(master=frame6, text='Обновить параметр', command=exp_param_set_ard)
# button_set_exp_param.pack(side='left', anchor='nw', padx=5, pady=2)
#
# button_get_exp_param = ttk.Button(master=frame6, text='Запросить параметр', command=exp_param_get_ard)
# button_get_exp_param.pack(side='left', anchor='nw', padx=5, pady=2)
#
# exp_param_get = tk.DoubleVar()  # переменная связанная со спиннером spinner8
# spinner8 = ttk.Spinbox(master=frame6, textvariable=exp_param_get, from_=1.00, to=100000.00, increment=1, width=6)
# spinner8.pack(side='left', anchor='nw', padx=5, pady=4)
# exp_param_get.set(10)

# ---------------- Раздел «Разделительа» -----------------
frame7 = tk.LabelFrame(master=win, text=' Разделитель ', bd=2)
frame7.pack(side='top', anchor='nw', fill='both', padx=10, pady=2)
# ----------------------- graph -------------------------
figure = plt.Figure(figsize=(8, 5), dpi=100)  # контейнер графиков, задает глобальные параметры отображения графиков

ax = figure.add_subplot(111)  # пустая область рисования графика

ax.grid(which='major', linewidth=1.2)  # рисую сетку
ax.tick_params(which='major', length=10, width=2)

figure.set_tight_layout(True)  # автовписать в область рисования
plt.tight_layout()

chart = FigureCanvasTkAgg(figure, frame7)  # Область рисования графиков в окне tkinter
chart.get_tk_widget().pack(side='left', anchor='n')  # , fill='both' )


# ----------------------- graph 2-------------------------
figure_2 = plt.Figure(figsize=(11, 7), dpi=100)  # контейнер графиков, задает глобальные параметры отображения графиков

ax_f2 = figure_2.add_subplot(111)  # пустая область рисования графика

ax_f2.grid(which='major', linewidth=1.2)  # рисую сетку
ax_f2.tick_params(which='major', length=10, width=2)

figure_2.set_tight_layout(True)  # автовписать в область рисования
plt.tight_layout()

chart_2 = FigureCanvasTkAgg(figure_2, frame7)  # Область рисования графиков в окне tkinter
chart_2.get_tk_widget().pack(side='left', anchor='n')  # , fill='both' )
# -------------------------------------------------------


win.mainloop()  # запуск окна и цикла событий tkinter

arduino_device.close()

print('okeh')
