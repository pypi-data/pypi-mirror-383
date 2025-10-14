import unittest
from nlannuzel.sgrain.rain import RainAreas
import datetime

class TestRain(unittest.TestCase):
    def test_round(self):
        rain = RainAreas()

        self.assertEqual(len(rain.color_scale), 32)

        sx = 217 / (rain.bottom_right.lon - rain.top_left.lon)
        sy = 120 / (rain.top_left.lat - rain.bottom_right.lat)
        error = abs(1 - sx/sy)
        self.assertTrue( error < 2/100 )

        rounded = rain.round_to_previous_5_min(datetime.datetime(year = 2025, month = 10, day = 11, hour = 12, minute = 13))
        self.assertEqual( rounded.year  , 2025)
        self.assertEqual( rounded.month , 10)
        self.assertEqual( rounded.day   , 11)
        self.assertEqual( rounded.hour  , 12)
        self.assertEqual( rounded.minute, 10)

        rounded = rain.round_to_previous_5_min(datetime.datetime(year = 2025, month = 10, day = 11, hour = 12, minute = 20))
        self.assertEqual( rounded.year  , 2025)
        self.assertEqual( rounded.month , 10)
        self.assertEqual( rounded.day   , 11)
        self.assertEqual( rounded.hour  , 12)
        self.assertEqual( rounded.minute, 20)

if __name__ == '__main__':
    unittest.main()
