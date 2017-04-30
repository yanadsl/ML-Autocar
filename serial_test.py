import datetime
import sys
import pigpio
import time
import math

time_record = int(time.time() * 1000)
time_limit = 50
pi = pigpio.pi()
sensor_message_size = 7
sensor_signal_pin = 4
dead_pin = 17
pi.set_mode(sensor_signal_pin, pigpio.OUTPUT)
h1 = pi.serial_open("/dev/ttyAMA0", 9600)
pi.serial_write_byte(h1, 10 * 2)
pi.write(sensor_signal_pin, pigpio.LOW)
print("start")
sita = 1
try:
    while True:
        while (int(time.time() * 1000) - time_record) <= time_limit:
            time.sleep(0.002)
        time_record = int(time.time() * 1000)
        distance = []
        pi.serial_read(h1)  # clear any redauntancy data
        pi.write(sensor_signal_pin, pigpio.HIGH)
        while pi.serial_data_available(h1) < sensor_message_size - 1:
            # print( pi.serial_data_available(h1))
            time.sleep(0.0007)
        (b, d) = pi.serial_read(h1, sensor_message_size)
        pi.write(sensor_signal_pin, pigpio.LOW)
        sets = []
        for a in d:
            sets.append(int(a) / 2.0)
        if pi.read(dead_pin) == pigpio.LOW:
            print("dead")

        if not (abs(sets[2] - sets[1]) > 7 and abs(sets[4] - sets[5]) > 7):
            print("SMALLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLER")
            if sets[2] < 40:
                a = sets[1]+0.5
                b = sets[2]
            else:
                a = sets[5]+0.5
                b = sets[4]
            c = math.sqrt(a ** 2 + b ** 2 - 2 * a * b * math.cos(math.pi * 25 / 180))
            sita = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
            ans = a * math.sin(math.pi - sita) / math.sin(sita - math.pi * 25 / 180)
            sets[3] = round(ans, 1)

        print([sets[0], sets[1], sets[2], sets[3], sets[4], sets[5], sets[6]], round(math.degrees(sita), 1))
        # distance = normalize(distance)
except KeyboardInterrupt:
    pi.serial_close(h1)
    sys.exit(0)
