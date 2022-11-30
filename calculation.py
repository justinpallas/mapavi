import math
import numpy as np
import data as data

# Umrechnung von Frequenz in die Entsprechende Tonheit (Bark)


def conv_to_bark(frequency):
    if type(frequency) is list:
        bark = []
        for i in frequency:
            x = ((26.81*i)/(1960+i))-0.53
            bark.append(x)
        return bark
    else:
        bark = ((26.81*frequency)/(1960+frequency))-0.53
        return bark

# Umrechnung von Tonheit (Bark) in die Entsprechende Frequenz (Hz)


def conv_to_freq(bark):
    if type(bark) is list:
        frequency = []
        for i in bark:
            x = (1960*(i+0.53))/(26.28-i)
            frequency.append(x)
        return frequency
    else:
        frequency = (1960*(bark+0.53))/(26.28-bark)
        return frequency

# Berechnung des Verdeckungsmaßes av


def masking_index(frequency):
    index = -2 - math.log(1 + (frequency / 502)**2.5) / math.log(10)
    return index

# Berechnung der einzelnen Flanken der Mithörschwelle


def calculate_threshold(frequency, volume, freq_center, group):
    # Bestimmung ob linke oder rechte Flanke berechnet wird
    # mit 0 = linke Flanke, und 1 = rechte Flanke
    if group == 0:
        slope = 27  # Steigung S1 für linke Flanke
    elif group == 1:
        # Steigung S2 für rechte Flanke
        slope = -(24+(0.23/(freq_center/1000))-0.2*volume)
    center = conv_to_bark(freq_center)  # Bandmittenfrequenz in Bark
    bark = conv_to_bark(frequency)  # jeweilige Frequenz in Bark
    # Berechnung des Schnittpunkts mit der X-Achse
    n = -slope * center + volume
    zero = (-n)/slope
    # Berechnung und Ausgabe des entsprechenden Pegels der Mithörschwelle
    level = []
    for i in range(len(bark)):
        x = slope * (bark[i] - zero) + masking_index(freq_center)
        level.append(x)
    return level


def smoothing_line(frequency, volume, freq_center):
    level = []
    # Werte vor erster Mittenfrequenz festlegen
    for i in frequency:
        if i < freq_center[0]:
            level.append(-100)
    keys = []
    for i in range(len(freq_center)):
        keys.append(volume[i] + masking_index(freq_center[i]))
    for i in range(len(freq_center) - 1):
        m = (keys[i + 1] - keys[i])/(freq_center[i + 1] - freq_center[i])
        n = keys[i] - m * freq_center[i]
        for z in frequency:
            if z >= freq_center[i] and z < freq_center[i + 1]:
                y = m * z + n
                level.append(y)
    for i in frequency:
        if i >= freq_center[len(freq_center) - 1]:
            level.append(-100)
    return level


# Berechnen der Mithörschwelle eines einzelnen Schmalbandrauschens
def threshold(frequency, volume, freq_center):
    freq_low = []
    freq_high = []
    for i in frequency:
        if i <= freq_center:
            freq_low.append(i)
        elif i > freq_center:
            freq_high.append(i)
    level_low = calculate_threshold(freq_low, volume, freq_center, 0)
    level_high = calculate_threshold(freq_high, volume, freq_center, 1)
    level = level_low
    for i in level_high:
        level.append(i)
    return level

# Berechnen der Gesamtmithörschwelle mehrerer Schmalbandrauschen


def multi_threshold(frequency, volume, freq_center):
    levels = []
    for i in range(len(freq_center)):
        freq_low = []
        freq_high = []
        for n in frequency:
            if n <= freq_center[i]:
                freq_low.append(n)
            elif n > freq_center[i]:
                freq_high.append(n)
        level_low = calculate_threshold(freq_low, volume[i], freq_center[i], 0)
        level_high = calculate_threshold(
            freq_high, volume[i], freq_center[i], 1)
        level = (level_low)
        for n in level_high:
            level.append(n)
        levels.append(level)
    #print('levels = ' + str(levels))
    levels.append(smoothing_line(frequency, volume, freq_center))
    thresh = []
    for i in levels[0]:
        thresh.append(i)
    for i in range(len(freq_center) - 1):
        for n in range(len(frequency)):
            if thresh[n] < levels[i + 1][n]:
                thresh[n] = levels[i + 1][n]
    #print('thresh = ' + str(thresh))
    return thresh


def smoothed_threshold(frequency, volume, freq_center):
    out = []
    thresh = multi_threshold(frequency, volume, freq_center)
    smoothing = smoothing_line(frequency, volume, freq_center)
    for i in range(len(thresh)):
        if thresh[i] < smoothing[i]:
            out.append(smoothing[i])
        else:
            out.append(thresh[i])
    return out

# Berechnet das Terzband zur entsprechenden unteren-, oberen-, oder Mittenfrequenz


def get_third_band(freq, param):
    if param == 'low':
        low = freq
        high = freq * 1.26
        center = low + ((high - low)/2)
    elif param == 'high':
        low = freq / 1.26
        high = freq
        center = low + ((high - low)/2)
    elif param == 'center':
        low = (2*freq)/2.26
        high = low * 1.26
        center = freq
    return (low, center, high)

# Bestimmung der Bandbreite eines Terzbandes mit einer bestimmten Mittenfrequenz


def bandwidth(freq_center):
    band = get_third_band(freq_center, 'center')
    width = band[2] - band[0]
    return width

# Bestimmung der x- und y-Werte zum Einzeichnen der angegebenen Terzbänder


def signal(freq_center, volume, xy):
    signals = []
    for i in range(len(freq_center)):
        band = get_third_band(freq_center[i], 'center')
        signal = [
            (band[0], -10),
            (band[0], volume[i]),
            (band[1], volume[i]),
            (band[2], volume[i]),
            (band[2], -10)
        ]
        for n in signal:
            signals.append(n)
    x, y = list(map(list, zip(*signals)))
    if xy == 'x':
        return x
    elif xy == 'y':
        return y

# Aufteilen eines breitbandigen Signals in einzelne Terzen


def cut_to_thirds(signal):
    start = get_third_band(signal[0], 'low')
    end = get_third_band(signal[1], 'high')
    curr_band = start
    thirds = [curr_band]
    while curr_band[2] <= end[2]:
        curr_band = get_third_band(curr_band[2], 'low')
        thirds.append(curr_band)
    return thirds
