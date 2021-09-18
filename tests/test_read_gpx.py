import unittest
import read_gpx as gpx
import pandas as pd
from pathlib import Path


class MyTestCase(unittest.TestCase):
    def test_read_gpx(self):
        file1 = Path('../data/bennevis.gpx')
        result1 = gpx.read_gpx(file1)
        self.assertIsInstance(result1, pd.DataFrame)

        file = Path('../data/macdui-cairngorm.gpx')
        result = gpx.read_gpx(file)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(['name', 'lat', 'long', 'elevation'], list(result))
        self.assertEqual(result.iloc[0]['lat'], 57.1334521657628)
        self.assertEqual(105, len(result))
        self.assertEqual(list(result.iloc[104]), ['Md-C105', 57.1334279564165, -3.67075015728156, 642.294851474619])

        file2 = Path('../data/Glenshielridge.gpx')
        result2 = gpx.read_gpx(file2)
        self.assertIsInstance(result2, pd.DataFrame)
        self.assertEqual(['name', 'lat', 'long', 'elevation'], list(result2))
        self.assertEqual(234, len(result2))
        self.assertEqual(list(result2.iloc[146]), ['SGS147', 57.134084, -5.281181, 994])

    def test_pad_gpx_dataframe(self):
        file = Path('../data/macdui-cairngorm.gpx')
        result = gpx.read_gpx(file)
        result = result.iloc[list(range(5))]
        padded_result = gpx.pad_gpx_dataframe(result)
        self.assertIsInstance(padded_result, pd.DataFrame)
        self.assertEqual(len(padded_result), len(result)*2-1)
        for i in range(4):
            expected = ['', 57.133315, -3.67459, 642.038455]
            self.assertAlmostEqual(list(padded_result.iloc[1])[i], expected[i], places=2)

    def test_get_route_bounds(self):
        route = gpx.read_gpx('../data/bennevis.gpx')
        result = gpx.get_route_bounds(route)
        self.assertIsInstance(result, list)
        self.assertAlmostEqual(result[0], 56.810818521)
        self.assertAlmostEqual(result[3], -5.077133203)


if __name__ == '__main__':
    unittest.main()
