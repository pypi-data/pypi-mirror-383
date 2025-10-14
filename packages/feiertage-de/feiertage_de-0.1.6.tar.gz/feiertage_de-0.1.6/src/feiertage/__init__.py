#!/usr/bin/env python3

__docformat__ = "numpy"

"""Calculate the holidays for a specified federal state of Germany within a given year

During the initialisation of a `Holiday` object all the holidays for the given state within the given year will be calculated. These will be assigned by the following table: https://de.wikipedia.org/wiki/Gesetzliche_Feiertage_in_Deutschland#%C3%9Cbersicht_aller_gesetzlichen_Feiertage
"""

import sys
from datetime import date, timedelta
from . import easter

states = {
    'Deutschland': 'DE',
    'Baden-Württemberg': 'BW',
    'Bayern': 'BY',
    'Berlin': 'BE',
    'Brandenburg': 'BB',
    'Bremen': 'HB',
    'Hamburg': 'HH',
    'Hessen': 'HE',
    'Mecklenburg-Vorpommern': 'MV',
    'Niedersachsen': 'NI',
    'Nordrhein-Westfalen': 'NW',
    'Rheinland-Pfalz': 'RP',
    'Saarland': 'SL',
    'Sachsen': 'SN',
    'Sachsen-Anhalt': 'ST',
    'Schleswig-Holstein': 'SH',
    'Thüringen': 'TH',
}


class Holidays:
    """
    Parameters
    ---------
    state : str
        The state code for the federal state for which the holidays should be calculated. This parameter can either be the name of the state or a short state code, p.Ex. 'Baden-Württemberg' and 'BW' would both be a valid option. Furthermore the option 'Deutschland' / 'DE' gives a list of only the holidays which all the federal states commonly share. The list of all the valid state codes is stored in the dictionary `feiertage.states`:

            - 'Deutschland' / 'DE',
            - 'Baden-Württemberg' / 'BW',
            - 'Bayern' / 'BY',
            - 'Berlin' / 'BE',
            - 'Brandenburg' / 'BB',
            - 'Bremen' / 'HB',
            - 'Hamburg' / 'HH',
            - 'Hessen' / 'HE',
            - 'Mecklenburg-Vorpommern' / 'MV',
            - 'Niedersachsen' / 'NI',
            - 'Nordrhein-Westfalen' / 'NW',
            - 'Rheinland-Pfalz' / 'RP',
            - 'Saarland' / 'SL',
            - 'Sachsen' / 'SN',
            - 'Sachsen-Anhalt' / 'ST',
            - 'Schleswig-Holstein' / 'SH',
            - 'Thüringen' / 'TH',

    year : int, optional
        the year for which the holidays should be calculated
    regional : boolean, default=False
        Optionally enable some regional holidays which are only valid in some communities. These would be the following ones:

            - Fronleichnam in SL and TH
            - Augsburger Hohes Friedensfest in BY
            - Mariä Himmelfahrt in BY

    school_free : boolean, default=False
        Optionally enable some days which are not holidays but there is no school. These would be the following ones:

            - Gründonnerstag in BW
            - Reformationstag in BW
            - Buß- und Bettag in BY
    """

    def __init__(self, state: str, year: int = date.today().year, regional: bool = False, school_free: bool = False):
        # parse the year so it can be stored internally as self.year as an integer
        try:
            self.year = int(year)
            if self.year < 1970:
                self.year = 1970
                print(sys.stderr, "Year was reset to 1970")  # TODO: throw exception instead
        except ValueError:
            print(sys.stderr, f"Fehler bei Parsen von {year} als Datums-Angabe")

        # parse the state name by its key code so it will be stored in self.state
        try:
            if state.upper() in states.values():
                self.state = state.upper()
            elif state in states.keys():
                self.state = states[state]
            else:
                raise ValueError
        except ValueError:
            print(sys.stderr, f"Fehler beim Parsen von {state} als Landes-Angabe")

        self._regional = regional
        self._school_free = school_free

        self.holidays = []
        self._generate_common_holidays()

        # in more then only the national wide should be included than add each of them individually
        if self.state != 'DE':
            self._generate_regional_holidays()

    def _generate_common_holidays(self) -> list:
        # add the common holidays for all states which have fixed dates
        self.holidays.append({'date': date(self.year, 1, 1), 'name': 'Neujahr'})
        self.holidays.append({'date': date(self.year, 5, 1), 'name': 'Tag der Arbeit'})
        self.holidays.append({'date': date(self.year, 10, 3), 'name': 'Tag der deutschen Einheit'})
        self.holidays.append({'date': date(self.year, 12, 25), 'name': '1. Weihnachstag'})
        self.holidays.append({'date': date(self.year, 12, 26), 'name': '2. Weihnachstag'})

        # now add all the holidays which are on another day every year. They are all depending on easter
        self.easter = easter.calc_easter(self.year)
        self.holidays.append({'date': (self.easter - timedelta(days=2)), 'name': 'Karfreitag'})
        self.holidays.append({'date': (self.easter + timedelta(days=1)), 'name': 'Ostermontag'})
        self.holidays.append({'date': (self.easter + timedelta(days=39)), 'name': 'Christi-Himmelfahrt'})
        self.holidays.append({'date': (self.easter + timedelta(days=50)), 'name': 'Pfingstmontag'})

    def _generate_regional_holidays(self) -> None:
        self._add_heilige_drei_koenige()
        self._add_frauentag()
        self._add_gruendonnerstag()
        self._add_easter_sunday()
        self._add_pfingsten()
        self._add_frohnleichnam()
        self._add_augsburg()
        self._add_mariae_himmelfahrt()
        self._add_kindertag()
        self._add_reformation()
        self._add_allerheiligen()
        self._add_buss_und_bettag()

    def _add_heilige_drei_koenige(self) -> None:
        if self.state in ["BW", "BY", "ST"]:
            self.holidays.append({'date': date(self.year, 1, 6), 'name': 'Heilige drei Könige'})

    def _add_frauentag(self) -> None:
        if self.state in ["BE", "MV"]:
            self.holidays.append({'date': date(self.year, 3, 8), 'name': 'Frauentag'})

    def _add_gruendonnerstag(self) -> None:
        if self.state in ["BW"] and self._school_free:
            self.holidays.append({'date': (self.easter - timedelta(days=3)), 'name': 'Gründonnerstag'})

    def _add_easter_sunday(self) -> None:
        if self.state in ["BB", "HE"]:
            self.holidays.append({'date': self.easter, 'name': 'Ostersonntag'})

    def _add_pfingsten(self) -> None:
        if self.state in ["BB", "HE"]:
            self.holidays.append({'date': (self.easter + timedelta(days=49)), 'name': 'Pfingstsonntag'})

    def _add_frohnleichnam(self) -> None:
        if (self.state in ["BW", "BY", "HE", "NW", "RP", "SL"]) or (self.state in ["SN", "TH"] and self._regional):
            self.holidays.append({'date': (self.easter + timedelta(days=60)), 'name': 'Fronleichnam'})

    def _add_augsburg(self) -> None:
        if self.state in ["BY"] and self._regional:
            self.holidays.append({'date': date(self.year, 8, 8), 'name': 'Augsburger Hohes Friedensfest'})

    def _add_mariae_himmelfahrt(self) -> None:
        if (self.state in ["SL"]) or (self.state in ["BY"] and self._regional):
            self.holidays.append({'date': date(self.year, 8, 15), 'name': 'Mariä Himmelfahrt'})

    def _add_kindertag(self) -> None:
        if self.state in ["TH"]:
            self.holidays.append({'date': date(self.year, 9, 20), 'name': 'Weltkindertag'})

    def _add_reformation(self) -> None:
        if (self.state in ["BB", "HB", "HH", "MV", "NI", "SN", "ST", "SH", "TH"]) or (self.state in ["BW"] and self._school_free):
            self.holidays.append({'date': date(self.year, 10, 31), 'name': 'Reformationstag'})

    def _add_allerheiligen(self) -> None:
        if self.state in ["BW", "BY", "NW", "RP", "SL"]:
            self.holidays.append({'date': date(self.year, 11, 1), 'name': 'Allerheiligen'})

    def _add_buss_und_bettag(self) -> None:
        if (self.state in ["SN"]) or (self.state in ["BY"] and self._school_free):
            day = date(self.year, 11, 22)
            while day.weekday() != 2:
                day = day - timedelta(days=1)
            self.holidays.append({'date': day, 'name': 'Buß und Bettag'})

    def get_holidays_list(self) -> list:
        """Get a list of only the dates for all holidays stored in a datetime.date object

        Returns
        -------
            holidays : list of datetime.date objects
                Each entry in this list is a `date` object which points to a holiday
        """
        return [i['date'] for i in self.holidays]
