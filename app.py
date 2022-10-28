import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import visualisation as graph

freq_center = 1000 # Hz
volume = 100 # dB

x = np.geomspace(1, 20000, 100)

graph.render_plots(x, freq_center, volume)
graph.draw_plots()