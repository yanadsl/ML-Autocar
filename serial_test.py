import datetime
import sys
import pigpio
import time
import math


def normalize_side(dist):
    dis = str(math.floor(float(dist) / 2.5))
    return dis


def normalize(dist):
    dis = str(math.floor(float(dist)/4.5))
    return dis


time_record = int(time.time() * 1000)
time_limit = 50
pi = pigpio.pi()
sensor_message_size = 7
sensor_signal_pin = 4
dead_pin = 17
sensor_unusable_diff = 6
pi.set_mode(sensor_signal_pin, pigpio.OUTPUT)
h1 = pi.serial_open("/dev/ttyAMA0", 9600)
pi.serial_write_byte(h1, 10 * 2)
pi.write(sensor_signal_pin, pigpio.LOW)
print("start")
sita = 1
distance = []
while True:
    try:
        pi.write(sensor_signal_pin, pigpio.HIGH)
        while pi.serial_data_available(h1) < sensor_message_size - 1:
            time.sleep(0.0007)
        (b, d) = pi.serial_read(h1, sensor_message_size)
        pi.write(sensor_signal_pin, pigpio.LOW)

        print(d)
    except:
        pi.serial_close(h1)
        sys.exit(0)
