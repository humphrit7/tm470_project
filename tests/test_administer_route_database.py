import unittest
import administer_route_database as ard
import sqlalchemy as db
from collections import Counter
import get_folium_route_map
import pandas as pd


class MyTestCase(unittest.TestCase):
    def test_create_db_table(self):
        engine = db.create_engine('sqlite:///waypoints.sqlite')
        connection = engine.connect()
        ard.create_db_table(connection)
        inspector = db.inspect(engine)
        wee = [x for x in inspector.get_table_names()]
        self.assertTrue('waypoints' in wee)
        columns = [x['name'] for x in inspector.get_columns('waypoints')]
        self.assertEqual(Counter(columns), Counter(['route', 'waypoint', 'lat', 'long',
                                                    'elevation', 'scariness', 'created_dt']))

    def test_prepare_route_for_insertion(self):
        route_df = pd.read_pickle('cdm_route_scariness.pkl')
        result = ard.prepare_route_for_insertion(route_df, '../data/carnmordeargarete.gpx')
        self.assertEqual(result['route'].iloc[0], 'carnmordeargarete')
        self.assertEqual(result['waypoint'].iloc[0], 'WP0001')
        self.assertEqual(Counter(list(result)),
                         Counter(['route', 'waypoint', 'lat', 'long',
                                  'elevation', 'scariness', 'created_dt']))

    def test_insert_route_into_db_table(self):
        route_df = ard.prepare_route_for_insertion(pd.read_pickle('cdm_route_scariness.pkl'),
                                                   '../data/carnmordeargarete.gpx')
        engine = db.create_engine('sqlite:///waypoints.sqlite')
        connection = engine.connect()
        ard.insert_route_into_db_table(route_df, engine, 'waypoints')
        query = 'select * from waypoints where route = "carnmordeargarete"'
        table_df = pd.read_sql(query, con=connection)
        route_df.sort_index(axis=1, inplace=True)
        table_df.sort_index(axis=1, inplace=True)
        for col in list(route_df.drop(['created_dt'], axis=1)):
            self.assertTrue(route_df[col].equals(table_df[col]), msg=f'{col} is fucked')

    def test_get_loaded_routes(self):
        engine = db.create_engine('sqlite:///waypoints.sqlite')
        connection = engine.connect()
        result = ard.get_loaded_routes(connection)
        self.assertIsInstance(result, list)
        self.assertEqual(Counter(set(result)), Counter(result))

    def test_get_route_from_db(self):
        """
        Will fail if carnmordeargarete Route not in database
        :return:
        """
        engine = db.create_engine('sqlite:///waypoints.sqlite')
        connection = engine.connect()
        route_df = ard.prepare_route_for_insertion(pd.read_pickle('cdm_route_scariness.pkl'),
                                                   '../data/carnmordeargarete.gpx')
        table_df = ard.get_route_from_db(connection, 'carnmordeargarete')
        for col in list(route_df.drop(['created_dt'], axis=1)):
            self.assertTrue(route_df[col].equals(table_df[col]), msg=f'{col} is fucked')
        self.assertEqual(Counter(list(table_df)), Counter(['route', 'waypoint', 'lat', 'long',
                                                    'elevation', 'scariness', 'created_dt']))

    def test_get_loaded_routes_with_get_db_connection(self):
        result = ard.get_loaded_routes(ard.get_route_db_connection())
        self.assertIsInstance(result, list)
        self.assertEqual(Counter(set(result)), Counter(result))


if __name__ == '__main__':
    unittest.main()
