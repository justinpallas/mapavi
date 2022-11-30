import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import visualisation as graph
import data as data

#signal=(start_freq, end_freq, volume)
signal = [
    (1, 1000, 60)
]
type = 'pink'  # white = weißes Rauschen, pink = rosa Rauschen

thirds = []
for i in signal:
    cutted = calc.cut_to_thirds(i)
    for z in cutted:
        thirds.append(z)
low_freqs, center_freqs, high_freqs = list(map(list, zip(*thirds)))


def get_volumes(type):
    volumes = []
    if type == 'pink':
        for n in range(len(signal)):
            thirds = calc.cut_to_thirds(signal[n])
            for z in thirds:
                volumes.append(signal[n][2])
    elif type == 'white':
        for n in range(len(signal)):
            thirds = calc.cut_to_thirds(signal[n])
            for z in thirds:
                freq_high = z[2]
                if freq_high <= 500:
                    volumes.append(signal[n][2])
                else:
                    distance = len(calc.cut_to_thirds((500, freq_high)))
                    level = signal[n][2] + distance - 1
                    volumes.append(level)
    return volumes


#freq_center = center_freqs
freq_center = [250, 1000, 4000]  # Hz
#volume = get_volumes(type)
volume = [60, 60, 60]  # dB


#x = np.geomspace(1, 20000, 100)
x = data.samples()
#x = [10, 100, 1000, 4000, 10000, 16000]

#print(data.measured_example(4000, 'toggle'))
graph.render_plots(x, freq_center, volume)
graph.draw_plots()
