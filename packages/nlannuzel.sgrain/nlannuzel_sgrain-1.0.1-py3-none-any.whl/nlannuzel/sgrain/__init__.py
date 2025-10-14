import datetime
import time
import argparse
from nlannuzel.sgrain.rain import RainAreas
from nlannuzel.sgrain.geo import Location

def rain_intensity_at():
    parser = argparse.ArgumentParser(
        prog = 'rain-intensity-at',
        description = "Tells if it's raining at the given location")
    parser.add_argument('-a', '--latitude', required = True, help = 'latitude in decimal')
    parser.add_argument('-o', '--longitude', required = True, help = 'longitude in decimal')
    parser.add_argument('-c', '--cachedir', help = 'directory that holds downloaded images')
    parser.add_argument('-O', '--output', help = 'output file')
    parser.add_argument('-p', '--squaresize', help = 'square area to consider around location (in pixels)')
    parser.add_argument('-Y', '--year', help = 'year to consider instead of current date/time' )
    parser.add_argument('-M', '--month', help = 'month to consider instead of current date/time' )
    parser.add_argument('-D', '--day', help = 'day to consider instead of current date/time' )
    parser.add_argument('-H', '--hour', help = 'hour to consider instead of current date/time' )
    parser.add_argument('-m', '--minute', help = 'minute to consider instead of current date/time. Will be rounded down to 5 min.' )
    args = parser.parse_args()

    rain = RainAreas(cache_dir = args.cachedir if args.cachedir else None)

    dt = None
    if args.year:
        dt = datetime.datetime(
            year=int(args.year),
            month=int(args.month),
            day=int(args.day),
            hour=int(args.hour),
            minute=int(args.minute))
    rain.load_image(dt)

    location = Location(
        lat = float(args.latitude),
        lon = float(args.longitude))
    if args.output:
        rain.save_intensity_map(args.output, location, 0 if args.squaresize else int(args.square_size))
    print(rain.intensity_at(location, int(args.squaresize)))
