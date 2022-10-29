import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import calculation as calc
import data as data

fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(8,7))

# ------ Graphische Darstellung -------- 

ax1 = axs[0]
ax2 = axs[1]

def render_plots(x, freq_center, volume):
    # -- Diagramm für physikalisches Eingangssignal --
    # Allgemein
    ax1.grid(True)
    ax1.set_title("Physikalisches Signal")
    
    # X-Achse
    ax1.set_xlabel("Frequenz f [Hz]")
    ax1.set_xlim([16, 22000])
    ax1.set_xscale('symlog')
    ax1.set_xticks([16, 31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000])
    ax1.get_xaxis().set_major_formatter(mticker.ScalarFormatter())
    
    # Y-Achse
    ax1.set_ylabel("Pegel L [dB]")
    ax1.set_ylim([-10, 130])

    # -- Diagramm mit gehörgerechter Darstellung des Signals --
    # Allgemein
    ax2.grid(True)
    ax2.set_title("Gehörgerechte Darstellung")
    
    # X-Achse
    ax2.set_xlabel("Frequenz f [Hz]")
    ax2.set_xlim([16, 22000])
    ax2.set_xscale('symlog')
    ax2.set_xticks([16, 31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000])
    ax2.get_xaxis().set_major_formatter(mticker.ScalarFormatter())
    
    # Y-Achse
    ax2.set_ylabel("Pegel L [dB]")
    ax2.set_ylim([-10, 130])
    
    # Darstellung der Ruhehörschwelle
    line1, = ax2.plot(data.tiq_freq, data.tiq_level, 'k--')
    
    # Versuch Darstellung MHS von SBR
    thresh = calc.masked_threshold(x, volume, freq_center)
    line2, = ax2.plot(x, thresh)
    
    # Beschriftung der Graphen
    line1.set_label('Ruhehörschwelle')
    line2.set_label("Mithörschwelle von SBR bei " + str(freq_center) + " Hz mit " + str(volume) + " dB")
    ax2.legend()


# -- Anzeigen der Diagramme --
def draw_plots():
    fig.tight_layout()
    plt.show()