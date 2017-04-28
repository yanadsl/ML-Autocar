import time
import pigpio


class Env:
    left_servo_pin = 13
    right_servo_pin = 12
    sensor_signal_pin = 4
    sensor_message_size = 3
    dead_pin = 17
    time_record = int(time.time() * 1000)
    time_limit = 20

    def __init__(self, ):
        self.pi = pigpio.pi()
        self.pi.set_mode(self.sensor_signal_pin, pigpio.OUTPUT)
        self.h1 = self.pi.serial_open("/dev/ttyAMA0", 9600)
        self.initial_run = True

    def step(self, action):
        if action == 'left':
            self.set_speed(20, 100)
        elif action == 'go':
            self.set_speed(100, 100)
        else:
            self.set_speed(100, 20)

    def get_respond(self):
        # delay at least 50ms to get right value of sonic sensor
        while (int(time.time() * 1000) - self.time_record) <= self.time_limit:
            time.sleep(0.002)
        self.time_record = int(time.time() * 1000)
        distance = []
        self.pi.serial_read(self.h1)  # clear any redauntancy data
        self.pi.write(self.sensor_signal_pin, pigpio.HIGH)
        while self.pi.serial_data_available(self.h1) < self.sensor_message_size-1:
            time.sleep(0.0007)
        (b, d) = self.pi.serial_read(self.h1, self.sensor_message_size)
        self.pi.write(self.sensor_signal_pin, pigpio.LOW)
        for a in d:
            distance.append(int(a) / 2.0)

        distance = self.normalize(distance)

        return distance

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

    def end(self):
        self.set_speed(0, 0)
        self.pi.serial_close(self.h1)
