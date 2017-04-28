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

    episode_count = 200
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

                new_state = env.get_respond()
                reward, dead = env.get_reward()
                if train_indicator:
                    Qlearning.learn(state, action, reward, new_state)

                total_reward += reward

                print( "Ep", i, "Step", step, "State", state, "Action", action,
                      "resp_t:", (int(time.time() * 1000) - time_record))

                if dead:
                    env.set_speed(0, 0)
                    break

                state = new_state
                step += 1

            if train_indicator:
                print("Now we save model")
                Qlearning.save("Qtable.h5")

            print("")
            input("Ready for next? Press return")
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
