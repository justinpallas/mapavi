import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import visualisation as graph
import data as data
import signal_analysation as analyzed

#params=(start_freq, end_freq, volume)
signal = [
    (0, 2000, 40),
    (2000, 5000, -100),
    (5000, 20000, 60)
]
type = 'white'  # white = weißes Rauschen, pink = rosa Rauschen

thirds = []
for i in signal:
    cutted = calc.cut_to_thirds(i)
    for z in cutted:
        thirds.append(z)
low_freqs, center_freqs, high_freqs = list(map(list, zip(*thirds)))


#freq_center = center_freqs
freq_center = [250, 1000, 4000]  # Hz
#freq_center = analyzed.frequencies()
#volume = calc.get_volumes(signal, type)
volume = [60, 80, 60]  # dB
#volume = analyzed.volumes()

sig = []
for n in range(len(freq_center)):
    sig.append((freq_center[n], volume[n]))
# print(sig)


#x = np.geomspace(1, 20000, 100)
x = data.samples()
#x = [10, 100, 1000, 4000, 10000, 16000]

#print(data.find_mid_values(data.get_test_data()[0]))
graph.render_plots(x, freq_center, volume)
#data.median_data(1000, 60)
graph.show_test_data(1000, 80)
graph.draw_plots()
