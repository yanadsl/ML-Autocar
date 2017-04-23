import time
from RpiEnv import Env
import numpy as np
from qLearning import QL


def playGame(train_indicator=1):  # 1 means Train, 0 means simply Run
    actions = ['left', 'go', 'right']
    learning_rate = 0.4
    greedy = 0.1
    decay = 0.9

    np.random.seed(1337)

    episode_count = 2000
    max_steps = 1000

    # Generate a Torcs environment
    env = Env()

    Qlearning = QL(actions, decay, greedy, learning_rate)

    # Now load the weight
    Qlearning.load("Qtable.h5")

    print("Autocar Experiment Start.")
    try:
        for i in range(episode_count):

            state = env.get_respond()
            step = 0
            total_reward = 0
            for j in range(max_steps):
                time_record = int(time.time() * 1000)
                action = Qlearning.action_choose(state)
                env.step(action)
                time.sleep(0.5)

                new_state = env.get_respond()
                reward, dead = env.get_reward()
                if train_indicator:
                    Qlearning.learn(state, action, reward, new_state)

                total_reward += reward

                print("Episode", i, "Step", step, "State", state, "Action", action, "Reward", reward)
                if dead:
                    env.stop_servo()
                    break

                state = new_state
                step += 1
                print("respond time", (int(time.time() * 1000) - time_record))

            if train_indicator:
                print("Now we save model")
                Qlearning.save("Qtable.h5")

            print("")
            input("Ready for next? Press return")
        env.end()  # Stop Servos
        print("Finish.")
    except KeyboardInterrupt:
        ask = input("save model?(y/n):")
        if ask == 'y':
            print("Now we save model")
            Qlearning.save("Qtable.h5")
        env.end()


if __name__ == "__main__":
    playGame()
