"""calculation.py: does all necessary calculations for masking pattern visualisation"""
import math
from bisect import bisect_left

# Umrechnung von Frequenz in die Entsprechende Tonheit (Bark)


def conv_to_bark(frequency):
    """converts given frequencies into bark"""
    # Unterscheidung ob Liste oder einzelner Wert umgewandelt werden soll
    if type(frequency) is list:
        # Umwandlung Liste von Frequenzwerten in Bark
        bark = []
        for i in frequency:
            x = ((26.81 * i) / (1960 + i)) - 0.53
            bark.append(x)
        return bark
        # Umwandlung eines einzelnen Frequenzwertes in Bark
    else:
        bark = ((26.81 * frequency) / (1960 + frequency)) - 0.53
        return bark


# Umrechnung von Tonheit (Bark) in die Entsprechende Frequenz (Hz)


def conv_to_freq(bark):
    """converts given bark values into frequencies"""
    # Unterscheidung ob Liste oder einzelner Wert umgewandelt werden soll
    if type(bark) is list:
        # Umwandlung Liste von Barkwerten in Frequenz
        frequency = []
        for i in bark:
            x = (1960 * (i + 0.53)) / (26.28 - i)
            frequency.append(x)
        return frequency
    else:
        # Umwandlung eines einzelnen Barkwerts in Frequenz
        frequency = (1960 * (bark + 0.53)) / (26.28 - bark)
        return frequency


# Berechnung der Schallintensität eines gegebenen Schallpegels
def intensity(level):
    """calculates the intensity of a given level"""
    I_zero = 10 ** (-12)  # Bezugsschallintensität
    if type(level) is list:
        intensity = []
        for i in level:
            x = I_zero * (10 ** (i / 10))
            intensity.append(x)
        return intensity
    else:
        intensity = I_zero * (10 ** (level / 10))
        return intensity


# Berechnung des Verdeckungsmaßes av


def masking_index(frequency):
    """calculates the masking index to a given frequency"""
    index = -(-2 - math.log(1 + (frequency / 502) ** 2.5) / math.log(10))
    return index


# Berechnung der einzelnen Flanken der Mithörschwelle


def calculate_threshold(frequency, volume, freq_center, group):
    """calculates the hearing threshold"""
    # Bestimmung ob linke oder rechte Flanke berechnet wird
    # mit 0 = linke Flanke, und 1 = rechte Flanke
    if group == 0:
        slope = 27  # Steigung S1 für linke Flanke
    elif group == 1:
        # Steigung S2 für rechte Flanke
        slope = -(24 + (0.23 / (freq_center / 1000)) - 0.2 * volume)
    center = conv_to_bark(freq_center)  # Bandmittenfrequenz in Bark
    bark = conv_to_bark(frequency)  # jeweilige Frequenz in Bark
    # Berechnung des Schnittpunkts mit der X-Achse
    n = -slope * center + volume
    zero = (-n) / slope
    # Berechnung und Ausgabe des entsprechenden Pegels der Mithörschwelle
    level = []
    for i in range(len(bark)):
        x = slope * (bark[i] - zero) - masking_index(freq_center)
        level.append(x)
    return level


# Berechnung einer Linie, welche durch alle Peaks der Mithörschwelle gezogen wird
# um diese als Filter zur Glättung der Mithörschwelle zu verwenden
def smoothing_line(frequency, volume, freq_center):
    """calculates a smoothing line which is used to smooth out the masking pattern"""
    level = []
    # Werte vor erster Mittenfrequenz festlegen
    for i in frequency:
        if i < freq_center[0]:
            level.append(-100)
    # Ermitteln aller Peaks in der Mithörschwelle
    keys = []
    for i in range(len(freq_center)):
        keys.append(volume[i] - masking_index(freq_center[i]))
    # Ermitteln der jeweiligen linearen Funktionen,
    # welche die Verbindungslinien zwischen allen Peaks beschreiben
    for i in range(len(freq_center) - 1):
        m = (keys[i + 1] - keys[i]) / (freq_center[i + 1] - freq_center[i])
        n = keys[i] - m * freq_center[i]
        # Füllen der level-Liste mit y-Werten,
        # die auf den entsprechenden Verbindungslinien liegen
        for z in frequency:
            if z >= freq_center[i] and z < freq_center[i + 1]:
                y = m * z + n
                level.append(y)
    # Werte nach letzter Mittenfrequenz festlegen
    for i in frequency:
        if i >= freq_center[len(freq_center) - 1]:
            level.append(-100)
    return level


# Berechnen der Mithörschwelle eines einzelnen Schmalbandrauschens
def threshold(frequency, volume, freq_center):
    """calculate the masking pattern of a single narrow band noise"""
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
    """calculate the masking pattern of multiple narrow band noises"""
    try:
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
            level_high = calculate_threshold(freq_high, volume[i], freq_center[i], 1)
            level = level_low
            for n in level_high:
                level.append(n)
            levels.append(level)
        # print('levels = ' + str(levels))
        levels.append(smoothing_line(frequency, volume, freq_center))
        thresh = []
        for i in levels[0]:
            thresh.append(i)
        for i in range(len(freq_center) - 1):
            for n in range(len(frequency)):
                if thresh[n] < levels[i + 1][n]:
                    thresh[n] = levels[i + 1][n]
        # print('thresh = ' + str(thresh))
        return thresh
    except:
        raise Exception(
            "Es ist ein Fehler bei der Berechnung der Mithörschwelle aufgetreten!"
        )


# Berechnung der "geglätteten" Mithörschwelle mithilfe der smoothing_line
def smoothed_threshold(frequency, volume, freq_center):
    """calculate a smoothed-out masking pattern using the smoothing line"""
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
    """calculate the third band to a given low, high, or center frequency"""
    if param == "low":
        if freq == 0:
            low = 0.001
        else:
            low = freq
        high = low * 1.26
        center = low + ((high - low) / 2)
    elif param == "high":
        high = freq
        low = high / 1.26
        center = low + ((high - low) / 2)
    elif param == "center":
        center = freq
        low = (2 * center) / 2.26
        high = low * 1.26
    return (low, center, high)


# Bestimmung der Bandbreite eines Terzbandes mit einer bestimmten Mittenfrequenz
def bandwidth(freq_center):
    """calculate the bandwidth of a thirdband with the given center frequency"""
    band = get_third_band(freq_center, "center")
    width = band[2] - band[0]
    return width


# Bestimmung der x- und y-Werte zum Einzeichnen der angegebenen Terzbänder
def signal(freq_center, volume, xy):
    """determine x- and y-values for visualization of the third bands"""
    signals = []
    for i in range(len(freq_center)):
        band = get_third_band(freq_center[i], "center")
        signal = [
            (band[0], -100),
            (band[0], volume[i]),
            (band[1], volume[i]),
            (band[2], volume[i]),
            (band[2], -100),
        ]
        for n in signal:
            signals.append(n)
    x, y = list(map(list, zip(*signals)))
    if xy == "x":
        return x
    elif xy == "y":
        return y


# Aufteilen eines breitbandigen Signals in einzelne Terzbänder
def cut_to_thirds(signal):
    """cuts a single broadband noise into multiple third bands"""
    if signal[0] < 0 or signal[1] < 0:
        raise Exception(
            "Fehler bei der Berechnung: Frequenzen dürfen nicht negativ sein!"
        )
    start = get_third_band(signal[0], "low")
    end = get_third_band(signal[1], "high")
    curr_band = start
    thirds = [curr_band]
    while curr_band[2] <= end[2]:
        curr_band = get_third_band(curr_band[2], "low")
        thirds.append(curr_band)
    return thirds


# Terzpegel für die entsprechende Art von Rauschen generieren
def get_volumes(signal, type):
    """generates the third band levels for the corresponding noise type"""
    volumes = []
    gap = len(cut_to_thirds((16, 500)))
    if type == "GAR":  # gleichmäßig anregendes Rauschen
        for n in range(len(signal)):
            thirds = cut_to_thirds(signal[n])
            for z in thirds:
                volumes.append(signal[n][2])
    elif type == "GVR":  # uniform masking noise / gleichmäßig verdeckendes Rauschen
        for n in range(len(signal)):
            thirds = cut_to_thirds(signal[n])
            for z in thirds:
                # das Verdeckungsmaß wird auf den Terzpegel addiert,
                # um den entsprechenden Abzug bei der
                # Mithörschwellenberechnung auszugleichen.
                # Das Verdeckungsmaß beträgt bei tiefen Frequenzen 2 dB.
                # Um die allgemeine Erhöhung um 2 dB auszugleichen,
                # werden außerdem frequenzunabhängig 2 dB abgezogen.
                level = signal[n][2] + masking_index(z[1]) - 2
                volumes.append(level)
    elif type == "weiß":
        for n in range(len(signal)):
            thirds = cut_to_thirds(signal[n])
            for z in thirds:
                freq_high = z[2]
                if freq_high <= 500:
                    volumes.append(signal[n][2])
                else:
                    distance = len(cut_to_thirds((500, freq_high))) - 1
                    level = signal[n][2] + distance
                    volumes.append(level)
    elif type == "rosa":
        for n in range(len(signal)):
            thirds = cut_to_thirds(signal[n])
            for z in thirds:
                freq_high = z[2]
                freq_low = z[0]
                if freq_high < 500:
                    distance = len(cut_to_thirds((freq_low, 500))) - 1
                    level = signal[n][2] + distance
                    volumes.append(level)
                else:
                    level = signal[n][2]
                    volumes.append(level)
    elif type == "rot":
        for n in range(len(signal)):
            thirds = cut_to_thirds(signal[n])
            for z in thirds:
                freq_high = z[2]
                freq_low = z[0]
                distance_low = len(cut_to_thirds((freq_low, 500))) - 1
                distance_high = len(cut_to_thirds((500, freq_high))) - 1
                if freq_high < 500:
                    level = signal[n][2] + (distance_low * 2)
                    volumes.append(level)
                else:
                    level = signal[n][2] - distance_high
                    volumes.append(level)
    elif type == "blau":
        for n in range(len(signal)):
            thirds = cut_to_thirds(signal[n])
            for z in thirds:
                freq_high = z[2]
                freq_low = z[0]
                if freq_high < 500:
                    distance = len(cut_to_thirds((freq_low, 500))) - 1
                    level = signal[n][2] - distance
                    volumes.append(level)
                else:
                    distance = len(cut_to_thirds((500, freq_high))) - 1
                    level = signal[n][2] + (distance * 2)
                    volumes.append(level)
    return volumes


# Lücken im Signal mit Pegeln bei -100 dB füllen,
# damit die GLättung richtig funktioniert
def fill_signal(signal):
    """fills gaps in signal automatically"""
    filled_signal = []
    filled_signal.append(signal[0])
    for n in range(len(signal) - 1):
        if signal[n + 1][0] > signal[n][1]:
            filled_signal.append((signal[n][1], signal[n + 1][0], -100))
        filled_signal.append(signal[n + 1])
    return filled_signal


def fill_thirds(freqs, levels):
    """fills gaps in thirds automatically"""
    filled_freqs = []
    filled_levels = []
    filled_freqs.append(freqs[0])
    filled_levels.append(levels[0])
    for n in range(len(freqs) - 1):
        curr_band = get_third_band(freqs[n], "center")
        next_band = get_third_band(freqs[n + 1], "center")
        if next_band[0] > curr_band[2]:
            fill_band = get_third_band(curr_band[2], "low")
            filled_freqs.append(fill_band[1])
            filled_levels.append(-100)
        filled_freqs.append(freqs[n + 1])
        filled_levels.append(levels[n + 1])
    return filled_freqs, filled_levels


def round_list(values):
    """rounds all values in a given list with 1 decimal"""
    rounded = []
    for value in values:
        rounded.append(round(value, 1))
    return rounded


def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before


def get_calibration(freqs, levels):
    freq_500 = take_closest(freqs, 500)
    index_500 = freqs.index(freq_500)
    level_500 = levels[index_500]
    freq_1000 = take_closest(freqs, 1000)
    index_1000 = freqs.index(freq_1000)
    level_1000 = levels[index_1000]
    return (round_list((freq_500, level_500)), round_list((freq_1000, level_1000)))
