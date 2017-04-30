import sys
import pigpio
import time
from colorama import Fore, Back, Style

def set_speed(lspeed, rspeed):
    pi.hardware_PWM(left_servo_pin, 800, int(lspeed)*10000)
    pi.hardware_PWM(right_servo_pin, 800, int(rspeed)*10000)


pi = pigpio.pi()

left_servo_pin = 13
right_servo_pin = 12
dead_pin = 17
rs = 100
ts = 100
print("start")
try:
    while True:
        set_speed(rs, ts)
        if pi.read(dead_pin) == pigpio.LOW:
            set_speed(0, 0)

except KeyboardInterrupt:
    set_speed(0, 0)
    sys.exit(0)
