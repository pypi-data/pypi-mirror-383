#!/usr/bin/env python3
# -*- encoding: utf8 -*-

__docformat__ = "numpy"

from datetime import date


def calc_easter(year: int) -> date:
    """Calculates the date of easter.

    The calculation of the Easter Sunday by following the formula by Karl Friedrich Gauss.
    A Detailed description can be read on the following website: https://de.wikipedia.org/wiki/Gau%C3%9Fsche_Osterformel

    Args:
    -----
        year : int
            The year for which the date of Easter should be calculated

    Returns:
    --------
        easter_day : date
            A datetime object which is set to the date of easter

    Examples:
    ---------
        >>> from feiertage import easter
        >>> easter.calc_easter(2023)    # example year: 2023
        datetime.date(2023,4,9)
    """

    K = year // 100                                 # Säkular-zahl
    M = 15 + (3 * K + 3) // 4 - (8 * K + 13) // 25  # säkulare Mondschaltung
    S = 2 - (3 * K + 3) // 4                        # säkulare Sonnenschaltung
    A = year % 19                                   # Mondparameter
    D = (19 * A + M) % 30                           # Keim für den ersten Vollmond im Frühling
    R = D // 29 + (D // 28 - D // 29) * (A // 11)   # Kalendarische korrekturgröße
    OG = 21 + D - R                                 # Ostergrenze
    SZ = 7 - (year + year // 4 + S) % 7             # erster Sonntag im März
    OE = 7 - (OG - SZ) % 7                          # Entfernung des Ostersonntags von der Ostergrenze
    OS = OG + OE                                    # Datum des Ostersonntags als Märzdatum

    if OS > 31:
        easter_day = date(year, 4, OS - 31)
    else:
        easter_day = date(year, 3, OS)
    return easter_day
