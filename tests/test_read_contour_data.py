import unittest
import read_contour_data as contour
import pandas as pd
from pathlib import Path
import numpy as np
import datetime as dt
import sqlalchemy as db

PADDED_ALT_DF = pd.read_pickle('padded_alt_test_df.pkl')


class MyTestCase(unittest.TestCase):
    def test_read_contour_file(self):
        filename = Path('../data/SR89.asc')
        result = contour.read_contour_file(filename)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(list(result)[-1], 189950)
        self.assertEqual(list(result)[0], 180000)
        self.assertEqual(result.index.min(), 190000)
        self.assertEqual(result.index.max(), 199950)

    def test_read_contour_file_nevis(self):
        filename = Path('../data/asc_files/NN17.asc')
        result = contour.read_contour_file(filename)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(list(result)[-1], 219950)
        self.assertEqual(list(result)[0], 210000)
        self.assertEqual(result.index.min(), 770000)
        self.assertEqual(result.index.max(), 779950)
        self.assertEqual(result[216650][771250], 1345.1)
        self.assertEqual(result[210000][779950], 194.5)
        self.assertEqual(result[219950][770000], 797.4)

    def test_get_asc_header_information(self):
        filename = Path('../data/SR89.asc')
        result = contour.get_asc_file_header_information(filename)
        expected = {'ncols': 200, 'nrows': 200, 'high_corner_x': 180000,
                    'high_corner_y': 199950, 'cellsize': 50}
        self.assertEqual(result, expected)

    def test_plot_asc_data(self):
        filename = Path('../data/asc_files/NN99.asc')
        result = contour.read_contour_file(filename)
        maxi = 0
        for col in list(result):
            if result[col].max() > maxi:
                maxi = result[col].max()
        contour.plot_asc_data(result, 'NN99')
        self.assertTrue(1)

    def test_pad_altitude_df_columns(self):
        filename = Path('../data/asc_files/NN99.asc')
        altitude_df = contour.read_contour_file(filename)
        new_altitude_df = contour.pad_altitude_df_columns(altitude_df.copy())
        self.assertEqual(len(list(new_altitude_df)), len(list(altitude_df))*2-1)

    def test_pad_altitude_df_rows(self):
        filename = Path('../data/asc_files/NN99.asc')
        altitude_df = contour.read_contour_file(filename)
        new_altitude_df = contour.pad_altitude_df_rows(altitude_df.copy())
        self.assertEqual(len(altitude_df)*2-1, len(new_altitude_df))

    def test_pad_altitude_df_rows_and_cols(self):
        filename = Path('../data/asc_files/NN17.asc')
        altitude_df = contour.read_contour_file(filename)
        new_altitude_df = contour.pad_altitude_df_columns(contour.pad_altitude_df_rows(altitude_df.copy()))
        self.assertEqual(len(list(new_altitude_df)), len(list(altitude_df)) * 2 - 1)
        self.assertEqual(len(altitude_df) * 2 - 1, len(new_altitude_df))

    def test_interpolate_na_values_in_altitude_df(self):
        filename = Path('../data/asc_files/NN99.asc')
        altitude_df = contour.read_contour_file(filename)
        new_altitude_df = contour.pad_altitude_df_columns(contour.pad_altitude_df_rows(altitude_df.copy()))
        interpolated_alt_df = contour.interpolate_na_values_in_altitude_df(new_altitude_df.copy())
        self.assertFalse(interpolated_alt_df.isnull().values.any())
        self.assertEqual(interpolated_alt_df[290000][790025.0], (679.70000+686.20000)/2)

    def test_interpolate_na_values_in_altitude_df_nevis(self):
        filename = Path('../data/asc_files/NN17.asc')
        altitude_df = contour.read_contour_file(filename)
        new_altitude_df = contour.pad_altitude_df_columns(contour.pad_altitude_df_rows(altitude_df.copy()))
        interpolated_alt_df = contour.interpolate_na_values_in_altitude_df(new_altitude_df.copy())
        self.assertFalse(interpolated_alt_df.isnull().values.any())

    def test_get_neighbouring_cell_average(self):
        filename = Path('../data/asc_files/NN99.asc')
        altitude_df = contour.read_contour_file(filename)
        new_altitude_df = contour.pad_altitude_df_columns(contour.pad_altitude_df_rows(altitude_df.copy()))
        res1 = contour.get_neighbouring_cell_average(new_altitude_df, 290000, 790025.0)
        self.assertEqual(res1, (679.70000+686.20000)/2)

    def test_get_cell_value_from_coordinates(self):
        filename = Path('../data/asc_files/NN99.asc')
        altitude_df = contour.read_contour_file(filename)
        cell_value = contour.get_cell_value_from_coordinates(altitude_df, 290000, 799950)
        self.assertEqual(cell_value, 978.60000)
        cell_value_nan = contour.get_cell_value_from_coordinates(altitude_df, 290000, 800000)
        self.assertTrue(np.isnan(cell_value_nan))

    def test_pad_altitude_df(self):
        filename = Path('../data/asc_files/NN99.asc')
        altitude_df = contour.read_contour_file(filename)
        padded_altitude_df = contour.double_pad_altitude_df(altitude_df.copy())
        self.assertFalse(padded_altitude_df.isnull().values.any())
        self.assertEqual(12.5, list(padded_altitude_df)[1] - list(padded_altitude_df)[0])
        self.assertEqual(12.5, padded_altitude_df.index.tolist()[1] - padded_altitude_df.index.tolist()[0])
        contour.plot_asc_data(padded_altitude_df, 'NN99-padded')
        # padded_altitude_df.to_pickle('padded_alt_test_df.pkl')

    def test_create_db_table_df_from_altitude_df(self):
        filename = Path('../data/asc_files/NN17.asc')
        altitude_df = contour.read_contour_file(filename)
        table_df = contour.create_db_table_df_from_altitude_df(altitude_df, 'NN')
        self.assertIsInstance(table_df, pd.DataFrame)
        self.assertEqual(['latitude', 'longitude', 'altitude', ], list(table_df))

    def test_create_db_table_df_from_altitude_df_nh(self):
        filename = Path('../data/asc_files/NH01.asc')
        altitude_df = contour.read_contour_file(filename)
        table_df = contour.create_db_table_df_from_altitude_df(altitude_df, 'NH')
        self.assertIsInstance(table_df, pd.DataFrame)
        self.assertEqual(['latitude', 'longitude', 'altitude', ], list(table_df))

    # def test_insert_coords_into_db_table(self):
    #     """
    #     Used for initial testing but dangerous for regression testing - commented out
    #     :return:
    #     """
    #     print(dt.datetime.now())
    #     engine = db.create_engine('sqlite:///altitudes.sqlite')
    #     connection = engine.connect()
    #     locations = contour.create_db_table(connection)
    #     filename = Path('data/asc_files/NN17.asc')
    #     altitude_df = contour.read_contour_file(filename)
    #     print(dt.datetime.now())
    #     padded_altitude_df = contour.double_pad_altitude_df(altitude_df.copy())
    #     print(dt.datetime.now())
    #     contour.insert_coords_into_db_table(padded_altitude_df, 'NN', connection, locations)
    #     print(dt.datetime.now())
    #     max_query = db.select(db.func.max(locations.columns.altitude))
    #     ResultProxy = connection.execute(max_query)
    #     result = ResultProxy.fetchone().values()
    #     self.assertEqual(altitude_df.to_numpy().max(), result[0])

    # def test_clear_out_table(self):
    #     """
    #     Used to delete contents of Locations table - dangerous!
    #     Commented out for suite testing
    #     :return:
    #     """
    #     engine = db.create_engine('sqlite:///altitudes.sqlite')
    #     connection = engine.connect()
    #     locations = contour.create_db_table(connection)
    #     contour.clear_out_table(connection, locations)

    def test_get_file_list(self):
        expected = ['NA00.asc', 'NA10.asc', 'NA64.asc', 'NA74.asc', 'NA81.asc']
        file_list = contour.get_file_list('../data/test_asc_files')
        self.assertEqual(expected, file_list)



if __name__ == '__main__':
    unittest.main()
