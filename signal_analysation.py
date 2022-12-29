import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import math
import calculation as calc
import data as data
from os.path import dirname, join as pjoin
from scipy.io import wavfile
from scipy import signal
import scipy.io
import octave_filter as filter


def read_file():
    data_dir = './sound_files'
    wav_fname = pjoin(data_dir, 'whitenoise_audition.wav')

    samplerate, data = wavfile.read(wav_fname)
    length = data.shape[0] / samplerate
    level = data

    spl, freq = filter.octavefilter(level, fs=samplerate, fraction=3, order=6)
    return spl, freq


# Zusammenfassung der Schallintensitäten aller Terzbänder innerhalb der jeweiligen Frequenzgruppenbänder für Frequenzen unterhalb 500 Hz
def critical_bands():
    spl, freq = read_file()
    I_zero = 10**(-12)
    log = 0
    levels = []
    freqs = []
    n = 0
    border_freqs = [100, 200, 300, 400, 510]
    for i in border_freqs:
        band_freqs = []
        sum = 0
        while freq[n] <= i:
            sum += calc.intensity(spl[n])
            band_freqs.append(freq[n])
            n += 1
        band_level = 10 * math.log10(sum/I_zero)
        for z in band_freqs:
            freqs.append(z)
            levels.append(band_level)
    while freq[n] < 16000:
        levels.append(spl[n])
        freqs.append(freq[n])
        n += 1
    return freqs, levels


freqs, levels = critical_bands()


def frequencies():
    return freqs


def volumes():
    return levels
