import json
import os, glob
from scipy.interpolate import interp1d
import statistics

# Berechnung der Ruhehörschwelle von gegebenen Frequenzen
def threshold_in_quiet(frequency):
    # Formel aus Skript TT2 Seite 23
    level = (3.64*(frequency/1000)**-0.8)-6.5**(-0.6*(frequency/1000-3.3)**2)+(10**-3)*(frequency/1000)**4
    return level

# Daten für Frequenzen und zugehörigen Pegeln der 
# Ruhehörschwelle unter Freifeldbedingungen
# aus DIN EN ISO 389-7:2020-06
# herausgegeben von DIN Deutsches Institut für Normung e. V. , DIN German Institute for Standardization

# tiq = [(Frequenz, Pegel)]
tiq = [
        (16, threshold_in_quiet(16)),
        (20, 78.1),
        (25, 68.7),
        (31.5, 59.5),
        (40, 51.1),
        (50, 44.0),
        (63, 37.5),
        (80, 31.5),
        (100, 26.5),
        (125, 22.1),
        (160, 17.9),
        (200, 14.4),
        (250, 11.4),
        (315, 8.6),
        (400, 6.2),
        (500, 4.4),
        (630, 3.0),
        (750, 2.4),
        (800, 2.2),
        (1000, 2.4),
        (1250, 3.5),
        (1500, 2.4),
        (1600, 1.7),
        (2000, -1.3),
        (2500, -4.2),
        (3000, -5.8),
        (3150, -6.0),
        (4000, -5.4),
        (5000, -1.5),
        (6000, 4.3),
        (6300, 6.0),
        (8000, 12.6),
        (9000, 13.9),
        (10000, 13.9),
        (11200, 13.0),
        (12500, 12.3),
        (14000, 18.4),
        (16000, 40.2),
        (18000, 70.4),
        (22000, threshold_in_quiet(22000))
]

tiq_freq, tiq_level = list(map(list, zip(*tiq)))


# Terzbänder nach EN ISO 266 "Normfrequenzen in Hz für akustische Messungen"

# thirds = [(Untere_Frequenz, Mittenfrequenz, Obere_Frequenz)]
thirds = [
        (22.4, 25, 28.2),
        (28.2, 31.5, 35.5),
        (35.5, 40, 44.7),
        (44.7, 50, 56.2),
        (56.2, 63, 70.8),
        (70.8, 80, 89.1),
        (89.1, 100, 112),
        (112, 125, 141),
        (141, 160, 178),
        (178, 200, 224),
        (224, 250, 282),
        (282, 315, 355),
        (355, 400, 447),
        (447, 500, 562),
        (562, 630, 708),
        (708, 800, 891),
        (891, 1000, 1122),
        (1122, 1250, 1413),
        (1413, 1600, 1778),
        (1778, 2000, 2239),
        (2239, 2500, 2818),
        (2818, 3150, 3548),
        (3548, 4000, 4467),
        (4467, 5000, 5623),
        (5623, 6300, 7079),
        (7079, 8000, 8913),
        (8913, 10000, 11220),
        (11220, 12500, 14130),
        (14130, 16000, 17780),
        (17780, 20000, 22390)
]

thirds_low, thirds_center, thirds_high = list(map(list, zip(*thirds)))
thirds_all = [i for sub in thirds for i in sub]

# Bestimmung welchem Terzband die jeweilige Frequenz am nächsten ist
# und Rückgabe des entsprechenden Terzbands
# Unterscheidung ob mit Mittenfrequenz, Startfrequenz, oder Endfrequenz des Bands verglichen wird
def get_third_band(freq, param):
    n = 0
    if param == 'center':
        list = thirds_center
    elif param == 'low':
        list = thirds_low
    elif param == 'high':
        list = thirds_high
    for i in list:
        if freq > i:
            n += 1
    if freq == list[n]:
        return list[n]
    else:
        diff_up = list[n] - freq
        diff_down = freq - list[n-1]
        if diff_up < diff_down:
            return list[n]
        elif diff_up > diff_down:
            return list[n-1]
        else: 
            return list[n]

# Unterteilung des Eingegebenen Signals in Terzbänder, welche in der thirds Liste enthalten sind.
def cut_to_thirds(signal):
    start = get_third_band(signal[0], 'low')
    end = get_third_band(signal[1], 'high')
    n = 0
    thirds = []
    while start != thirds[n]:
        n += 1
    thirds.append(start)
    while thirds[n] != end:
        n += 1
        thirds.append(thirds[n])
    return thirds

# Generierung von x-Werten von 0 Hz bis 22000 Hz
def samples():
        freqs = []
        for i in range(22000):
                freqs.append(i)
        return freqs

def measured_example(freq, spec):
    if freq == 1000:
        with open('./measured_data/2022-11-24 Messungen/2022-11-24_Justin_Pallas_links_MHS_SBR_1kHz.json', 'r') as read_file:
            file = json.load(read_file)
    elif freq == 4000:
        with open('./measured_data/2022-11-24 Messungen/2022-11-24_Justin_Pallas_links_MHS_SBR_4kHz.json', 'r') as read_file:
            file = json.load(read_file)
    elif freq == 250:
        with open('./measured_data/2022-11-24 Messungen/2022-11-24_Justin_Pallas_links_MHS_SBR_250Hz.json', 'r') as read_file:
            file = json.load(read_file)
    values = []
    data = file['Data']
    for key in data:
        values.append(data[key])
    if spec == 'all':
        return values
    else: 
        freqs, levels, toggle = list(map(list, zip(*values)))
        if spec == 'freq':
            return freqs
        elif spec == 'level':
            return levels
        elif spec == 'toggle':
            return toggle

def get_path(freq, volume):
    if volume == 60:
        if freq == -1:
            path = './measured_data/threshold_in_quiet'
        elif freq == 250:
            path = './measured_data/nbn_250Hz_60dB'
        elif freq == 1000:
            path = './measured_data/nbn_1kHz_60dB'
        elif freq == 4000:
            path = './measured_data/nbn_4kHz_60dB'
    elif volume == 40:
        path = './measured_data/nbn_1kHz_40dB'
    elif volume == 80:
        path = './measured_data/nbn_1kHz_80dB'
    return path

def get_test_data(freq=-1, volume=60):
    data = []
    path = get_path(freq, volume)
    print(path)
    for filename in glob.glob(os.path.join(path, '*.json')):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            file = json.load(f)
            values = []
            content = file['Data']
            for key in content:
                 values.append(content[key])
            data.append(values)
    return data

def find_mid_values(dataset):
    values = []
    for n in range(len(dataset)-1):
        freq_mid = dataset[n][0] + (dataset[n+1][0] - dataset[n][0])
        level_mid = dataset[n][1] + (dataset[n+1][1] - dataset[n][1])
        mid = (freq_mid, level_mid)
        values.append(mid)
    return values

def comparable_list(dataset):
    comp = []
    freqs, levels = list(map(list, zip(*dataset)))
    f = interp1d(freqs, levels, kind='linear', bounds_error=False, fill_value=-100)
    for i in thirds_all:
        level = f(i)
        comp.append((i, level))
    return comp

def median_data(freq=-1, volume=60):
    median_levels = []
    comps = []
    freqs = []
    data = get_test_data(freq, volume)
    for i in data:
        mid = find_mid_values(i)
        comp = comparable_list(mid)
        comps.append(comp)
    for n in range(len(comps[0])):
        levels = []
        frequency = comps[0][n][0]
        for z in range(len(comps)):
            level = comps[z][n][1]
            levels.append(level)
        median = statistics.median(levels)
        median_levels.append(median)
        freqs.append(frequency)
    return freqs, median_levels
        
