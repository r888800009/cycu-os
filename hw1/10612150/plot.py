#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np

x = [10000, 100000, 500000, 1000000]
bubblesort = [0.1261167526, 11.30908847, 283.9312696, 1157.237283]
process = [0.0893228054, 1.127340794, 21.58810401, 86.55200291]
thread = [0.5930533409, 3.272245169, 74.93181825, 292.4291878]
merge = [0.1272084713, 3.757363558, 75.82278562, 296.1974378]


plt.plot(x, bubblesort)
plt.plot(x, process)
plt.plot(x, thread)
plt.plot(x, merge)
plt.legend(('Bubble sort', 'K Process', 'K Thread', 'One Process'),
loc='upper left', shadow=True)

plt.xlabel('Data Size (10 ^ 6)')
plt.ylabel('Time (Second)')
plt.grid(True)

plt.savefig('fig1.png')

plt.clf()
x = [10000, 100000, 500000, 1000000]
process = [0.1521923542, 3.380565882, 74.10192752, 286.828119]
thread = [0.07281732559, 3.204283237, 71.91410947, 284.5606923]

plt.plot(x, process)
plt.plot(x, thread)

plt.legend(('K Process', 'K Thread'),
loc='upper left', shadow=True)

plt.title('Only One Core')
plt.xlabel('Data Size (10 ^ 6)')
plt.ylabel('Time (Second)')
plt.grid(True)

plt.savefig('fig2.png')
