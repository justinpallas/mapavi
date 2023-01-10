import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import data as data

# Erstellen der Diagramme
    # x -> X-Werte
    # freq_center -> Liste Mit Terzband-Mittenfrequenzen
    # volume -> Liste mit Terzpegeln
    # testdata -> False: Daten aus Hörversuchen nicht anzeigen | True: Daten aus Hörversuchen anzeigen (funktioniert nur, wenn zur Kombination aus freq_center und volume Testdaten vorliegen)
    # smooth -> False: keine "Glättung" der Mithörschwelle (Für einzelne Terzbänder) | True: "Glättung" der Mithörschwelle
    # example_freq -> False: kein Frequenzband aus Testdaten gewählt | 
def render_plots(x, freq_center, volume, testdata=False, smooth=True):
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(14, 15))

    ax1 = axs[0]
    ax2 = axs[1]

    # Festlegung, ob der Graph "geglättet" werden soll, oder nicht
    thresh = calc.multi_threshold(x, volume, freq_center)
    smoothed = calc.smoothed_threshold(x, volume, freq_center)
    if smooth == True:    
        y = smoothed
    else:
        y = thresh
    # Obergrenze für Pegel in Dagrammen in dB
    dBlim = 80 

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

    # Darstellung MHS von SBR
    line3, = ax1.plot(calc.conv_to_bark(x), y, 'r')

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

    # Darstellung MHS von SBR
    line3, = ax2.plot(x, y, 'r')

    # Beschriftung der Graphen
    line1.set_label('Ruhehörschwelle nach DIN EN ISO 389-7:2020-06')
    line2.set_label('Ermittelte Terzbänder')
    line3.set_label('Mithörschwelle')

    if testdata == True:
        freqs, levels = data.median_data(freq_center, volume)

        # Darstellung Tonheit
        line4, = ax1.plot(calc.conv_to_bark(freqs), levels, 'g')
        # Darstellung Frequenz
        line4, = ax2.plot(freqs, levels, 'g', label=('Median der Messwerte mit SBR bei fc = ' +
                        str(freq_center) + ' Hz und L =' + str(volume) + ' dB als Maskierer'))

# -- Anzeigen der Diagramme --
    ax2.legend(loc='lower center', bbox_to_anchor=(
        0.5, -0.37), fancybox=True, shadow=True)
    fig.tight_layout()
    plt.show()

# -- Schließen der Diagramme --


def close_plots():
    plt.close()
