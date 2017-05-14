import time
import pigpio
import math


def normalize(dist):
    dis = ''
    if dist >= 50:
        dis += '7'
    elif dist >= 40:
        dis += '6'
    elif dist >= 30:
        dis += '5'
    elif dist >= 25:
        dis += '4'
    elif dist >= 20:
        dis += '3'
    elif dist >= 15:
        dis += '2'
    elif dist >= 10:
        dis += '1'
    else:
        dis += '0'
    return dis


class Env:
    left_servo_pin = 13
    right_servo_pin = 12
    sensor_signal_pin = 4
    sensor_message_size = 7
    next_signal_pin = 24
    dead_pin = 17
    time_record = int(time.time() * 1000)
    time_limit = 20
    sensor_unusable_diff = 6

    def __init__(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(self.sensor_signal_pin, pigpio.OUTPUT)
        self.pi.write(self.sensor_signal_pin, pigpio.LOW)
        self.h1 = self.pi.serial_open("/dev/ttyAMA0", 9600)

    def step(self, action):
        if action == 'left':
            self.set_speed(0, 100)
        elif action == 'go':
            self.set_speed(80, 80)
        else:
            self.set_speed(97, 0)

    def get_respond(self):  # FPGA sends data once when the signal_pin is high
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

        return d

    def get_reward(self):
        # 0 means die
        reward = 20
        dead = False
        if self.pi.read(self.dead_pin) == pigpio.LOW:
            reward = -1000
            dead = True
        return reward, dead

    def set_speed(self, lspeed=0, rspeed=0):
        self.pi.hardware_PWM(self.left_servo_pin, 800, int(lspeed) * 10000)
        self.pi.hardware_PWM(self.right_servo_pin, 800, int(rspeed) * 10000)

    def process_data(self, data):  # some algorithms to correct the sensors
        fixed = False
        # transform byte array to int
        distance = [int(each) / 2 for each in data]
        if (abs(distance[2] - distance[1]) < self.sensor_unusable_diff and distance[2] < 50) or (
                        abs(distance[4] - distance[5]) < self.sensor_unusable_diff and distance[4] < 50):
            if distance[2] < 50:
                a = distance[1]
                b = distance[2]
            else:
                a = distance[5]
                b = distance[4]
            c = math.sqrt((a + 8) ** 2 + (b + 8) ** 2 - 2 * (a + 8) * (b + 8) * math.cos(math.pi * 30 / 180))
            sita = math.acos(((b + 8) ** 2 + c ** 2 - (a + 8) ** 2) / (2 * (b + 8) * c))
            ans = ((b + 8) * math.sin(math.pi - sita) / math.sin(sita - math.pi * 30 / 180)) - 8
            distance[3] = round(ans, 1)
            fixed = True

        if fixed:
            state = normalize(min(((distance[1] + 8) / math.cos(math.pi * 30 / 180)) - 8, distance[0])) + \
                    normalize(distance[3]) + \
                    normalize(
                        min(distance[6], ((distance[5] + 8) / math.cos(math.pi * 30 / 180)) - 8))
        else:
            state = normalize(min(((distance[1] + 8) / math.cos(math.pi * 30 / 180)) - 8, distance[0])) + \
                    normalize(min(((distance[2] + 8) / math.cos(math.pi * 30 / 180)) - 8, distance[3],
                                  ((distance[4] + 8) / math.cos(math.pi * 30 / 180)) - 8)) + \
                    normalize(
                        min(distance[6], ((distance[5] + 8) / math.cos(math.pi * 30 / 180)) - 8))

        return state

    def wait(self):
        try:
            while not self.pi.read(self.next_signal_pin):
                time.sleep(0.001)
        except:
            self.end()
            print("STOP")

    def test(self, receive_data):
        distance = [int(each) / 2 for each in receive_data]
        print(distance)
        fixed = False
        # transform byte array to int
        if (abs(distance[2] - distance[1]) < self.sensor_unusable_diff and distance[2] < 50) or (
                        abs(distance[4] - distance[5]) < self.sensor_unusable_diff and distance[4] < 50):
            if distance[2] < 50:
                a = distance[1]
                b = distance[2]
            else:
                a = distance[5]
                b = distance[4]
            c = math.sqrt((a + 8) ** 2 + (b + 8) ** 2 - 2 * (a + 8) * (b + 8) * math.cos(math.pi * 30 / 180))
            sita = math.acos(((b + 8) ** 2 + c ** 2 - (a + 8) ** 2) / (2 * (b + 8) * c))
            ans = ((b + 8) * math.sin(math.pi - sita) / math.sin(sita - math.pi * 30 / 180)) - 8
            distance[3] = round(ans, 1)
            fixed = True

        if fixed:
            state = normalize(min(((distance[1] + 8) / math.cos(math.pi * 30 / 180)) - 8, distance[0])) + \
                    normalize(distance[3]) + \
                    normalize(
                        min(distance[6], ((distance[5] + 8) / math.cos(math.pi * 30 / 180)) - 8))
        else:
            state = normalize(min(((distance[1] + 8) / math.cos(math.pi * 30 / 180)) - 8, distance[0])) + \
                    normalize(min(((distance[2] + 8) / math.cos(math.pi * 30 / 180)) - 8, distance[3],
                                  ((distance[4] + 8) / math.cos(math.pi * 30 / 180)) - 8)) + \
                    normalize(
                        min(distance[6], ((distance[5] + 8) / math.cos(math.pi * 30 / 180)) - 8))

        if self.pi.read(self.dead_pin) == pigpio.LOW:
            print('DEAD   ' + 'state:' + state)
        else:
            print('Alive  ' + 'state:' + state)

    def end(self):
        self.set_speed(0, 0)
        self.pi.serial_close(self.h1)
