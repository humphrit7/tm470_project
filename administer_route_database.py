"""
Functions to read and write to Routes database for mountain fear finder application
"""

import datetime as dt
from pathlib import Path
import pandas as pd
import sqlalchemy as db
from sqlalchemy.exc import IntegrityError


def create_db_table(connection):
    """
    Creates a database table for the route data, with columns for route name, waypoint, latitude,
    longitude, elevation, if the table doesn't already exist
    :param connection: sqlite database connection
    :return: sqlalchemy database table object
    """
    metadata = db.MetaData(connection)
    waypoints = db.Table('waypoints', metadata,
                         db.Column('route', db.String(), nullable=False, primary_key=True),
                         db.Column('waypoint', db.String(), nullable=False, primary_key=True),
                         db.Column('lat', db.Float(), nullable=False),
                         db.Column('long', db.Float(), nullable=False),
                         db.Column('elevation', db.Float(), nullable=False),
                         db.Column('scariness', db.Integer(), nullable=False),
                         db.Column('created_dt', db.DateTime(), nullable=False))
    metadata.create_all()
    return waypoints


def insert_route_into_db_table(route_df, connection, table):
    """
    Inserts a route into a database table
    :param route_df: pd.Dataframe
    :param connection: SQLalchemy connection
    :param table: string
    """
    try:
        route_df.to_sql(name=table, con=connection, index=False, if_exists='append')
    except IntegrityError:
        pass


def prepare_route_for_insertion(route_df, filename):
    """
    Renames route waypoints, adds route name and created_dt to dataframe
    :param route_df: pandas Dataframe
    :param filename: string
    :return: pandas Dataframe
    """
    route_df.reset_index(inplace=True, drop=True)
    route_df.reset_index(inplace=True)
    route_df.rename({'index': 'waypoint'}, axis=1, inplace=True)
    route_df['waypoint'] = route_df['waypoint'].apply(lambda x: f'WP{x+1:04}')
    route_df['route'] = Path(filename).name.replace('.gpx', '')
    route_df.drop(['name'], axis=1, inplace=True)
    route_df['created_dt'] = dt.datetime.now()
    return route_df


def get_loaded_routes(connection):
    """
    Gets a list of all the route names that have been loaded into the databases
    :param connection: SQLalchemy connection
    :return: list of strings
    """
    query = "select distinct route from waypoints"
    routes = list(pd.read_sql(query, connection)['route'])
    return routes if routes else ['None']


def get_route_db_connection():
    """
    Gets a SQLalchemy connection to the Routes (waypoints.sqlite) database
    :return: SQLalchemy Connection object
    """
    engine = db.create_engine('sqlite:///waypoints.sqlite')
    connection = engine.connect()
    return connection


def get_route_from_db(connection, route):
    """
    Gets all the Waypoints for a selected Route from the database
    :param connection: SQLalchemy connection
    :param route: string
    :return: pandas Dataframe
    """
    query = (f'select * '
             f'from waypoints '
             f'where route="{route}"')
    return pd.read_sql(query, connection)
