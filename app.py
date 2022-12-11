import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import visualisation as graph
import data as data
import signal_analysation as signal

#params=(start_freq, end_freq, volume)
params = [
    (0, 1000, 60)
]
type = 'pink'  # white = weißes Rauschen, pink = rosa Rauschen

thirds = []
for i in params:
    cutted = calc.cut_to_thirds(i)
    for z in cutted:
        thirds.append(z)
low_freqs, center_freqs, high_freqs = list(map(list, zip(*thirds)))


#freq_center = center_freqs
#freq_center = [250, 1000, 4000]  # Hz
freq_center = signal.freqs()
#volume = calc.get_volumes(type)
#volume = [60, 60, 60]  # dB
volume = signal.levels()
print(volume)


#x = np.geomspace(1, 20000, 100)
x = data.samples()
#x = [10, 100, 1000, 4000, 10000, 16000]

#print(data.measured_example(4000, 'toggle'))
graph.render_plots(x, freq_center, volume)
graph.draw_plots()
