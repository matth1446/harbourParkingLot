import matplotlib.pyplot as mpl
import pandas as pd
import numpy as np

#chart 1 -
#createing ficticious data to plot.
gates = [1,2,3,4]
data_y1 = [10, 20, 30, 40]
data_y2 = [20, 30, 40, 50]
data_x = np.arange(len(gates))
#Creating the Figure container
fig = mpl.figure(figsize=(9,5))
#Creating the axis
ax = fig.add_subplot()
#Line plot command
ax.bar(data_x, data_y1, label='Vehicles handled')
ax.bar(data_x, data_y2, bottom = data_y1, label='Vehicles waiting')
ax.set_ylabel('Vehicles')
ax.set_xlabel('Gates')
ax.set_title('Handled Vehicles per Gate')
ax.legend()

ax.set_xticks(data_x, gates)
#ax.grid()
mpl.show()