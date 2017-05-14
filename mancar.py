state_number = 1
distance_difference = 10
delay = 0.021
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
        state = '0'
        action = '0'
        change = False
        for i in range(state_number):
            if c - d > distance_difference * (i+1):
                change = True
                action = 'left'
                state = str(i * 2 + 1)
            elif d - c > distance_difference * (i+1):
                change = True
                action = 'right'
                state = str(i * 2 + 2)  # avoid i=0 you cant reach 2
        if not change:
            action = 'go'
            state = '0'
        env.step(action)
        print(state + ', ' + action)
        time.sleep(delay)
except:
    env.end()
