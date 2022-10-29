import numpy as np

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


def masked_threshold_low(frequency, volume, freq_center):
    slope = 27 # Steigung S1
    center = conv_to_bark(freq_center) # Bandmittenfrequenz in Bark
    bark = conv_to_bark(frequency) # jeweilige Frequenz in Bark
    # Berechnung des Schnittpunkts mit der X-Achse
    n = -slope * center + volume
    zero = (-n)/slope
    # Berechnung und Ausgabe des entsprechenden Pegels der Mithörschwelle
    level = []
    for i in bark:
        x = slope * (i - zero)
        level.append(x)
    return level


def masked_threshold_high(frequency, volume, freq_center):
    slope = -(24+(0.23/(freq_center/1000))-0.2*volume) # Steigung S2
    center = conv_to_bark(freq_center) # Bandmittenfrequenz in Bark
    bark = conv_to_bark(frequency) # jeweilige Frequenz in Bark
    # Berechnung des Schnittpunkts mit der X-Achse
    n = -slope * center + volume    
    zero = (-n)/slope
    # Berechnung und Ausgabe des entsprechenden Pegels der Mithörschwelle
    level = []
    for i in bark:
        x = slope * (i - zero)
        level.append(x)
    return level

# def masked_threshold(frequency, volume, freq_center):
#     # freq_low = np.minimum(frequency, freq_center)
#     # level_low = masked_threshold_low(freq_low, volume, freq_center)
#     # level_low, idx_low = np.unique(level_low, return_index=True)
#     # level_low = level_low[np.sort(idx_low)]
#     # print(level_low)

#     freq_high = np.maximum(frequency, freq_center)
#     count_high = np.count_nonzero(frequency < freq_center)
#     level_high = masked_threshold_high(freq_high, volume, freq_center)
#     for i in range(count_high):
#         level_high = np.delete(level_high, i)

    print(level_high)
    #levels = np.append(level_low, level_high)
    #level, idx = np.unique(levels, return_index=True)
    #print(level[np.sort(idx)])

# Berechnung der Ruhehörschwelle von gegebenen Frequenzen
def threshold_in_quiet(frequency):
    # Formel aus Skript TT2 Seite 23
    level = (3.64*(frequency/1000)**-0.8)-6.5**(-0.6*(frequency/1000-3.3)**2)+(10**-3)*(frequency/1000)**4
    return level