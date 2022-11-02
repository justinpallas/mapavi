
# Daten für Frequenzen und zugehörigen Pegeln der 
# Ruhehörschwelle unter Freifeldbedingungen
# aus DIN EN ISO 389-7:2020-06
# herausgegeben von DIN Deutsches Institut für Normung e. V. , DIN German Institute for Standardization

# Berechnung der Ruhehörschwelle von gegebenen Frequenzen
def threshold_in_quiet(frequency):
    # Formel aus Skript TT2 Seite 23
    level = (3.64*(frequency/1000)**-0.8)-6.5**(-0.6*(frequency/1000-3.3)**2)+(10**-3)*(frequency/1000)**4
    return level

# tiq = [(Frequenz, Pegel)]
tiq = [
        (16, threshold_in_quiet(16)),
        (20, 78.1),
        (25, 68.7),
        (31.5, 59.5),
        (40, 51.1),
        (50, 44.0),
        (63, 37.5),
        (80, 31.5),
        (100, 26.5),
        (125, 22.1),
        (160, 17.9),
        (200, 14.4),
        (250, 11.4),
        (315, 8.6),
        (400, 6.2),
        (500, 4.4),
        (630, 3.0),
        (750, 2.4),
        (800, 2.2),
        (1000, 2.4),
        (1250, 3.5),
        (1500, 2.4),
        (1600, 1.7),
        (2000, -1.3),
        (2500, -4.2),
        (3000, -5.8),
        (3150, -6.0),
        (4000, -5.4),
        (5000, -1.5),
        (6000, 4.3),
        (6300, 6.0),
        (8000, 12.6),
        (9000, 13.9),
        (10000, 13.9),
        (11200, 13.0),
        (12500, 12.3),
        (14000, 18.4),
        (16000, 40.2),
        (18000, 70.4),
        (22000, threshold_in_quiet(22000))
]

tiq_freq, tiq_level = list(map(list, zip(*tiq)))


# Terzbänder nach EN ISO 266 "Normfrequenzen in Hz für akustische Messungen"

# thirds = [(Untere_Frequenz, Mittenfrequenz, Obere_Frequenz)]
thirds = [
        (22.4, 25, 28.2),
        (28.2, 31.5, 35.5),
        (35.5, 40, 44.7),
        (44.7, 50, 56.2),
        (56.2, 63, 70.8),
        (70.8, 80, 89.1),
        (89.1, 100, 112),
        (112, 125, 141),
        (141, 160, 178),
        (178, 200, 224),
        (224, 250, 282),
        (282, 315, 355),
        (355, 400, 447),
        (447, 500, 562),
        (562, 630, 708),
        (708, 800, 891),
        (891, 1000, 1122),
        (1122, 1250, 1413),
        (1413, 1600, 1778),
        (1778, 2000, 2239),
        (2239, 2500, 2818),
        (2818, 3150, 3548),
        (3548, 4000, 4467),
        (4467, 5000, 5623),
        (5623, 6300, 7079),
        (7079, 8000, 8913),
        (8913, 10000, 11220),
        (11220, 12500, 14130),
        (14130, 16000, 17780),
        (17780, 20000, 22390)
]

thirds_low, thirds_center, thirds_high = list(map(list, zip(*thirds)))
thirds_all = [i for sub in thirds for i in sub]

def samples():
        freqs = []
        for i in range(22000):
                freqs.append(i)
        return freqs