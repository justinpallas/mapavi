import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import visualisation as graph
import data as data

#signal=(start_freq, end_freq, volume)
signal=[
    (250, 1000, 60),
    (4000, 8000, 60),
]

thirds = []
for i in signal:
    cutted = calc.cut_to_thirds(i)
    for z in cutted:
        thirds.append(z)
low_freqs, center_freqs, high_freqs = list(map(list, zip(*thirds)))

freq_center = center_freqs  # Hz
volume = []  # dB

for n in range(len(signal)):
    for z in calc.cut_to_thirds(signal[n]):
        volume.append(signal[n][2])


#x = np.geomspace(1, 20000, 100)
x = data.samples()
#x = [10, 100, 1000, 4000, 10000, 16000]

graph.render_plots(x, freq_center, volume)
graph.draw_plots()
