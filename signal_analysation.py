import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import calculation as calc
import data as data
from os.path import dirname, join as pjoin
from scipy.io import wavfile
from scipy import signal
import scipy.io
import octave_filter as filter

data_dir = './sound_files'
wav_fname = pjoin(data_dir, 'whitenoise_audition.wav')

samplerate, data = wavfile.read(wav_fname)
length = data.shape[0] / samplerate
level = data

spl, freq = filter.octavefilter(level, fs=samplerate, fraction=3, order=6)

# plt.semilogy(frequencies, band_levels)
# plt.ylim([1e-7, 1e7]) 
# plt.xlim([16, 22000])
# plt.xscale('log')
# plt.xticks([16, 31.5, 63, 125, 250, 500,
#                    1000, 2000, 4000, 8000, 16000])
# ax = plt.gca()
# ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
# plt.xlabel('frequency [Hz]')
# plt.ylabel('PSD [V**2/Hz]')
# plt.show()

def freqs():
    return freq

def levels():
    return spl