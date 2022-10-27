import numpy as np

# Umrechnung von Frequenz in die Entsprechende Tonheit (Bark)
def conv_to_bark(frequency):
    bark = ((26.81*frequency)/(1960+frequency))-0.53
    return bark

# Umrechnung von Tonheit (Bark) in die Entsprechende Frequenz (Hz)
def conv_to_freq(bark):
    freq = (1960*(bark+0.53))/(26.28-bark)
    return freq


def masked_threshold_low(frequency, volume, freq_center):
    slope = 27 # Steigung S1
    center = conv_to_bark(freq_center) # Bandmittenfrequenz in Bark
    bark = conv_to_bark(frequency) # jeweilige Frequenz in Bark
    # Berechnung des Schnittpunkts mit der X-Achse
    n = -slope * center + volume    
    zero = (-n)/slope
    # Berechnung und Ausgabe des entsprechenden Pegels der Mithörschwelle
    level = slope * (bark - zero)
    return level

def masked_threshold_high(frequency, volume, freq_center):
    slope = -(24+(0.23/(freq_center/1000))-0.2*volume) # Steigung S2
    center = conv_to_bark(freq_center) # Bandmittenfrequenz in Bark
    bark = conv_to_bark(frequency) # jeweilige Frequenz in Bark
    # Berechnung des Schnittpunkts mit der X-Achse
    n = -slope * center + volume    
    zero = (-n)/slope
    # Berechnung und Ausgabe des entsprechenden Pegels der Mithörschwelle
    level = slope * (bark - zero)
    return level

# Berechnung der Ruhehörschwelle von gegebenen Frequenzen
def threshold_in_quiet(frequency):
    # Formel aus Skript TT2 Seite 23
    level = (3.64*(frequency/1000)**-0.8)-6.5**(-0.6*(frequency/1000-3.3)**2)+(10**-3)*(frequency/1000)**4
    return level