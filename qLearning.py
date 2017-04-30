import numpy as np
import pandas as pd


class QL:
    def __init__(self, actions, learning_rate, greedy, decay):
        self.actions = actions
        self.lr = learning_rate
        self.learning_rate = learning_rate
        self.g = greedy
        self.greedy = greedy
        self.decay = decay
        self.table = pd.DataFrame(columns=self.actions)

    def load(self, fname):
        try:
            self.table = pd.read_hdf(fname, 'table')
            print("load successfully")
        except:
            print("no file to load")

    def save(self, fname):
        self.table.to_hdf(fname, 'table')

    def action_choose(self, ob, train_indicator):
        self.ob_exist(ob)
        if train_indicator:
            if np.random.uniform() > self.greedy:
                act = self.table.ix[ob, :]
                print('[' + act.to_string().replace('\n', '][') + ']')
                act = act.reindex(np.random.permutation(act.index))
                act = act.argmax()
        else:
            act = np.random.choice(self.act)
            print("")
            print("random")
        return act

    def learn(self, state, a, reward, next_state, done=False):
        self.ob_exist(next_state)
        q_guess = self.table.ix[state, a]
        if done:
            q = reward
        else:
            # q = reward + self.decay * self.table.ix[next_state, :].max()     # Q-learning
            q = reward + self.decay * self.table.ix[next_state, a]  # SARSA
        self.table.ix[state, a] += self.learning_rate * (q - q_guess)

    def ob_exist(self, state):
        if state not in self.table.index:
            self.table = self.table.append(
                pd.Series(
                    [0] * len(self.a),
                    index=self.table.columns,
                    name=state,
                )
            )

    def parameter_change(self, step):  # write equation to change parameters here
        if step >= 200:
            if step < 450:
                self.learning_rate += (0.5 - self.lr) / (450 - 200)
                self.greedy -= self.g / (450 - 200)
            else:
                self.learning_rate = 0.5
                self.greedy = 0

    def parameter_reset(self):  # reset parameter to original(value when qLearning initialize)
        self.learning_rate = self.lr
        self.greedy = self.g

    def parameter_set(self, learning_rate, greedy, decay):
        self.learning_rate = learning_rate
        self.greedy = greedy
        self.decay = decay
