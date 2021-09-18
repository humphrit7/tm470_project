"""
Functions to gather data for, configure and return the html representation of a folium route map,
with scarier points highlighted, for plugging into a flask application
"""

from pathlib import Path
import folium
from flask import abort
import calculate_scary_points as csp
import read_gpx
import administer_route_database
from calculate_scary_points import timer


@timer
def get_route_with_scariness_from_file(route_file_path):
    """
    Processes a gpx route file to assign scariness score to each waypoint
    :param route_file_path: string
    :return: pandas Dataframe
    """
    route = read_gpx.read_gpx(route_file_path)
    route = read_gpx.pad_gpx_dataframe(route)
    route_bounds = read_gpx.get_route_bounds(route)
    if not csp.check_route_bounds_fit_location_data(route_bounds):
        abort(400)
    altitudes_df = csp.get_complete_route_altitude_df(route_bounds)
    route = csp.calculate_route_scariness(route, altitudes_df)
    administer_route_database.insert_route_into_db_table(
        administer_route_database.prepare_route_for_insertion(route, route_file_path),
        administer_route_database.get_route_db_connection(), 'waypoints'
    )
    return route


@timer
def get_route_with_scariness_from_db(route_name):
    """
    Gets a pre-processed route with scariness rating for each waypoint from database
    :param route_name: string
    :return: pandas Dataframe
    """
    connection = administer_route_database.get_route_db_connection()
    route = administer_route_database.get_route_from_db(connection, route_name)
    return route


def check_route_not_loaded(route_file):
    """
    Checks that a route matching the route file name is not already in the Routes database
    :param route_file: string
    :return: boolean
    """
    loaded_routes = administer_route_database.get_loaded_routes(
        administer_route_database.get_route_db_connection()
    )
    route_file_route_name = Path(route_file).name.replace('.gpx', '')
    for group in loaded_routes:
        if route_file_route_name in group:
            return True
    return False


def translate_fear_level(fear_level):
    """
    Translates the fear level given by the application to a minimum scariness rating at which to
    flag Waypoints
    :param fear_level: int
    :return: int
    """
    if fear_level == 1:
        scariness_threshold = 6
    elif fear_level == 2:
        scariness_threshold = 5
    else:
        scariness_threshold = 4
    return scariness_threshold


@timer
def get_folium_route_map(scariness_level, route_file=None, route_choice=None):
    """
    Creates a folium route map html representation for easy implementation into Flask for a route
    requested in the application
    :param scariness_level: int
    :param route_file: string
    :param route_choice: string
    :return: folium map html representation
    """
    scariness_level = translate_fear_level(scariness_level)
    if route_file and not check_route_not_loaded(route_file):
        route = get_route_with_scariness_from_file(route_file)
    elif route_file:
        route_choice = Path(route_file).name.replace('.gpx', '')
        route = get_route_with_scariness_from_db(route_choice)
    else:
        route = get_route_with_scariness_from_db(route_choice)
    first_point = (route['lat'].mean(), route['long'].mean())
    mappy = folium.Map(location=first_point,
                       tiles='http://tile.mtbmap.cz/mtbmap_tiles/{z}/{x}/{y}.png', zoom_start=13,
                       attr='&copy; <a href="https://www.openstreetmap.org/copyright">'
                            'OpenStreetMap</a> contributors &amp; USGS')
    for _, row in route.iterrows():
        if row['scariness'] > scariness_level:
            colour = 'red'
        else:
            colour = 'blue'
        if colour == 'red':
            folium.Marker(
                [row['lat'], row['long']],
                popup=f"<i>{row['waypoint']}, Latitude: {row['lat']},\n Longitude: {row['long']},\n"
                      f"Altitude: {row['elevation']},\n Scariness: {row['scariness']}/16\n</i>",
                icon=folium.Icon(color=colour),
                tooltip="Click me").add_to(mappy)
        if colour == 'blue':
            folium.CircleMarker(
                [row['lat'], row['long']],
                popup=f"<i>{row['waypoint']}, {row['lat']}, {row['long']}, {row['elevation']}, "
                      f"{row['scariness']}</i>",
                tooltip="Click me", radius=3).add_to(mappy)
    return mappy._repr_html_()
