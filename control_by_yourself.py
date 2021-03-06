import time
from RpiEnv import Env
import numpy as np
from qLearning import QL
from qlearning_lambda import qlearning_lambda
import sys, select, tty, termios
from threading import Thread
key = 0
stop = False

def read_input(threadname):

    global key
    global stop
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        i = 0
        while not stop:
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                key = sys.stdin.read(1)
                print(key)
                if key == '\x1b':         # x1b is ESC
                    break

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)



def playGame(train_indicator=1):  # 1 means Train, 0 means simply Run
    global key
    global stop
    actions = ['left', 'go', 'right']
    learning_rate = 0.4
    greedy = 0.05
    decay = 0.7
    Lambda = 0.5
    average_step_length = 5
    np.random.seed(1337)

    episode_count = 120000
    max_steps = 1000

    step_queue = []
    # initialize pigpiod and set at which distance is dead
    env = Env()

    #Qlearning = QL(actions, decay, greedy, learning_rate)
    Qlearning = qlearning_lambda(actions, decay, greedy, learning_rate, Lambda)

    # load weight
    Qlearning.load("Qtable.h5")

    # load episode of last time
    try:
        file = open('episode.txt', 'r')
        episode_num = int(file.read())
        file.close()
        print("Episode number: " + str(episode_num))
    except:
        episode_num = 1
        print("Episode number: Error")
    # load best step of last time
    try:
        file = open('best_step.txt', 'r')
        best_step = int(file.read())
        file.close()
        print("best_step: " + str(best_step))
    except:
        best_step = 0
        print("best_step: Error")
    # load step average of last time
    try:
        file = open('step_average.txt', 'r')
        step_average = int(file.read())
        file.close()
        print("step_average:" + str(step_average))
    except:
        step_average = 0
        print("step_average: Error")

    print("Autocar Experiment Start.")

    thread1 = Thread(target=read_input, args=("Thread-1",))
    thread1.start()

    try:
        for i in range(episode_num, episode_count):
            file = open('episode.txt', 'w')
            file.write(str(i))
            file.close()

            receive_data = env.get_respond()
            state = env.process_data(receive_data)
            step = 0
            total_reward = 0
            time.sleep(1.5)  # prevent from restart instantly
            print('Press button to start')
            while key == 0:
                pass
            for j in range(max_steps):
                time_record = int(time.time() * 1000)

                if str(key) == 'a':
                    action = 'left'
                elif str(key) == 'w':
                    action = 'go'
                elif str(key) == 'd':
                    action = 'right'
                elif str(key) == 's' or str(key) == 'r':
                    break

                env.step(action)
                # you should give a small latency to make sure your action do work without being skipped
                time.sleep(0.2)
                receive_data = env.get_respond()
                new_state = env.process_data(receive_data)
                reward, dead = env.get_reward()
                if train_indicator:
                    Qlearning.learn(state, action, reward, new_state)

                total_reward += reward

                # if you are concern about how fast does Rpi run , use line 101
                # print("Ep", i, "Step", step, "State", state, "Act", action,
                #       "resp_t:", (int(time.time() * 1000) - time_record))
                print("Ep: "+str(i)+"Step: "+str(step)+"State: "+str(state)+"Act: "+str(action))

                if dead:
                    break

                state = new_state
                step += 1
            env.set_speed(0, 0)
            if str(key) == 's':
                break
            #Qlearning.backtrace_reset()
            key = 0

            step_queue.append(step)
            if len(step_queue) > average_step_length:
                step_queue.pop(0)
            step_average = sum(step_queue)/average_step_length

            if np.mod(i, 10) == 0:    # save every 10 times
                Qlearning.save("Qtable" + str(i) + ".h5")

            if train_indicator:
                print("Now we save model")
                Qlearning.save("Qtable.h5")
                # save some record
                if step > best_step:
                    file = open('best_step.txt', 'w')
                    file.write(str(step))
                    file.close()
                score = open('score.txt', 'a')
                score.write("Episode: " + str(i) + "\tStep: " + str(step) + "\n")
                score.close()
                file = open('step_average.txt', 'w')
                file.write(str(step_average))
                file.close()

            print("")

        env.end()  # Stop Servos
        stop = True
        print("Finish.")

    except KeyboardInterrupt:
        stop = True
        env.end()
        ask = raw_input("save model?(y/n):")
        if ask == 'y':
            print("Now we save model")
            Qlearning.save("Qtable.h5")


if __name__ == "__main__":
    playGame()
