import unittest
import pandas as pd
import calculate_scary_points as csp
import read_gpx
import datetime as dt


class TestCalculateScaryPoints(unittest.TestCase):
    def test_get_complete_route_altitude_df(self):
        route = read_gpx.read_gpx('../data/bennevis.gpx')
        route_bounds = read_gpx.get_route_bounds(route)
        result = csp.get_complete_route_altitude_df(route_bounds)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreaterEqual(result['longitude'].max(), route_bounds[1])

    def test_get_route_altitude_df(self):
        route = read_gpx.read_gpx('../data/bennevis.gpx')
        route_bounds = read_gpx.get_route_bounds(route)
        result = csp.get_route_altitude_df(route_bounds, 'locations42')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreaterEqual(result['longitude'].max(), route_bounds[1])

    def test_get_neighbouring_points_cmd(self):
        route = read_gpx.read_gpx('../data/carnmordeargarete.gpx')
        route_bounds = read_gpx.get_route_bounds(route)
        start = dt.datetime.now()
        route_altitudes_df = csp.get_complete_route_altitude_df(route_bounds)
        normalised_route = csp.normalise_points(route, route_altitudes_df)
        print(f"Time to get route_altitudes_df: {dt.datetime.now() - start}")
        point = normalised_route.iloc[24]
        result = csp.get_neighbouring_points(point, route_altitudes_df, 16)
        self.assertEqual(len(result), 16)
        # csp.plot_route_on_altitudes_df(point, result, 'poo') # Uncomment to view plot

    def test_plot_route_on_altitudes_df(self):
        """
        Sanity check to ensure that the route and the altitudes_df are matching up
        Comment out for unit test suite run
        """
        route = read_gpx.read_gpx('../data/ben-more.gpx')
        route_bounds = read_gpx.get_route_bounds(route)
        route_altitude_df = csp.get_route_altitude_df(route_bounds, 'locations')
        csp.plot_route_on_altitudes_df(route, route_altitude_df, "Ben More")

    def test_calculate_scariness(self):
        cmd_altitudes = pd.read_pickle('cmd_altitudes.pkl')
        route = read_gpx.read_gpx('../data/carnmordeargarete.gpx')
        normalised_route = csp.normalise_points(route, cmd_altitudes)
        point = normalised_route.iloc[87]
        scariness = csp.calculate_scariness(point, cmd_altitudes)
        self.assertEqual(scariness, 6)
        point = normalised_route.iloc[2]
        scariness = csp.calculate_scariness(point, cmd_altitudes)
        self.assertEqual(scariness, 3)
        point = normalised_route.iloc[79]
        scariness = csp.calculate_scariness(point, cmd_altitudes)
        self.assertEqual(scariness, 6)

    def test_get_sectors(self):
        cmd_altitudes = pd.read_pickle('cmd_altitudes.pkl')
        route = read_gpx.read_gpx('../data/carnmordeargarete.gpx')
        point = route.loc[route['name'] == 'CMD 099'][['lat', 'long']].squeeze()
        neighbours = csp.get_neighbouring_points(point, cmd_altitudes, 32)
        # csp.plot_route_on_altitudes_df(point, neighbours, 'wee') # Uncomment for plot
        result = csp.get_sectors(point, neighbours)
        self.assertIsInstance(result, dict)

    def test_get_angle_between_two_points(self):
        result1 = csp.get_angle_between_two_points(1, 1, 2, 2)
        self.assertAlmostEqual(result1, 45)
        result2 = csp.get_angle_between_two_points(1, 1, -2, 4)
        self.assertAlmostEqual(result2, 135)
        result3 = csp.get_angle_between_two_points(0, 0, -1, -1)
        self.assertAlmostEqual(result3, 225)
        result4 = csp.get_angle_between_two_points(0, 0, 1, -1)
        self.assertAlmostEqual(result4, 315)

    def test_calculate_route_scariness(self):
        route = read_gpx.read_gpx('../data/carnmordeargarete.gpx')
        route = read_gpx.pad_gpx_dataframe(route)
        route_bounds = read_gpx.get_route_bounds(route)
        cmd_altitudes = csp.get_complete_route_altitude_df(route_bounds)
        route = csp.calculate_route_scariness(route, cmd_altitudes)
        self.assertLessEqual(route['scariness'].max(), 16)
        self.assertEqual(route['scariness'].min(), 0)
        # poo = route.loc[route['scariness'] > 6] # Uncomment for plot
        # csp.plot_route_on_altitudes_df(poo, cmd_altitudes, 'cmd') # Uncomment for plot
        wee = route.loc[route['name'] == 'CMD 087'].iloc[0]
        self.assertEqual(wee['scariness'], 6)

    def test_calculate_route_scariness_south_glen_shiel(self):
        route = read_gpx.read_gpx('../data/Glenshielridge.gpx')
        route = read_gpx.pad_gpx_dataframe(route)
        route_bounds = read_gpx.get_route_bounds(route)
        altitudes_df = csp.get_complete_route_altitude_df(route_bounds)
        altitudes_df.to_pickle('sgs_ridge_altitudes.pkl')
        start = dt.datetime.now()
        route = csp.calculate_route_scariness(route, altitudes_df)
        print(dt.datetime.now() - start)
        self.assertLessEqual(route['scariness'].max(), 16)
        self.assertEqual(route['scariness'].min(), 0)
        # poo = route.loc[route['scariness'] > 4] # Uncomment for plot
        # csp.plot_route_on_altitudes_df(poo, altitudes_df, 'poo') # Uncomment for plot

    def test_calculate_route_scariness_macdui(self):
        route = read_gpx.read_gpx('../data/beinn-heasgarnich.gpx')
        route = read_gpx.pad_gpx_dataframe(route)
        route_bounds = read_gpx.get_route_bounds(route)
        altitudes_df = csp.get_complete_route_altitude_df(route_bounds)
        start = dt.datetime.now()
        route = csp.calculate_route_scariness(route, altitudes_df)
        print(dt.datetime.now() - start)
        self.assertLessEqual(route['scariness'].max(), 16)
        self.assertEqual(route['scariness'].min(), 0)
        # poo = route.loc[route['scariness'] > 5] # Uncomment for plot
        # csp.plot_route_on_altitudes_df(poo, altitudes_df, 'poo') # Uncomment for plot

    def test_normalise_points(self):
        cmd_altitudes = pd.read_pickle('cmd_altitudes.pkl')
        route = read_gpx.read_gpx('../data/carnmordeargarete.gpx')
        normalised_route = csp.normalise_points(route, cmd_altitudes)
        self.assertEqual(list(route), list(normalised_route))
        self.assertEqual(route.iloc[0]['lat']-normalised_route.iloc[0]['lat'],
                         route.iloc[3]['lat']-normalised_route.iloc[3]['lat'])
        self.assertTrue(route.index.equals(normalised_route.index))
        # csp.plot_route_on_altitudes_df(normalised_route, cmd_altitudes, 'poo') # Uncomment 4 plot

    def test_get_altitudes_max_and_min_lat_and_long(self):
        result = csp.get_altitudes_max_and_min_lat_and_long()
        self.assertIsInstance(result, pd.DataFrame)
        result.to_pickle("locations_extremes.pkl")

    def test_check_route_bounds_fit_location_data(self):
        rb1 = [57.9, -3, 56.8, -3.4]
        self.assertTrue(csp.check_route_bounds_fit_location_data(rb1))
        rb2 = [57.9, -2, 56.8, -3.4]
        self.assertFalse(csp.check_route_bounds_fit_location_data(rb2))
        rb3 = [58, -3, 56.8, -3.4]
        self.assertFalse(csp.check_route_bounds_fit_location_data(rb3))
        rb4 = [57, -3, 56, -3.1]
        self.assertFalse(csp.check_route_bounds_fit_location_data(rb4))
        rb5 = [1, 1, 1, 1]
        self.assertFalse(csp.check_route_bounds_fit_location_data(rb5))


if __name__ == '__main__':
    unittest.main()
