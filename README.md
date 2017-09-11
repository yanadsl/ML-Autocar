
# ML-AutoCar

A side project using Raspberry pi and reinforcement learning to train a simple auto car

The algorithm we used is not SARSA or Q-learning either(dismiss the annotation in the code), this algorithm need lots of works to tune the parms.

the car contains 3 sonic sensors which are **in front** and **+30/-30 degree** along the y-axis

with other 4 sonic sensors for error correction.

sonic sensor is very easy to get and error once the angle **over 50~60 degrees**

**!!!NEVER USE SONIC SENSORS IF YOU WANT TO DO SIMILAR EXPERIMENT!!!**

or it might be the SR-04 too cheap to handle this haha

## System Architecture 

sonic sensors <====> FPGA <==(UART)==> Raspberry pi

normalize the distance from **1 to 9 (0 means die)**

total state would be **8^3 = 512**

and three actions to do **[left, go, right]**

## Result

[https://youtu.be/hdKyGBblRRQ](https://youtu.be/hdKyGBblRRQ)

As you can see, the car works but it's really dumb



## Problems we face

1. Sonic sensors are really really unreliable. They are so unaccurate to give a consistant report

2. There are strange delay when chosing actions from **pandas**(python module) and from  **directly  programmed**.

We make an easy test to check the whole system's delay, diagram as below:

|   state   |    action   |
|:---------:|:-----------:|
|  too left |  turn right |
|   middle  | go straight |
| too right |  turn left  |

Set one for the normal learning process `get state -> get actions from pandas -> do action`

the other from directly programmed `get state -> get actions from the chart above -> do action`

To detect how delay works, I add `time()` from where the loop started, but both of them report almost the same time.

So we add delay ourselves and find out that **when using pandas, there're almost 80ms more delay but we cant find out why**




