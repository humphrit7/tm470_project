"""
Functions to process a dataframe containing Route data (latitude, longitude, elevation and name)
to work out if points in route are scary, and assign scariness rating/16
"""

import sqlite3
import datetime as dt
from statistics import mean
from functools import wraps
from time import perf_counter
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.spatial.distance import cdist
import swifter   # this import is used implicitly later
from get_db_table import get_tables


def timer(func):
    """
    Decorator function to time the execution of a function
    :param func: function
    :return: function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        elapsed = end - start
        print(f'{func.__name__} took {elapsed} seconds')
        return result
    return wrapper


@timer
def get_complete_route_altitude_df(route_bounds):
    """
    Gets all the data from the location database within the max and min latitude and longitude
    given in route_bounds
    :param route_bounds: list, [max_lat, max_long, min_lat, min_long]
    :return: dataframe with columns for latitude, longitude, altitude
    """
    tables = get_tables(max_long=route_bounds[1], min_long=route_bounds[3])
    altitudes_df = pd.DataFrame()
    for table in tables:
        altitudes_df = altitudes_df.append(get_route_altitude_df(route_bounds, table))
    altitudes_df.reset_index(inplace=True, drop=True)
    return altitudes_df


@timer
def get_route_altitude_df(route_bounds, table):
    """
    Gets all the data from the specified location table within the max and min latitude and
    longitude given in route_bounds
    :param route_bounds: list, [max_lat, max_long, min_lat, min_long]
    :param table: string
    :return: dataframe with columns for latitude, longitude, altitude
    """
    query = (f'select * '
             f'from {table} '
             f'where latitude > {route_bounds[2] - 0.03} and '
             f'latitude < {route_bounds[0] + 0.03} and '
             f'longitude > {route_bounds[3] - 0.03} and '
             f'longitude < {route_bounds[1] + 0.03}')
    con = sqlite3.connect('altitudes.sqlite')
    altitudes_df = pd.DataFrame()
    start = dt.datetime.now()
    for small_altitudes_df in pd.read_sql_query(query, con, chunksize=1000):
        altitudes_df = altitudes_df.append(small_altitudes_df)
    con.close()
    print(dt.datetime.now() - start)
    return altitudes_df


def get_neighbouring_points(point, route_altitude_df, no_points):
    """
    Gets the closest points in a Dataframe of locations to the point passed
    :param point: point to find neighbours of, pd.Series
    :param route_altitude_df: pandas Dataframe
    :param no_points: int (number of neighbours required)
    :return: pandas Dataframe
    """
    point_arr = np.reshape(point[['lat', 'long']].to_numpy(), (-1, 2))
    route_altitude_arr = route_altitude_df[['latitude', 'longitude']].to_numpy()
    distances = cdist(route_altitude_arr, point_arr)
    distances_df = pd.DataFrame(distances)
    distances_df.sort_values(by=[0], inplace=True)
    indices = list(distances_df.iloc[list(range(no_points))].index)
    return route_altitude_df.iloc[indices]


def plot_route_on_altitudes_df(route_df, altitudes_df, region_name):
    """
    Plots the route on the background of the altitudes, for sanity checks
    :param route_df: pandas dataframe from gpx file
    :param altitudes_df: pandas dataframe containing background Locations
    :param region_name: string
    """
    plt.scatter(altitudes_df['longitude'], altitudes_df['latitude'],
                c=altitudes_df['altitude'])
    plt.scatter(route_df['long'], route_df['lat'], marker=11)
    plt.title(region_name)
    plt.show()


def calculate_scariness(point, route_altitude_df):
    """
    For a given point, calculates how scary that point is out of 16
    :param point: pandas Series
    :param route_altitude_df: Pandas Dataframe
    :return: int, max 16
    """
    neighbours = get_neighbouring_points(point, route_altitude_df, 64)
    midpoint = neighbours['altitude'].head(4).mean()
    sectors = get_sectors(point, neighbours)
    scariness = 0
    for listy in [x for x in sectors.values() if len(x) > 0]:
        if abs(mean(listy) - midpoint) > 10:
            scariness += 1
    return scariness


def get_sectors(point, neighbours):
    """
    For each neighbour in the neighbours dataframe, assigns it to a sector around the main point,
    each sector comprising 45 degrees
    :param point: pandas Series
    :param neighbours: pandas Dataframe
    :return: list of lists
    """
    sectors = {'ene': [], 'nne': [], 'nnw': [], 'wnw': [],
               'wsw': [], 'ssw': [], 'sse': [], 'ese': []}
    for _, row in neighbours.iterrows():
        lat2 = row['latitude']
        lat1 = point['lat']
        long2 = row['longitude']
        long1 = point['long']
        angle = get_angle_between_two_points(long1, lat1, long2, lat2)
        if angle < 45:
            sectors['ene'].append(row['altitude'])
        elif angle < 90:
            sectors['nne'].append(row['altitude'])
        elif angle < 135:
            sectors['nnw'].append(row['altitude'])
        elif angle < 180:
            sectors['wnw'].append(row['altitude'])
        elif angle < 225:
            sectors['wsw'].append(row['altitude'])
        elif angle < 270:
            sectors['ssw'].append(row['altitude'])
        elif angle < 315:
            sectors['sse'].append(row['altitude'])
        elif angle < 360:
            sectors['ese'].append(row['altitude'])
    return sectors


def get_angle_between_two_points(point1_x, point1_y, point2_x, point2_y):
    """
    Gets the angle of orientation between point 1 (x1, y1) and point 2 (x2, y2)
    :param point1_x: float
    :param point1_y: float
    :param point2_x: float
    :param point2_y: float
    :return: float
    """
    vector1 = [point2_x-point1_x, point2_y-point1_y]
    vector2 = [1, 0]
    unit_vector1 = vector1 / np.linalg.norm(vector1)
    unit_vector2 = vector2 / np.linalg.norm(vector2)
    dot_product = np.dot(unit_vector1, unit_vector2)
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0)) / np.pi * 180
    if point2_y < point1_y:
        angle = 360 - angle
    return angle


@timer
def calculate_route_scariness(route, altitude_df):
    """
    For each point in a route, calculate the scariness of that point /16
    :param route: pandas Dataframe from .gpx file
    :param altitude_df: pandas Dataframe containing Location data (latitude, longitude, altitude)
                        surrounding the Route
    :return: pandas Dataframe
    """
    normalised_route = normalise_points(route.copy(), altitude_df)
    route['scariness'] = normalised_route[['lat', 'long']].swifter.apply(
            calculate_scariness, axis=1, route_altitude_df=altitude_df)
    return route


@timer
def normalise_points(route, altitude_df):
    """
    Ensures location of highest point of route is matched to point of same altitude in altitude
    dataframe, and then subtracts difference from each point in Route
    :param route: pandas dataframe from .gpx file
    :param altitude_df: pandas dataframe with latitude, longitude, altitude for all surrounding
    locations
    :return: pandas dataframe
    """
    max_route_height = route['elevation'].max()
    max_route_point = route.loc[route['elevation'] == max_route_height]
    equivalent_heights_from_alt = altitude_df.loc[
        (altitude_df['altitude'] >= (max_route_height - 20))
        & (altitude_df['altitude'] <= (max_route_height + 20))]
    equivalent_alt_point = get_neighbouring_points(
        max_route_point, equivalent_heights_from_alt, 1
    )
    lat_diff = equivalent_alt_point.iloc[0]['latitude'] - max_route_point['lat']
    lon_diff = equivalent_alt_point.iloc[0]['longitude'] - max_route_point['long']
    route['lat'] = route['lat'] + lat_diff.iloc[0]
    route['long'] = route['long'] + lon_diff.iloc[0]
    return route


def get_altitudes_max_and_min_lat_and_long():
    """
    Gets the maximum and minimum latitude and longitude from the big altitudes table
    For setting application config only
    :return: pandas dataframe
    """
    con = sqlite3.connect('altitudes.sqlite')
    query = "select max(latitude) maxlat, min(latitude) minlat, " \
            "max(longitude) maxlong, min(longitude) minlong " \
            "from locations"
    result = pd.read_sql_query(query, con)
    con.close()
    return result


def check_route_bounds_fit_location_data(route_bounds):
    """
    Checks that the bounds of a given route are within the Location database limits
    :param route_bounds: list
    :return: boolean
    """
    database_maxima_minima = pd.read_pickle("tests/locations_extremes.pkl").iloc[0]
    if route_bounds[0] < database_maxima_minima['maxlat'] \
        and route_bounds[1] < database_maxima_minima['maxlong'] \
        and route_bounds[2] > database_maxima_minima['minlat'] \
        and route_bounds[3] > database_maxima_minima['minlong']:
        return True
    return False
