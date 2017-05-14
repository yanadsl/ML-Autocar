import time
from RpiEnv import Env

err = 1
env = Env()


try:
    while True:
        a = env.get_respond()
        state = env.process_data(a)
        if int(state[0]) - int(state[2] > err):
            env.step('left')
        elif int(state[2]) - int(state[0] > err):
            env.step('right')
        else:
            env.step('go')
        time.sleep(0.2)
except:
    env.end()
