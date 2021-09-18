import unittest
import pandas as pd
import get_folium_route_map as gfrm
from collections import Counter
import re


class MyTestCase(unittest.TestCase):
    def test_get_route_with_scariness_from_db(self):
        result = gfrm.get_route_with_scariness_from_db('bennevis')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.isnull().values.any())

    def test_get_folium_map_no_file(self):
        result = gfrm.get_folium_route_map(
            2, route_file=None, route_choice='carnmordeargarete')
        compare = gfrm.get_route_with_scariness_from_db('carnmordeargarete')
        markers = len([i for i in re.finditer('AwesomeMarker', result)])
        scary_points = len(compare.loc[compare['scariness'] > gfrm.translate_fear_level(2)])
        circles = len([i for i in re.finditer('circle_marker', result)]) / 3
        self.assertEqual(markers, scary_points)
        self.assertEqual(circles, len(compare) - scary_points)
        markers_indices = [m.start() for m in re.finditer('AwesomeMarker', result)]
        markers_html = [result[i:i+1200] for i in markers_indices]
        for marker_html in markers_html:
            scariness = int(marker_html.split('%')[197][2])
            self.assertGreater(scariness, gfrm.translate_fear_level(2))

        result = gfrm.get_folium_route_map(
            3, route_file=None, route_choice='carnmordeargarete')
        compare = gfrm.get_route_with_scariness_from_db('carnmordeargarete')
        markers = len([i for i in re.finditer('AwesomeMarker', result)])
        scary_points = len(compare.loc[compare['scariness'] > gfrm.translate_fear_level(3)])
        circles = len([i for i in re.finditer('circle_marker', result)]) / 3
        self.assertEqual(markers, scary_points)
        self.assertEqual(circles, len(compare) - scary_points)
        markers_indices = [m.start() for m in re.finditer('AwesomeMarker', result)]
        markers_html = [result[i:i+1200] for i in markers_indices]
        for marker_html in markers_html:
            scariness = int(marker_html.split('%')[197][2])
            self.assertGreater(scariness, gfrm.translate_fear_level(3))

    def test_get_route_with_scariness_from_file(self):
        result = gfrm.get_route_with_scariness_from_file('../data/ben-more.gpx')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.isnull().values.any())
        self.assertEqual(Counter(list(result)),
                         Counter(['waypoint', 'lat', 'long', 'elevation', 'scariness', 'route',
                          'created_dt']))

    def test_check_route_not_loaded(self):
        result1 = gfrm.check_route_not_loaded('../data/carnmordeargarete.gpx')
        self.assertTrue(result1)
        result2 = gfrm.check_route_not_loaded('data/fakemountain.gpx')
        self.assertFalse(result2)

    def test_translate_fear_level(self):
        self.assertEqual(gfrm.translate_fear_level(1), 6)
        self.assertEqual(gfrm.translate_fear_level(2), 5)
        self.assertEqual(gfrm.translate_fear_level(3), 4)


if __name__ == '__main__':
    unittest.main()
