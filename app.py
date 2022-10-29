import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import visualisation as graph
import data as data

freq_center = 1000 # Hz
volume = 100 # dB

#x = np.geomspace(1, 20000, 100)
x = data.thirds_center

graph.render_plots(x, freq_center, volume)
graph.draw_plots()
