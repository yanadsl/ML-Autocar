delay = 0.21
import time,math
from RpiEnv import Env

err = 1
env = Env()

try:
    while True:
        data = env.get_respond()
        distance = [int(each) / 2 for each in data]

        c = min(distance[0:3])
        d = min(distance[4:7])
        state = env.process_data(data)
        if c - d > 10:
            env.step('left')
        elif d-c > 10:
            env.step('right')
        else:
            env.step('go')
        time.sleep(0.021)
except:
    env.end()
