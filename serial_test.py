import datetime
import sys
import pigpio
import time

def normalize(things):
    dis = ''
    for distance in things:
        if distance >= 36:
            dis += '8'
        elif distance >= 24:
            dis += '7'
        elif distance >= 20:
            dis += '6'
        elif distance >= 16:
            dis += '5'
        elif distance >= 12:
            dis += '4'
        elif distance >= 10:
            dis += '3'
        elif distance >= 8:
            dis += '2'
        elif distance >= 6:
            dis += '1'
        else:
            dis += '0'
    return dis

time_record = int(time.time() * 1000)
time_limit = 50
pi = pigpio.pi()
sensor_message_size = 2
sensor_signal_pin = 4
pi.set_mode(sensor_signal_pin, pigpio.OUTPUT)
h1 = pi.serial_open("/dev/ttyAMA0", 9600)
pi.write(sensor_signal_pin, 0)
print("start")
try:
    while True:
        while (int(time.time() * 1000) - time_record) <= time_limit:
            time.sleep(0.002)
        time_record = int(time.time() * 1000)
        distance = []
        pi.serial_read(h1)  # clear any redauntancy data
        pi.write(sensor_signal_pin, 1)
        print("high")
        while pi.serial_data_available(h1) < sensor_message_size:
            #print( pi.serial_data_available(h1))
            time.sleep(0.0007)
        (b, d) = pi.serial_read(h1,sensor_message_size)
        pi.write(sensor_signal_pin, pigpio.LOW)
        print("LOW")

        for a in d:
            distance.append(int(a) / 2.0)
        #distance = normalize(distance)
        print('distance:' + str(distance))
except KeyboardInterrupt:
    pi.serial_close(h1)
    sys.exit(0)
