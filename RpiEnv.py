import time
import pigpio
import math


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


class Env:
    left_servo_pin = 13
    right_servo_pin = 12
    sensor_signal_pin = 4
    sensor_message_size = 7
    dead_pin = 17
    time_record = int(time.time() * 1000)
    time_limit = 20
    sensor_unusable_diff = 6

    def __init__(self, die_distance):
        self.pi = pigpio.pi()
        self.pi.set_mode(self.sensor_signal_pin, pigpio.OUTPUT)
        self.pi.write(self.sensor_signal_pin, pigpio.LOW)
        self.h1 = self.pi.serial_open("/dev/ttyAMA0", 9600)
        self.pi.serial_write_byte(self.h1, die_distance * 2)

    def step(self, action):
        if action == 'left':
            self.set_speed(20, 100)
        elif action == 'go':
            self.set_speed(97, 100)
        else:
            self.set_speed(100, 20)

    def get_respond(self):
        # delay at least 50ms to get right value of sonic sensor
        while (int(time.time() * 1000) - self.time_record) <= self.time_limit:
            time.sleep(0.002)
        self.time_record = int(time.time() * 1000)

        self.pi.serial_read(self.h1)  # clear any redauntancy data
        self.pi.write(self.sensor_signal_pin, pigpio.HIGH)
        while self.pi.serial_data_available(self.h1) < self.sensor_message_size - 1:
            time.sleep(0.0007)
        (b, d) = self.pi.serial_read(self.h1, self.sensor_message_size)
        self.pi.write(self.sensor_signal_pin, pigpio.LOW)

        return self.process_data(d)

    def get_reward(self):
        # 0 means die
        if self.pi.read(self.dead_pin) == pigpio.LOW:
            reward = -1000
            dead = True
        else:
            reward = 10
            dead = False
        return reward, dead

    def set_speed(self, lspeed=0, rspeed=0):
        self.pi.hardware_PWM(self.left_servo_pin, 800, int(lspeed) * 10000)
        self.pi.hardware_PWM(self.right_servo_pin, 800, int(rspeed) * 10000)

    def process_data(self, data):
        distance = []
        fixed = False
        # transform byte array to int
        for a in data:
            distance.append(int(a) / 2.0)
        if (abs(distance[2] - distance[1]) < self.sensor_unusable_diff and distance[2] < 40) or (
                        abs(distance[4] - distance[5]) < self.sensor_unusable_diff and distance[4] < 40):
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
            fixed = True
        if distance[3] > 60:
            if fixed:
                state = normalize_side(round(min(distance[0] * math.cos(math.pi * 25 / 180), distance[1]), 1)) + \
                        distance[3] + \
                        normalize_side(
                            round(min(distance[5], (distance[6] + 1) * math.cos(math.pi * 25 / 180)), 1))
            else:
                state = normalize_side(round(min(distance[0] * math.cos(math.pi * 25 / 180), distance[1]), 1)) + \
                        normalize(round(min((distance[2] + 1) * math.cos(math.pi * 37 / 180), distance[3],
                                            (distance[4] + 1) * math.cos(math.pi * 37 / 180)), 1)) + \
                        normalize_side(
                            round(min(distance[5], (distance[6] + 1) * math.cos(math.pi * 25 / 180)), 1))
        else:
            if fixed:
                state = normalize_side(round(distance[1], 1)) + \
                        distance[3] + \
                        normalize_side(round(distance[5], 1))
            else:
                state = normalize_side(round(distance[1], 1)) + \
                        normalize(round(min((distance[2] + 1) * math.cos(math.pi * 37 / 180), distance[3],
                                            (distance[4] + 1) * math.cos(math.pi * 37 / 180)), 1)) + \
                        normalize_side(round(distance[5], 1))
        return state

    def end(self):
        self.set_speed(0, 0)
        self.pi.serial_close(self.h1)
