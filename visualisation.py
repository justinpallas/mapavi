import matplotlib.pyplot as plt  # type: ignore
import matplotlib.ticker as mticker  # type: ignore
import calculation as calc
import data as data


def testdata(choice):
    testdata.bool = False
    testdata.test_freq = 250
    testdata.test_level = 60
    if choice == "250 Hz 60 dB":
        testdata.bool = True
        testdata.test_freq = 250
        testdata.test_level = 60
    elif choice == "1 kHz 40 dB":
        testdata.bool = True
        testdata.test_freq = 1000
        testdata.test_level = 40
    elif choice == "1 kHz 60 dB":
        testdata.bool = True
        testdata.test_freq = 1000
        testdata.test_level = 60
    elif choice == "1 kHz 80 dB":
        testdata.bool = True
        testdata.test_freq = 1000
        testdata.test_level = 80
    elif choice == "4 kHz 60 dB":
        testdata.bool = True
        testdata.test_freq = 4000
        testdata.test_level = 60
    elif choice == "nicht anzeigen":
        testdata.bool = False
        print("showing no testdata")
    if choice != "nicht anzeigen":
        print(
            "showing testdata for "
            + str(testdata.test_freq)
            + " Hz and "
            + str(testdata.test_level)
            + " dB"
        )


def thirdbands(switch):
    thirdbands.show = True
    if switch == "on":
        thirdbands.show = True
        print("displaying thirdbands")
    if switch == "off":
        thirdbands.show = False
        print("not displaying thirdbands")


testdata("nicht anzeigen")
thirdbands("on")

# Erstellen der Diagramme
# x -> X-Werte
# freq_center -> Liste Mit Terzband-Mittenfrequenzen
# volume -> Liste mit Terzpegeln
# smooth -> False: keine "Glättung" der Mithörschwelle
# (Für einzelne Terzbänder) | True: "Glättung" der Mithörschwelle


def render_plots(x, freq_center, volume, smooth=True, show_calibration="none"):
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(14, 15))

    ax1 = axs[0]
    ax2 = axs[1]

    # Frequenzen aufsteigend sortieren
    freq_center, volume = calc.sort_freqs(freq_center, volume)

    # Festlegung, ob der Graph "geglättet" werden soll, oder nicht
    thresh = calc.multi_threshold(x, volume, freq_center)
    smoothed = calc.smoothed_threshold(x, volume, freq_center)
    if smooth is True:
        y = smoothed
    else:
        y = thresh
    # Obergrenze für Pegel in Dagrammen in dB
    dBlim = 80

    # -- Diagramm für Darstellung in der Tonheit --
    # Allgemein
    ax1.grid(True)
    ax1.set_title("Darstellung in der Tonheit", fontsize=24)

    # X-Achse
    ax1.set_xlabel("Tonheit z [Bark]", fontsize=20)
    ax1.set_xlim([0, 24])
    # ax1.set_xscale('symlog')
    ax1.set_xticks([2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24])
    # ax1.get_xaxis().set_major_formatter(mticker.ScalarFormatter())

    # Y-Achse
    ax1.set_ylabel("Pegel L [dB]", fontsize=20)
    ax1.set_ylim([-10, dBlim])

    ax1.tick_params(axis="both", labelsize=16)

    # Darstellung der Ruhehörschwelle
    (line1,) = ax1.plot(calc.conv_to_bark(data.tiq_freq), data.tiq_level, "k--.")

    # Darstellung der ermittelten Terzbänder
    if thirdbands.show is True:
        (line2,) = ax1.plot(
            (calc.conv_to_bark(calc.signal(freq_center, volume, "x"))),
            calc.signal(freq_center, volume, "y"),
        )

    # Darstellung MHS von SBR
    (line3,) = ax1.plot(calc.conv_to_bark(x), y, "r")

    # Beschriftung der Graphen
    line1.set_label("Ruhehörschwelle nach DIN EN ISO 389-7:2020-06")
    line3.set_label("Mithörschwelle")
    # ax1.legend()

    # -- Diagramm mit Darstellung in der Frequenz --
    # Allgemein
    ax2.grid(True)
    ax2.set_title("Darstellung in der Frequenz", fontsize=24)

    # X-Achse
    ax2.set_xlabel("Frequenz f [Hz]", fontsize=20)
    ax2.set_xlim([16, 22000])
    ax2.set_xscale("symlog")
    ax2.set_xticks([16, 31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000])
    ax2.get_xaxis().set_major_formatter(mticker.ScalarFormatter())
    # Y-Achse
    ax2.set_ylabel("Pegel L [dB]", fontsize=20)
    ax2.set_ylim([-10, dBlim])

    ax2.tick_params(axis="both", labelsize=16)
    # Darstellung der Ruhehörschwelle
    (line1,) = ax2.plot(data.tiq_freq, data.tiq_level, "k--.")

    # Darstellung der ermittelten Terzbänder
    if thirdbands.show is True:
        (line2,) = ax2.plot(
            calc.signal(freq_center, volume, "x"),
            calc.signal(freq_center, volume, "y"),
            label="Ermittelte Terzbänder",
        )

    # Darstellung MHS von SBR
    (line3,) = ax2.plot(x, y, "r")

    # Beschriftung der Graphen
    line1.set_label("Ruhehörschwelle nach DIN EN ISO 389-7:2020-06")
    line3.set_label("Berechnete Mithörschwelle")

    if testdata.bool is True:
        freqs, levels = data.median_data(testdata.test_freq, testdata.test_level)

        # Darstellung Tonheit
        (line4,) = ax1.plot(calc.conv_to_bark(freqs), levels, "g")
        # Darstellung Frequenz
        (line4,) = ax2.plot(
            freqs,
            levels,
            "g",
            label=(
                "Median der Messwerte mit SBR bei fc = "
                + str(testdata.test_freq)
                + " Hz und L = "
                + str(testdata.test_level)
                + " dB als Maskierer"
            ),
        )

    if show_calibration != "none":
        ax1.text(
            1.5,
            75,
            show_calibration,
            style="italic",
            bbox={"facecolor": "green", "alpha": 0.5, "pad": 10},
            fontsize=16,
        )
        ax2.text(
            28,
            75,
            show_calibration,
            style="italic",
            bbox={"facecolor": "green", "alpha": 0.5, "pad": 10},
            fontsize=16,
        )

    # -- Anzeigen der Diagramme --
    ax2.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.37),
        fancybox=True,
        shadow=True,
        fontsize=16,
    )
    fig.tight_layout()
    plt.show()


# -- Schließen der Diagramme --


def close_plots():
    plt.close()


# render_plots(
#     data.samples(),
#     [1000],
#     [60],
#     smooth=False,
#     show_amp="mit 60 dB bei 500 Hz und 80 dB bei 1 kHz",
# )
