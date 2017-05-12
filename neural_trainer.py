import RpiEnv
import numpy as np
import sys
from keras.models import load_model

model = load_model('my_model.h5')
np.set_printoptions(precision=2)
yeah = False
env = RpiEnv.Env()
y_train = np.array([])
x_train = np.array([])
try:
    y_train = np.loadtxt('y_train.txt', dtype=float)
    x_train = np.loadtxt('x_train.txt', dtype=int)
    yeah = True
except:
    print('Nda')
input('準備讀取超音波 (請按Enter)')
data = env.get_respond()
distance = []
for a in data:
    distance.append(int(a) / 2.0)
print(distance)
distance = np.array([distance], np.float32)
print('預測')
print(model.predict(distance))
s = input('輸入正確答案:')
l = np.array([[i*0 for i in range(7)]], np.int8)
for a in s:
    if a.isnumeric():
        l[0][int(a)-1] = 1
if yeah:
    x_train = np.concatenate((x_train, distance))
    y_train = np.concatenate((y_train, l))
else:
    x_train = distance
    y_train = l
w = 1
while True:
    w += 1
    print('第' + str(w) + '次')
    input('準備讀取超音波 (請按Enter)')
    data = env.get_respond()
    distance = []
    for a in data:
        distance.append(int(a) / 2.0)
    print(distance)
    distance = np.array([distance], np.float32)
    print('預測')
    print(model.predict(distance))

    s = input('輸入正確答案:')
    if str(s) == 'n':
        w -= 1
        continue
    if str(s) == 'q' or str(s) == 'quit':
        sys.exit(0)
    l = np.array([[i * 0 for i in range(7)]], np.int8)
    for a in s:
        if a.isnumeric():
            l[0][int(a) - 1] = 1
    x_train = np.concatenate((x_train, distance))
    np.savetxt('x_train.txt', x_train, fmt='%d')
    y_train = np.concatenate((y_train, l))
    np.savetxt('y_train.txt', y_train, fmt='%d')
