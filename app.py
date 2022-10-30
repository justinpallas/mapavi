import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import visualisation as graph
import data as data

freq_center = 250 # Hz
volume = 60 # dB

#x = np.geomspace(1, 20000, 100)
x = data.samples()

graph.render_plots(x, freq_center, volume)
graph.draw_plots()
