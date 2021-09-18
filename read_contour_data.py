"""
Functions to take Ordnance Survey contour/altitude data in asc file format,
read it into a pandas dataframe, interpolate between points to reduce data resolution,
convert points from OS grid to Lat/long and insert points into database
"""


import datetime as dt
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlalchemy as db
from sqlalchemy.exc import IntegrityError
from OSGridConverter import grid2latlong


def read_contour_file(filename):
    """
    Reads a contour data file from the OS, in .asc format
    :param filename: string or Path object
    :return: DataFrame matrix with x as the column names, y as the index and altitude as the values
    """
    metadata = get_asc_file_header_information(filename)
    columns = list(range(metadata['high_corner_x'],
                         metadata['high_corner_x'] + metadata['ncols'] * metadata['cellsize'],
                         metadata['cellsize']))
    altitudes_df = pd.read_csv(filename, skiprows=5, sep=' ', names=columns, )
    altitudes_df['cellsize'] = metadata['cellsize']
    altitudes_df['high_corner_y'] = metadata['high_corner_y']
    altitudes_df['y'] = altitudes_df['high_corner_y'] - \
        altitudes_df.index * altitudes_df['cellsize']
    altitudes_df.drop(['cellsize', 'high_corner_y'], axis=1, inplace=True)
    altitudes_df.set_index('y', inplace=True)
    return altitudes_df


def get_asc_file_header_information(filename):
    """
    Gets the metadata from the asc file header
    :param filename: string or Path object
    :return: dict
    """
    with open(filename) as asc_file:
        toplines = asc_file.readlines(200)[:5]
    metadata = dict()
    for line in toplines:
        liney = line.split(' ')
        metadata[liney[0]] = int(liney[1])
    metadata['high_corner_x'] = metadata['xllcorner']
    metadata['high_corner_y'] = \
        metadata['yllcorner'] + (metadata['nrows'] - 1) * metadata['cellsize']
    metadata = {key: value for key, value in metadata.items() if
                key not in ['xllcorner', 'yllcorner']}
    return metadata


def plot_asc_data(asc_df, region_name):
    """
    Plots the altitude data, if you want to
    :param asc_df: DataFrame matrix with x as the column names,
                   y as the index and altitude as the values
    :param region_name: string
    """
    plt.imshow(asc_df)
    plt.title(region_name)
    plt.show()


def pad_altitude_df_columns(altitude_df):
    """
    Pads the columns in the altitude dataframe by interpolating between them
    :param altitude_df: DataFrame matrix with x as the column names,
                        y as the index and altitude as the values
    :return: DataFrame matrix with x as the column names,
             y as the index and altitude as the values
    """
    newcols = []
    oldcols = list(altitude_df)
    for i in range(len(oldcols) - 1):
        newcols.append((oldcols[i] + oldcols[i + 1]) / 2)
    altitude_df[newcols] = np.nan
    altitude_df.sort_index(axis=1, inplace=True)
    return altitude_df


def pad_altitude_df_rows(altitude_df):
    """
    Pads the rows in the altitude dataframe by interpolating between the indices
    :param altitude_df: DataFrame matrix with x as the column names,
                        y as the index and altitude as the values
    :return: DataFrame matrix with x as the column names,
             y as the index and altitude as the values
    """
    new_rows = []
    old_rows = altitude_df.index.tolist()
    for i in range(len(old_rows) - 1):
        new_rows.append((old_rows[i] + old_rows[i + 1]) / 2)
    altitude_df = altitude_df.reindex(old_rows + new_rows)
    altitude_df.sort_index(inplace=True)
    return altitude_df


def get_neighbouring_cell_average(altitude_df, cell_x, cell_y):
    """
    For a given cell in the dataframe, gets the average value of all neighbouring cells
    :param altitude_df: DataFrame matrix with x as the column names,
                        y as the index and altitude as the values
    :param cell_x: x value of the cell
    :param cell_y: y value of the cell
    :return: float
    """
    y_values = altitude_df.index.tolist()
    x_values = list(altitude_df)
    y_step = y_values[1] - y_values[0]
    x_step = x_values[1] - x_values[0]
    neighbour_pairs = [(cell_x - x_step, cell_y + y_step), (cell_x, cell_y + y_step),
                       (cell_x + x_step, cell_y + y_step),
                       (cell_x - x_step, cell_y), (cell_x + x_step, cell_y),
                       (cell_x - x_step, cell_y - y_step), (cell_x, cell_y - y_step),
                       (cell_x + x_step, cell_y - y_step)]
    neighbour_values = [get_cell_value_from_coordinates(altitude_df, x[0], x[1]) for x in
                        neighbour_pairs]
    neighbour_values = [x for x in neighbour_values if not np.isnan(x)]
    return sum(neighbour_values) / len(neighbour_values)


def get_cell_value_from_coordinates(altitude_df, cell_x, cell_y):
    """
    Gets the value of the cell in the altitude dataframe given the x and y coordinates
    :param altitude_df: DataFrame matrix with x as the column names,
                        y as the index and altitude as the values
    :param cell_x: x coordinate of the cell
    :param cell_y: y coordinate of the cell
    :return: int
    """
    try:
        return altitude_df[cell_x][cell_y]
    except KeyError:
        return np.nan


def interpolate_na_values_in_altitude_df(altitude_df):
    """

    :param altitude_df: DataFrame matrix with x as the column names,
                        y as the index and altitude as the values
    :return: DataFrame matrix with x as the column names,
             y as the index and altitude as the values
    """
    for x_coord in list(altitude_df):
        for y_coord in altitude_df.index.tolist():
            if np.isnan(altitude_df[x_coord][y_coord]):
                altitude_df[x_coord][y_coord] = get_neighbouring_cell_average(altitude_df, x_coord,
                                                                              y_coord)
    return altitude_df


def double_pad_altitude_df(altitude_df):
    """
    Pads the altitude dataframe twice, to increase the resolution twofold
    :param altitude_df: DataFrame matrix with x as the column names,
                        y as the index and altitude as the values
    :return: DataFrame matrix with x as the column names,
             y as the index and altitude as the values, but much bigger
    """
    for _ in range(2):
        altitude_df = pad_altitude_df_rows(altitude_df)
        altitude_df = pad_altitude_df_columns(altitude_df)
        altitude_df = interpolate_na_values_in_altitude_df(altitude_df)
    return altitude_df


def create_db_table_df_from_altitude_df(altitude_df, grid_ref_initials):
    """
    For each point in the altitude dataframe, takes the x and y coordinates, works out the
    latitude and longitude and then puts that in a new dataframe
    :param altitude_df: DataFrame matrix with x as the column names,
                        y as the index and altitude as the values
    :param grid_ref_initials: string
    :return: dataframe with columns for latitude, longitude, altitude
    """
    table_df = pd.DataFrame(columns=['latitude', 'longitude', 'altitude'])
    for x_coord in list(altitude_df):
        for y_coord in altitude_df.index.tolist():
            loc_ll = grid2latlong(f'{grid_ref_initials} {int(x_coord)} {int(y_coord)}',
                                  tag="OSGB36")
            loc_list = [loc_ll.latitude, loc_ll.longitude, altitude_df[x_coord][y_coord]]
            table_df.loc[len(table_df)] = loc_list
    return table_df


def create_db_table(connection):
    """
    Creates a database table for the location data, with columns for latitude, longitude,
    altitude, if the table doesn't already exist
    :param connection: sqlite database connection
    :return: sqlalchemy database table object
    """
    metadata = db.MetaData(connection)
    locations = db.Table('locations', metadata,
                         db.Column('latitude', db.Float(), nullable=False, primary_key=True),
                         db.Column('longitude', db.Float(), nullable=False, primary_key=True),
                         db.Column('altitude', db.Float(), nullable=False))
    metadata.create_all()
    return locations


def insert_coords_into_db_table(altitude_df, grid_ref_initials, connection, table):
    """
    Puts the data in the dataframe (converted into latitude, longitude and altitude), into the
    database table
    :param altitude_df: DataFrame matrix with x as the column names,
                        y as the index and altitude as the values
    :param grid_ref_initials: string (two letters denoting the grid reference area)
    :param connection: sqlite database connection
    :param table: sqlalchemy table object
    """
    _ = db.MetaData(connection)  # get sqlalchemy metadata
    values_list = []
    query = db.insert(table)
    for x_coord in list(altitude_df):
        for y_coord in altitude_df.index.tolist():
            x_coordy = str(x_coord).split('.', maxsplit=1)[0]
            y_coordy = str(y_coord).split('.', maxsplit=1)[0]
            loc_ll = grid2latlong(f'{grid_ref_initials} {x_coordy[1:]} {y_coordy[1:]}',
                                  tag='OSGB36')
            values_list.append({'latitude': loc_ll.latitude, 'longitude': loc_ll.longitude,
                                'altitude': altitude_df[x_coord][y_coord]})
    try:
        _ = connection.execute(query, values_list)  # execute query with no return needed
    except IntegrityError:
        print("Entry already in table")


def clear_out_table(connection, table):
    """
    Delete all the records from a table (BE CAREFUL WITH THIS)
    :param connection: sqlite connection
    :param table: sqlalchemy table object
    """
    query = db.delete(table)
    _ = connection.execute(query)


def get_file_list(base_path):
    """
    Gets the list of asc files that have already been read into the database, from a config file,
    and removes them from a separate list of available files in the base path
    :param base_path: path to where the asc files are sitting (string or Path object)
    :return: file list
    """
    files = os.listdir(base_path)
    with open('in_db.csv', 'r') as inserted_files_doc:
        files_done = inserted_files_doc.readlines()
    files = [f for f in files if f + '\n' not in files_done]
    return files


def ingest_asc_file(file):
    """
    Given an asc file, reads it into a dataframe, pads the dataframe to increase data resolution,
    then converts coordinates to latitude and longitude and inserts them into the database
    :param file:
    """
    engine = db.create_engine('sqlite:///altitudes.sqlite')
    with engine.connect() as connection:
        locations = create_db_table(connection)
        print(f'Reading in {file} at {dt.datetime.now()}')
        file_reference = file[0:2]
        altitude_df = read_contour_file(Path(f'data/asc_files/{file}'))
        altitude_df = double_pad_altitude_df(altitude_df)
        print(f'Inserting padded data into db at {dt.datetime.now()}')
        insert_coords_into_db_table(altitude_df, file_reference, connection, locations)
    with open('in_db.csv', 'a+') as inserted_files_doc:
        inserted_files_doc.write(f'{file}\n')
    print(f'Finished with {file} at {dt.datetime.now()}\n**************\n')


def main():
    """
    Gets a list of files and puts the altitude data for each into a database
    :return:
    """
    file_list = get_file_list('data/asc_files/')

    engine = db.create_engine('sqlite:///altitudes.sqlite')
    connection = engine.connect()
    locations = create_db_table(connection)
    for file in file_list:
        print(f'Reading in {file} at {dt.datetime.now()}')
        file_reference = file[0:2]
        altitude_df = read_contour_file(Path(f'data/asc_files/{file}'))
        altitude_df = double_pad_altitude_df(altitude_df)
        print(f'Inserting padded data into db at {dt.datetime.now()}')
        insert_coords_into_db_table(altitude_df, file_reference, connection, locations)
        with open('in_db.csv', 'a+') as inserted_files_doc:
            inserted_files_doc.write(f'{file}\n')
        print(f'Finished with {file} at {dt.datetime.now()}\n**************\n')


if __name__ == '__main__':
    main()
