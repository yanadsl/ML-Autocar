import RpiEnv
import numpy as np

env = RpiEnv.Env()
input('準備讀取超音波 (請按Enter)')
data = env.get_respond()
distance = []
for a in data:
    distance.append(int(a) / 2.0)
distance = np.array(distance, np.float32)
s = input('輸入正確答案:')
l = np.array([i*0 for i in range(7)], np.int8)
for a in s:
    if a.isnumeric():
        l[int(a)-1] = 1
x_train = np.stack((distance))
y_train = np.stack((l))

while True:
    input('準備讀取超音波 (請按Enter)')
    data = env.get_respond()
    distance = []
    for a in data:
        distance.append(int(a) / 2.0)
    distance = np.array(distance, np.float32)
    s = input('輸入正確答案:')
    if str(s) == 'q' or str(s) == 'quit':
        break;
    l = np.array([i * 0 for i in range(7)], np.int8)
    for a in s:
        if a.isnumeric():
            l[int(a) - 1] = 1
    x_train = np.stack((x_train, distance))
    np.savetxt('x_train.txt', x_train, fmt='%d')
    y_train = np.stack((y_train, l))
    np.savetxt('y_train.txt', y_train, fmt='%d')

from keras.datasets import mnist
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import RMSprop, SGD

# Another way to build your neural net
model = Sequential([
    Dense(8, input_dim=7),
    Activation('sigmoid'),
    Dense(4),
    Activation('sigmoid')
])

# Another way to define your optimizer
rmsprop = RMSprop(lr=0.1, rho=0.9, epsilon=1e-08, decay=0.0)
# rmsprop = RMSprop(lr=0.1)
sgd = SGD(lr=0.5, decay=0, momentum=0.9, nesterov=True)

# We add metrics to get more results you want to see
model.compile(optimizer=rmsprop,
              loss='binary_crossentropy',
              metrics=['accuracy'])

print('Training ------------')
# Another way to train the model
model.fit(x_train, y_train, epochs=100, batch_size=32)

print('\nTesting ------------')
# Evaluate the model with the metrics we defined earlier
loss, accuracy = model.evaluate(x_train, y_train)

print('test loss: ', loss)
print('test accuracy: ', accuracy)
model.save('sonic_predict.h5')
