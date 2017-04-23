
# Project under developement

A side project using Raspberry pi to train a simple auto car

the car contains only three sonic sensors which are **in front** and **+30/-30 degree** along the y-axis

three sensors <====> FPGA <==(UART)==> Raspberry pi

we normalize the distance  from **1 to 9 (0 means die)**

so total state would be **8^3 = 512**

three actions of **[left, go, right]**