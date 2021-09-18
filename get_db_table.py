"""
Single function to get a set of database table names needed to cover the Locations encompassed by
a given route, whose max long and min long are passed.
"""


def get_tables(max_long, min_long):
    """
    Horrible function to get a list of tables based on the maximum and minimum longitude of a route
    :param max_long: float
    :param min_long: float
    :return: set of strings
    """
    longitudes = list(range(int(min_long * 1000), int(max_long * 1000), 40))
    longitudes = [x / 1000 for x in longitudes] + [min_long, max_long]
    tables = set()
    for longitude in longitudes:
        if -7.05 >= longitude > -7.1:
            tables.add('locations1')
        elif -7.0 >= longitude > -7.05:
            tables.add('locations2')
        elif -6.95 >= longitude > -7.0:
            tables.add('locations3')
        elif -6.9 >= longitude > -6.95:
            tables.add('locations4')
        elif -6.85 >= longitude > -6.9:
            tables.add('locations5')
        elif -6.8 >= longitude > -6.85:
            tables.add('locations6')
        elif -6.75 >= longitude > -6.8:
            tables.add('locations7')
        elif -6.7 >= longitude > -6.75:
            tables.add('locations8')
        elif -6.65 >= longitude > -6.7:
            tables.add('locations9')
        elif -6.6 >= longitude > -6.65:
            tables.add('locations10')
        elif -6.55 >= longitude > -6.6:
            tables.add('locations11')
        elif -6.5 >= longitude > -6.55:
            tables.add('locations12')
        elif -6.45 >= longitude > -6.5:
            tables.add('locations13')
        elif -6.4 >= longitude > -6.45:
            tables.add('locations14')
        elif -6.35 >= longitude > -6.4:
            tables.add('locations15')
        elif -6.3 >= longitude > -6.35:
            tables.add('locations16')
        elif -6.25 >= longitude > -6.3:
            tables.add('locations17')
        elif -6.2 >= longitude > -6.25:
            tables.add('locations18')
        elif -6.15 >= longitude > -6.2:
            tables.add('locations19')
        elif -6.1 >= longitude > -6.15:
            tables.add('locations20')
        elif -6.05 >= longitude > -6.1:
            tables.add('locations21')
        elif -6.0 >= longitude > -6.05:
            tables.add('locations22')
        elif -5.95 >= longitude > -6.0:
            tables.add('locations23')
        elif -5.9 >= longitude > -5.95:
            tables.add('locations24')
        elif -5.85 >= longitude > -5.9:
            tables.add('locations25')
        elif -5.8 >= longitude > -5.85:
            tables.add('locations26')
        elif -5.75 >= longitude > -5.8:
            tables.add('locations27')
        elif -5.7 >= longitude > -5.75:
            tables.add('locations28')
        elif -5.65 >= longitude > -5.7:
            tables.add('locations29')
        elif -5.6 >= longitude > -5.65:
            tables.add('locations30')
        elif -5.55 >= longitude > -5.6:
            tables.add('locations31')
        elif -5.5 >= longitude > -5.55:
            tables.add('locations32')
        elif -5.45 >= longitude > -5.5:
            tables.add('locations33')
        elif -5.4 >= longitude > -5.45:
            tables.add('locations34')
        elif -5.35 >= longitude > -5.4:
            tables.add('locations35')
        elif -5.3 >= longitude > -5.35:
            tables.add('locations36')
        elif -5.25 >= longitude > -5.3:
            tables.add('locations37')
        elif -5.2 >= longitude > -5.25:
            tables.add('locations38')
        elif -5.15 >= longitude > -5.2:
            tables.add('locations39')
        elif -5.1 >= longitude > -5.15:
            tables.add('locations40')
        elif -5.05 >= longitude > -5.1:
            tables.add('locations41')
        elif -5.0 >= longitude > -5.05:
            tables.add('locations42')
        elif -4.95 >= longitude > -5.0:
            tables.add('locations43')
        elif -4.9 >= longitude > -4.95:
            tables.add('locations44')
        elif -4.85 >= longitude > -4.9:
            tables.add('locations45')
        elif -4.8 >= longitude > -4.85:
            tables.add('locations46')
        elif -4.75 >= longitude > -4.8:
            tables.add('locations47')
        elif -4.7 >= longitude > -4.75:
            tables.add('locations48')
        elif -4.65 >= longitude > -4.7:
            tables.add('locations49')
        elif -4.6 >= longitude > -4.65:
            tables.add('locations50')
        elif -4.55 >= longitude > -4.6:
            tables.add('locations51')
        elif -4.5 >= longitude > -4.55:
            tables.add('locations52')
        elif -4.45 >= longitude > -4.5:
            tables.add('locations53')
        elif -4.4 >= longitude > -4.45:
            tables.add('locations54')
        elif -4.35 >= longitude > -4.4:
            tables.add('locations55')
        elif -4.3 >= longitude > -4.35:
            tables.add('locations56')
        elif -4.25 >= longitude > -4.3:
            tables.add('locations57')
        elif -4.2 >= longitude > -4.25:
            tables.add('locations58')
        elif -4.15 >= longitude > -4.2:
            tables.add('locations59')
        elif -4.1 >= longitude > -4.15:
            tables.add('locations60')
        elif -4.05 >= longitude > -4.1:
            tables.add('locations61')
        elif -4.0 >= longitude > -4.05:
            tables.add('locations62')
        elif -3.95 >= longitude > -4.0:
            tables.add('locations63')
        elif -3.9 >= longitude > -3.95:
            tables.add('locations64')
        elif -3.85 >= longitude > -3.9:
            tables.add('locations65')
        elif -3.8 >= longitude > -3.85:
            tables.add('locations66')
        elif -3.75 >= longitude > -3.8:
            tables.add('locations67')
        elif -3.7 >= longitude > -3.75:
            tables.add('locations68')
        elif -3.65 >= longitude > -3.7:
            tables.add('locations69')
        elif -3.6 >= longitude > -3.65:
            tables.add('locations70')
        elif -3.55 >= longitude > -3.6:
            tables.add('locations71')
        elif -3.5 >= longitude > -3.55:
            tables.add('locations72')
        elif -3.45 >= longitude > -3.5:
            tables.add('locations73')
        elif -3.4 >= longitude > -3.45:
            tables.add('locations74')
        elif -3.35 >= longitude > -3.4:
            tables.add('locations75')
        elif -3.3 >= longitude > -3.35:
            tables.add('locations76')
        elif -3.25 >= longitude > -3.3:
            tables.add('locations77')
        elif -3.2 >= longitude > -3.25:
            tables.add('locations78')
        elif -3.15 >= longitude > -3.2:
            tables.add('locations79')
        elif -3.1 >= longitude > -3.15:
            tables.add('locations80')
        elif -3.05 >= longitude > -3.1:
            tables.add('locations81')
        elif -3.0 >= longitude > -3.05:
            tables.add('locations82')
        elif -2.95 >= longitude > -3.0:
            tables.add('locations83')
        else:
            pass
    return tables
