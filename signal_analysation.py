import pandas as pd  # type: ignore
import math
import calculation as calc
from scipy.io import wavfile  # type: ignore
import PyOctaveBand as filter


# Die Terzpegel aus Excel-Datei auslesen, welche von Artemis generitert wurde
def read_excel(filename):
    """reads third band levels from Excel-file"""
    df = pd.read_excel(filename, header=12, usecols="A:B", skiprows=[13])
    data = df.to_dict()
    freqs = []
    levels = []
    for i in data["Hz"]:
        freqs.append(data["Hz"][i])
    for i in data["dB(SPL)"]:
        levels.append(data["dB(SPL)"][i])
    return levels, freqs


# Die Terzpegel mithilfe eines Terzfilters aus Wave Datei bestimmen
def read_wav(filename):
    """reads third band levels from wav-file"""
    samplerate, data = wavfile.read(filename)
    level = data

    spl, freq = filter.octavefilter(level, fs=samplerate, fraction=3, order=6)
    return spl, freq


# Zusammenfassung der Schallintensitäten aller Terzbänder innerhalb der jeweiligen
# Frequenzgruppenbänder für Frequenzen unterhalb 500 Hz


def critical_bands(spl, freq):
    """calculates the levels of the critical bands"""
    I_zero = 10 ** (-12)
    levels = []
    freqs = []
    n = 0
    length = len(freq)
    border_freqs = [100, 200, 300, 400, 500]
    for i in border_freqs:
        band_freqs = []
        sum = 0
        while freq[n] < i:
            sum += calc.intensity(spl[n])
            band_freqs.append(freq[n])
            n += 1
        if sum == 0:
            sum = calc.intensity(spl[n - 1])
        band_level = 10 * math.log10(sum / I_zero)
        for z in band_freqs:
            freqs.append(z)
            levels.append(band_level)
    while freq[n] < freq[length - 1]:
        levels.append(spl[n])
        freqs.append(freq[n])
        n += 1
    return freqs, levels


def load_file(filename):
    """loads a file with given"""
    if filename.endswith(".wav"):
        spl, freq = read_wav(filename)
    elif filename.endswith(".xlsx"):
        spl, freq = read_excel(filename)
    freqs, levels = critical_bands(spl, freq)
    return freqs, levels
