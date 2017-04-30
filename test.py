import sys
import pigpio
import time
from colorama import Fore, Back, Style

def set_speed(lspeed, rspeed):
    pi.hardware_PWM(left_servo_pin, 800, int(lspeed)*10000)
    pi.hardware_PWM(right_servo_pin, 800, int(rspeed)*10000)


pi = pigpio.pi()
h1 = pi.serial_open("/dev/ttyAMA0", 9600)
left_servo_pin = 13
right_servo_pin = 12
dead_pin = 17
die_distance = 8
rs = 100
ts = 100
print("start")
pi.serial_write_byte(h1, die_distance * 2)

try:
    while True:
        set_speed(rs, ts)
        if pi.read(dead_pin) == pigpio.LOW:
            set_speed(0, 0)
            pi.serial_close(h1)

except :
    set_speed(0, 0)
    pi.serial_close(h1)
    sys.exit(0)
