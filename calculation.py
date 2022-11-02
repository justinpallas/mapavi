import math
import numpy as np
import data as data

# Umrechnung von Frequenz in die Entsprechende Tonheit (Bark)
# def conv_to_bark(frequency):
#     bark = ((26.81*frequency)/(1960+frequency))-0.53
#     return bark
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
    index = -2 - math.log(1 + (frequency / 502 )**2.5) / math.log(10)
    return index

# Berechnung der einzelnen Flanken der Mithörschwelle
def calculate_threshold(frequency, volume, freq_center, group):
    # Bestimmung ob linke oder rechte Flanke berechnet wird
    # mit 0 = linke Flanke, und 1 = rechte Flanke
    if group == 0:
        slope = 27 # Steigung S1 für linke Flanke
    elif group == 1:
        slope = -(24+(0.23/(freq_center/1000))-0.2*volume) # Steigung S2 für rechte Flanke
    center = conv_to_bark(freq_center) # Bandmittenfrequenz in Bark
    bark = conv_to_bark(frequency) # jeweilige Frequenz in Bark
    # Berechnung des Schnittpunkts mit der X-Achse
    n = -slope * center + volume    
    zero = (-n)/slope
    # Berechnung und Ausgabe des entsprechenden Pegels der Mithörschwelle
    level = []
    for i in range(len(bark)):
        x = slope * (bark[i] - zero) + masking_index(freq_center)
        level.append(x)
    return level


def masked_threshold(frequency, volume, freq_center):
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

# Bestimmung welchem Terzband die jeweilige Mittenfrequenz am nächsten ist
# und Rückgabe des entsprechenden Terzbands
def get_third_band(freq_center):
    n = 0
    for i in data.thirds_center:
        if freq_center > i:
            n += 1
    if freq_center == data.thirds_center[n]:
        return data.thirds[n]
    else:
        diff_up = data.thirds_center[n] - freq_center
        diff_down = freq_center - data.thirds_center[n-1]
        if diff_up < diff_down:
            return data.thirds[n]
        elif diff_up > diff_down:
            return data.thirds[n-1]
        else: 
            return data.thirds[n]
        
def bandwidth(freq_center):
    band = get_third_band(freq_center)
    width = band[2] - band[0]
    return width

def signal(freq_center, volume, xy):
    band = get_third_band(freq_center)
    signal = [
        (band[0], -10),
        (band[0], volume),
        (band[1], volume),
        (band[2], volume),
        (band[2], -10)
    ]
    x, y = list(map(list, zip(*signal)))
    if xy == 'x':
        return x
    elif xy == 'y':
        return y

