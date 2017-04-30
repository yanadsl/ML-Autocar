import time
import pigpio
import math


class Env:
    left_servo_pin = 13
    right_servo_pin = 12
    sensor_signal_pin = 4
    sensor_message_size = 7
    dead_pin = 17
    time_record = int(time.time() * 1000)
    time_limit = 20

    def __init__(self, die_distance):
        self.pi = pigpio.pi()
        self.pi.set_mode(self.sensor_signal_pin, pigpio.OUTPUT)
        self.pi.write(self.sensor_signal_pin, pigpio.LOW)
        self.h1 = self.pi.serial_open("/dev/ttyAMA0", 9600)
        self.pi.serial_write_byte(self.h1, die_distance*2)

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

    def normalize(self, things):
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

    def set_speed(self, lspeed=0, rspeed=0):
        self.pi.hardware_PWM(self.left_servo_pin, 800, int(lspeed) * 10000)
        self.pi.hardware_PWM(self.right_servo_pin, 800, int(rspeed) * 10000)

    def process_data(self, data):
        sets = []
        # transform byte array to int
        for a in data:
            sets.append(int(a) / 2.0)
        a = sets[1]
        b = sets[2]
        c = math.sqrt(a**2+b**2-a*b*math.cos(math.pi / 6))
        sita = math.acos((b**2+c**2-a**2/2*b*c))
        ans = a - math.sin(math.pi-sita)/math.sin(sita-math.pi/6)

        if not (abs(sets[2] - sets[1]) > 7 and abs(sets[4] - sets[5]) > 7):
            sets[3] = ans

        return self.normalize(
                [round(min(sets[0] * math.cos(math.pi * 25 / 180), sets[1]), 1),
                 round(min((sets[2]+1) * math.cos(math.pi * 37 / 180), sets[3], (sets[4]+1) * math.cos(math.pi * 37 / 180)), 1),
                 round(min(sets[5], (sets[6]+1) * math.cos(math.pi * 25 / 180)), 1)]
        )

    def end(self):
        self.set_speed(0, 0)
        self.pi.serial_close(self.h1)
