import numpy as np

# Umrechnung von Frequenz in die Entsprechende Tonheit (Bark)
def conv_to_bark(frequency):
    bark = ((26.81*frequency)/(1960+frequency))-0.53
    return bark

# Umrechnung von Tonheit (Bark) in die Entsprechende Frequenz (Hz)
def conv_to_freq(bark):
    freq = (1960*(bark+0.53))/(26.28-bark)
    return freq

# Berechnung der Ruhehörschwelle von gegebenen Frequenzen
def threshold_in_quiet(frequency):
    # Formel aus Skript TT2 Seite 23
    level = (3.64*(frequency/1000)**-0.8)-6.5**(-0.6*(frequency/1000-3.3)**2)+(10**-3)*(frequency/1000)**4
    return level