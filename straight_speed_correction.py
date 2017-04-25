import sys
import pigpio
import time


def set_speed(lspeed=0, rspeed=0):
    pi.hardware_PWM(left_servo_pin, 800, int(lspeed)*10000)
    pi.hardware_PWM(right_servo_pin, 800, int(rspeed)*10000)


pi = pigpio.pi()

left_servo_pin = 13
right_servo_pin = 12
ls = 80
rs = 80
h1 = pi.serial_open("/dev/ttyAMA0", 9600)

print("start")
try:
    while True:
        pi.serial_read(h1)  # clear any redauntancy data

        while not pi.serial_data_available(h1):
            time.sleep(0.1)
        (b, d) = pi.serial_read(h1, 1)
        for a in d:
            distance = int(a)
        is_left_slower = distance & 128
        gap = distance & 127
        if gap >= 10:
            if is_left_slower:
                ls -= 1
            else:
                rs -= 1
            set_speed(ls, rs)
            time.sleep(0.5)
        else:
            set_speed(0, 0)
            print("ls:", ls, "rs:", rs)
            pi.serial_close(h1)
            sys.exit(0)

except KeyboardInterrupt:
    set_speed(0, 0)
    pi.serial_close(h1)
    sys.exit(0)
