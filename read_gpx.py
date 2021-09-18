"""
Functions for reading in .gpx (GPS exchange format) route files and manipulating
the data therein
"""

import re
import xml.etree.ElementTree as et
import pandas as pd


def read_gpx(file_name):
    """
    Reads a gpx route file (xml) to DataFrame
    :param file_name: string or Path object
    :return: pandas DataFrame containing route data with columns name, lat, long, elevation
    """
    columns = ['name', 'lat', 'long', 'elevation']
    rows = []

    with open(file_name) as gpx_file:
        xmlstring = gpx_file.read()
    xmlstring = re.sub(' xmlns="[^"]+"', '', xmlstring, count=1)
    gpx_tree = et.ElementTree(et.fromstring(xmlstring))
    gpx_root = gpx_tree.getroot()

    for elem in gpx_root:
        if elem.tag == 'rte':
            for node in elem.findall('rtept'):
                point_name = node.find('name').text
                point_lat = node.attrib.get('lat')
                point_lon = node.attrib.get('lon')
                point_elevation = node.find('ele').text

                rows.append({'name': point_name, 'lat': float(point_lat),
                             'long': float(point_lon), 'elevation': float(point_elevation)})
    gpx_df = pd.DataFrame(rows, columns=columns)
    return gpx_df


def pad_gpx_dataframe(gpx_df):
    """
    Pads the route by interpolating between points
    :param gpx_df: dataframe with columns name, lat, long, elevation
    :return: dataframe with columns name, lat, long, elevation
    """
    gpx_df['newindex'] = gpx_df.index * 2
    gpx_df['newindex'] = gpx_df['newindex'].astype(int)
    max_index = len(gpx_df) * 2
    # gpx_df.set_index('newindex', inplace=True, drop=False)
    rangey = list(range(1, max_index - 2, 2))

    for i in rangey:
        before = gpx_df.loc[gpx_df['newindex'] == i - 1]
        after = gpx_df.loc[gpx_df['newindex'] == i + 1]
        lat = (before.iloc[0]['lat'] + after.iloc[0]['lat']) / 2
        long = (before.iloc[0]['long'] + after.iloc[0]['long']) / 2
        elevation = (before.iloc[0]['elevation'] + after.iloc[0]['elevation']) / 2
        gpx_df = gpx_df.append({'name': '', 'lat': lat, 'long': long,
                                'elevation': elevation, 'newindex': i}, ignore_index=True)
    gpx_df.set_index('newindex', inplace=True)
    gpx_df.sort_index(inplace=True)

    return gpx_df


def get_route_bounds(route_df):
    """
    Gets the maximum and minimum latitude and longitude from a route
    :param route_df: dataframe with columns name, lat, long, elevation
    :return: list
    """
    return [route_df['lat'].max(), route_df['long'].max(),
            route_df['lat'].min(), route_df['long'].min()]
