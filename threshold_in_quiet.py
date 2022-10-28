import calculation as calc

# Daten für Frequenzen und zugehörigen Pegeln der 
# Ruhehörschwelle unter Freifeldbedingungen
# aus DIN EN ISO 389-7:2020-06
# herausgegeben von DIN Deutsches Institut für Normung e. V. , DIN German Institute for Standardization

# data = [(Frequenz, Pegel)]
data = [
        (16, calc.threshold_in_quiet(16)),
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
        (22000, calc.threshold_in_quiet(22000))
        ]