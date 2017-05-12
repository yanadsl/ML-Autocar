import RpiEnv
import numpy as np

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
s = input('輸入正確答案:')
l = np.array([[i*0 for i in range(7)]], np.int8)
for a in s:
    if a.isnumeric():
        l[0][int(a)-1] = 1
if yeah:
    x_train = np.concatenate((x_train,distance))
    y_train = np.concatenate((y_train,l))
else:
    x_train = np.concatenate((distance))
    y_train = np.concatenate((l))

while True:
    input('準備讀取超音波 (請按Enter)')
    data = env.get_respond()
    distance = []
    for a in data:
        distance.append(int(a) / 2.0)
    distance = np.array([distance], np.float32)

    s = input('輸入正確答案:')
    if str(s) == 'q' or str(s) == 'quit':
        break
    l = np.array([[i * 0 for i in range(7)]], np.int8)
    for a in s:
        if a.isnumeric():
            l[0][int(a) - 1] = 1
    x_train = np.concatenate((x_train, distance))
    np.savetxt('x_train.txt', x_train, fmt='%d')
    y_train = np.concatenate((y_train, l))
    np.savetxt('y_train.txt', y_train, fmt='%d')