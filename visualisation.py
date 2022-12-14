import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import data as data

fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(8, 9))

# ------ Graphische Darstellung --------

ax1 = axs[0]
ax2 = axs[1]

def render_plots(x, freq_center, volume):
    thresh = calc.multi_threshold(x, volume, freq_center)
    smoothed = calc.smoothed_threshold(x, volume, freq_center)
    smoothing_line = calc.smoothing_line(x, volume, freq_center)
    y = thresh
    dBlim = 80
    example_freq = False
    example_level = 60


    # -- Diagramm für physikalisches Eingangssignal --
    # Allgemein
    ax1.grid(True)
    ax1.set_title("Darstellung in der Tonheit")

    # X-Achse
    ax1.set_xlabel("Tonheit z [Bark]")
    ax1.set_xlim([0, 24])
    # ax1.set_xscale('symlog')
    ax1.set_xticks([2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24])
    # ax1.get_xaxis().set_major_formatter(mticker.ScalarFormatter())

    # Y-Achse
    ax1.set_ylabel("Pegel L [dB]")
    ax1.set_ylim([-10, dBlim])

    # Darstellung der Ruhehörschwelle
    line1, = ax1.plot(calc.conv_to_bark(data.tiq_freq),
                      data.tiq_level, 'k--.')

    # Darstellung des bestimmten Terzbandes
    line2, = ax1.plot((calc.conv_to_bark(calc.signal(freq_center, volume, 'x'))),
                      calc.signal(freq_center, volume, 'y'))

    # Versuch Darstellung MHS von SBR
    line3, = ax1.plot(calc.conv_to_bark(x), y, 'r')

    # Darstellung der Ergebnisse des Hörversuchs vom 24.11.2022
    if example_freq != False:
        line4, = ax1.plot(calc.conv_to_bark(data.measured_example(
            example_freq, 'freq')), data.measured_example(example_freq, 'level'), 'g')

    # Beschriftung der Graphen
    line1.set_label('Ruhehörschwelle nach DIN EN ISO 389-7:2020-06')
    line2.set_label('Ermittelte Terzbänder')
    line3.set_label('Mithörschwelle')
    # ax1.legend()

    # -- Diagramm mit gehörgerechter Darstellung des Signals --
    # Allgemein
    ax2.grid(True)
    ax2.set_title("Darstellung in der Frequenz")

    # X-Achse
    ax2.set_xlabel("Frequenz f [Hz]")
    ax2.set_xlim([16, 22000])
    ax2.set_xscale('symlog')
    ax2.set_xticks([16, 31.5, 63, 125, 250, 500,
                   1000, 2000, 4000, 8000, 16000])
    ax2.get_xaxis().set_major_formatter(mticker.ScalarFormatter())

    # Y-Achse
    ax2.set_ylabel("Pegel L [dB]")
    ax2.set_ylim([-10, dBlim])

    # Darstellung der Ruhehörschwelle
    line1, = ax2.plot(data.tiq_freq, data.tiq_level, 'k--.')

    # Darstellung des bestimmten Terzbandes
    line2, = ax2.plot(calc.signal(freq_center, volume, 'x'),
                      calc.signal(freq_center, volume, 'y'))

    # Versuch Darstellung MHS von SBR
    line3, = ax2.plot(x, y, 'r')

    # Darstellung der Ergebnisse des Hörversuchs vom 24.11.2022
    if example_freq != False:
        line4, = ax2.plot(data.measured_example(example_freq, 'freq'),
                          data.measured_example(example_freq, 'level'), 'g')
        line4.set_label('Messwerte mit SBR bei fc = ' +
                        str(example_freq) + ' Hz und L =' + str(example_level) +  ' dB als Maskierer')

    # Beschriftung der Graphen
    line1.set_label('Ruhehörschwelle nach DIN EN ISO 389-7:2020-06')
    line2.set_label('Ermittelte Terzbänder')
    line3.set_label('Mithörschwelle')
    ax2.legend(loc='lower center', bbox_to_anchor=(
        0.5, -0.37), fancybox=True, shadow=True)

def show_test_data(freq, level):
    freqs, levels = data.median_data(freq, level)

    #Darstellung Tonheit
    line4, = ax1.plot(calc.conv_to_bark(freqs), levels, 'g')
    #Darstellung Frequenz
    line4, = ax2.plot(freqs, levels, 'g', label='Messwerte mit SBR bei fc = ' + 
    str(freq) + ' Hz und L =' + str(level) +  ' dB als Maskierer')
    line4.set_label('Messwerte mit SBR bei fc = ' + 
    str(freq) + ' Hz und L =' + str(level) +  ' dB als Maskierer')

# -- Anzeigen der Diagramme --
def draw_plots():
    fig.tight_layout()
    plt.show()
