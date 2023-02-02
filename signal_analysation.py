import pandas as pd  # type: ignore
import math
import calculation as calc
from scipy.io import wavfile  # type: ignore
import PyOctaveBand as filter


# Die Terzpegel aus Excel-Datei auslesen, welche von Artemis generitert wurde
def read_excel(filename):
    """reads third band levels from Excel-file"""
    df = pd.read_excel(
        filename,
        header=0,
        usecols="A:B",
    )
    data = df.to_dict()
    freqs = []
    levels = []
    for i in data["Frequenz in Hz"]:
        freqs.append(data["Frequenz in Hz"][i])
    for i in data["Pegel in dB"]:
        levels.append(data["Pegel in dB"][i])
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


def critical_bands(spl, freq, amp=0):
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
        band_level = 10 * math.log10(sum / I_zero) + amp
        for z in band_freqs:
            freqs.append(z)
            levels.append(band_level)
    while freq[n] < freq[length - 1]:
        levels.append(spl[n] + amp)
        freqs.append(freq[n])
        n += 1
    return freqs, levels


def get_third_levels(filename):
    """reads the third levels from a file"""
    if filename.endswith(".wav"):
        spl, freq = read_wav(filename)
    elif filename.endswith(".xlsx"):
        spl, freq = read_excel(filename)
    return spl, freq


def load_file(filename, amp=0):
    """loads a file with given"""
    spl, freq = get_third_levels(filename)
    freqs, levels = critical_bands(spl, freq, amp)
    return freqs, levels
