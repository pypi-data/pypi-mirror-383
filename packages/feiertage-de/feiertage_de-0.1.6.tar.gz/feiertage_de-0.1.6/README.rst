Feiertage
=========

This python package provides an easy access to the list of German national holidays for each federal state.

.. code-block:: python

  >>> import feiertage
  >>> holidays = feiertage.Holidays("BW", year=2023).holidays
  >>> # holidays now contains a list of dictionaries for each holiday with the attribues
  >>> # 'date' -> a datetime.date object with the date of the holiday
  >>> # 'name'-> a string with the name of the holiday
  >>> 
  >>> # let's print this list beautifully formatted
  >>> from pprint import pprint
  >>> pprint(holidays)
  [{'date': datetime.date(2023, 1, 1), 'name': 'Neujahr'},
   {'date': datetime.date(2023, 5, 1), 'name': 'Tag der Arbeit'},
   {'date': datetime.date(2023, 10, 3), 'name': 'Tag der deutschen Einheit'},
   {'date': datetime.date(2023, 12, 25), 'name': '1. Weihnachstag'},
   {'date': datetime.date(2023, 12, 26), 'name': '2. Weihnachstag'},
   {'date': datetime.date(2023, 4, 7), 'name': 'Karfreitag'},
   {'date': datetime.date(2023, 4, 10), 'name': 'Ostermontag'},
   {'date': datetime.date(2023, 5, 18), 'name': 'Christi-Himmelfahrt'},
   {'date': datetime.date(2023, 5, 29), 'name': 'Pfingstmontag'},
   {'date': datetime.date(2023, 1, 6), 'name': 'Heilige drei Könige'},
   {'date': datetime.date(2023, 6, 8), 'name': 'Fronleichnam'},
   {'date': datetime.date(2023, 11, 1), 'name': 'Allerheiligen'}]

Installation
------------

This package can be easily installed with pip:

.. code-block:: bash

  $ pip install feiertage-de

Further information can be seen at the `PyPi project page <https://pypi.org/project/feiertage-de/>`_ or at `Read the Docs <https://feiertage-de.readthedocs.io/en/latest/index.html>`_
