import unittest
from get_db_table import get_tables
from collections import Counter


class MyTestCase(unittest.TestCase):
    def test_get_db_table(self):
        max_long = -2.8
        min_long = -7.09
        expected = (f'locations{i}' for i in range(1, 84))
        result = get_tables(max_long, min_long)
        self.assertEqual(Counter(expected), Counter(result))


if __name__ == '__main__':
    unittest.main()
