import datetime
import sys
import pigpio
import time
import math


def normalize(dist):
    dis = ''
    if dist >= 81:
        dis += '8'
    elif dist >= 54:
        dis += '7'
    elif dist >= 45:
        dis += '6'
    elif dist >= 35:
        dis += '5'
    elif dist >= 27:
        dis += '4'
    elif dist >= 22.5:
        dis += '3'
    elif dist >= 18:
        dis += '2'
    elif dist >= 13.5:
        dis += '1'
    else:
        dis += '0'
    return dis


def normalize_side(dist):
    dis = ''
    if dist >= 45:
        dis += '8'
    elif dist >= 30:
        dis += '7'
    elif dist >= 25:
        dis += '6'
    elif dist >= 20:
        dis += '5'
    elif dist >= 15:
        dis += '4'
    elif dist >= 12.5:
        dis += '3'
    elif dist >= 10:
        dis += '2'
    elif dist >= 7.5:
        dis += '1'
    else:
        dis += '0'
    return dis


time_record = int(time.time() * 1000)
time_limit = 50
pi = pigpio.pi()
sensor_message_size = 7
sensor_signal_pin = 4
dead_pin = 17
sensor_unusable_diff = 4
pi.set_mode(sensor_signal_pin, pigpio.OUTPUT)
h1 = pi.serial_open("/dev/ttyAMA0", 9600)
pi.serial_write_byte(h1, 10 * 2)
pi.write(sensor_signal_pin, pigpio.LOW)
print("start")
sita = 1
distance = []
try:
    while True:
        while (int(time.time() * 1000) - time_record) <= time_limit:
            time.sleep(0.002)
        time_record = int(time.time() * 1000)
        pi.serial_read(h1)  # clear any redauntancy data
        pi.write(sensor_signal_pin, pigpio.HIGH)
        while pi.serial_data_available(h1) < sensor_message_size - 1:
            # print( pi.serial_data_available(h1))
            time.sleep(0.0007)
        (b, d) = pi.serial_read(h1, sensor_message_size)
        pi.write(sensor_signal_pin, pigpio.LOW)
        distance = []
        for a in d:
            distance.append(int(a) / 2.0)
        if pi.read(dead_pin) == pigpio.LOW:
            print("dead")

        if (abs(distance[2] - distance[1]) < sensor_unusable_diff and distance[2] < 40) or (
                        abs(distance[4] - distance[5]) < sensor_unusable_diff and distance[4] < 40):
            print("修正啦FIXED")
            if distance[2] < 40:
                a = distance[1] + 0.5
                b = distance[2]
            else:
                a = distance[5] + 0.5
                b = distance[4]
            c = math.sqrt(a ** 2 + b ** 2 - 2 * a * b * math.cos(math.pi * 25 / 180))
            sita = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
            ans = a * math.sin(math.pi - sita) / math.sin(sita - math.pi * 25 / 180)
            distance[3] = round(ans, 1)
        if distance[3] > 60:
            state = [normalize_side(round(min(distance[0] * math.cos(math.pi * 25 / 180), distance[1]), 1)),
                     normalize(round(min((distance[2] + 1) * math.cos(math.pi * 37 / 180), distance[3],
                                         (distance[4] + 1) * math.cos(math.pi * 37 / 180)), 1)),
                     normalize_side(round(min(distance[5], (distance[6] + 1) * math.cos(math.pi * 25 / 180)), 1))]
        else:
            state = [normalize_side(round(min(distance[1]), 1)),
                     normalize(round(min((distance[2] + 1) * math.cos(math.pi * 37 / 180), distance[3],
                                         (distance[4] + 1) * math.cos(math.pi * 37 / 180)), 1)),
                     normalize_side(round(min(distance[5]), 1))]

        print([distance[0], distance[1], distance[2], distance[3], distance[4], distance[5], distance[6]],
              '      ', round(math.degrees(sita), 1), '      ', state)

except KeyboardInterrupt:
    pi.serial_close(h1)
    sys.exit(0)
