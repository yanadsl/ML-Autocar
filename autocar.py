import time
from RpiEnv import Env
import numpy as np
from qLearning import QL


def playGame(train_indicator=1):  # 1 means Train, 0 means simply Run
    actions = ['left', 'go', 'right']
    learning_rate = 0.4
    greedy = 0.05
    decay = 0.7

    average_step_length = 5
    np.random.seed(1337)

    episode_count = 120000
    max_steps = 1000

    step_average = 0
    step_queue = []
    # initialize pigpiod and set at which distance is dead
    env = Env()

    Qlearning = QL(actions, decay, greedy, learning_rate)

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

    print("Autocar Experiment Start.")
    env.wait()
    time.sleep(0.7)
    try:
        for i in range(episode_num, episode_count):
            file = open('episode.txt', 'w')
            file.write(str(i))
            file.close()

            print("step_average: " + str(step_average))
            # change parameters by step_average = least (average_step_length) times step average
            if step_average < 50:
                Qlearning.parameter_set(0.5, 0.05, 0.7)
            elif step_average < 100:
                Qlearning.parameter_set(0.5, 0.03, 0.7)
            elif step_average < 150:
                Qlearning.parameter_set(0.48, 0.02, 0.7)
            elif step_average < 200:
                Qlearning.parameter_set(0.46, 0.01, 0.7)
            elif step_average < 400:
                Qlearning.parameter_set(0.44, 0.005, 0.7)
            else:
                Qlearning.parameter_set(0.4, 0.001, 0.7)

            state = env.get_respond()
            step = 0
            total_reward = 0
            for j in range(max_steps):
                time_record = int(time.time() * 1000)

                action = Qlearning.action_choose(state, train_indicator)
                env.step(action)
                time.sleep(0.07)
                new_state = env.get_respond()
                reward, dead = env.get_reward()
                if train_indicator:
                    Qlearning.learn(state, action, reward, new_state)

                total_reward += reward

                # print("Ep", i, "Step", step, "State", state, "Act", action,
                #       "resp_t:", (int(time.time() * 1000) - time_record))
                print("Ep: "+str(i)+"Step: "+str(step)+"State: "+str(state)+"Act: "+str(action))

                if dead:
                    break

                state = new_state
                step += 1
            env.set_speed(0, 0)
            step_queue.append(step)
            if len(step_queue) > average_step_length:
                step_queue.pop(0)
            step_average = sum(step_queue)/average_step_length
            if np.mod(i, 10) == 0:    # save every 10 times
                Qlearning.save("Qtable" + str(i) + ".h5")

            if train_indicator:
                print("Now we save model")
                Qlearning.save("Qtable.h5")
                if step > best_step:
                    file = open('best_step.txt', 'w')
                    file.write(str(step))
                    file.close()
                score = open('score.txt', 'a')
                score.write("Episode: " + str(i) + "\tStep: " + str(step) + "\n")
                score.close()

            print("")
            env.wait()
            time.sleep(0.7)
        env.end()  # Stop Servos
        print("Finish.")

    except KeyboardInterrupt:
        env.end()
        ask = raw_input("save model?(y/n):")
        if ask == 'y':
            print("Now we save model")
            Qlearning.save("Qtable.h5")


if __name__ == "__main__":
    playGame()
