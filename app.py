import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import visualisation as graph
import data as data

#signal=(start_freq, end_freq, volume)
signal=(400, 1000, 60)

freq_center = [800, 1000, 1250]  # Hz
volume = [60, 60, 60]  # dB


#x = np.geomspace(1, 20000, 100)
x = data.samples()
#x = [10, 100, 1000, 4000, 10000, 16000]
print(calc.get_third_band(signal[1], 'center'))

graph.render_plots(x, freq_center, volume)
graph.draw_plots()
