from argparse import ArgumentParser
from geocoder import google as google_geo
import json
from math import atan2, cos, pi, radians, sin, sqrt
from os import path
from requests import RequestException
import sys
from unicodecsv import DictReader
import pdb

EARTH_RADIUS_KM = 6371
EARTH_RADIUS_MI = 3959


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points on the surface of the Earth using
    the haversine formula as described at
    https://www.movable-type.co.uk/scripts/latlong.html
    """
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    lat_diff = lat2_rad - lat1_rad
    lon_diff = radians(lon2 - lon1)

    a = sin(lat_diff / 2) ** 2 \
        + cos(lat1_rad) * cos(lat2_rad) * sin(lon_diff / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return c * EARTH_RADIUS_MI


def main():
    parser = ArgumentParser()
    main_arg_group = parser.add_mutually_exclusive_group(required=True)
    main_arg_group.add_argument('--address', type=str)
    main_arg_group.add_argument('--zip', type=str)
    parser.add_argument('--units', choices=['mi', 'km'])
    parser.add_argument('--output', choices=['text', 'json'])
    args = parser.parse_args()
    if args.address:
        starting_location = args.address
    elif args.zip:
        starting_location = args.zip
    else:
        sys.exit('You must provide a starting address or zip code to use this'
                 ' tool. Please try again.')

    # Use Geocoder library (https://github.com/DenisCarriere/geocoder) to
    # convert address or zip into coordinates via Google Maps Geocoding API
    try:
        geo_data = google_geo(starting_location)
    except RequestException:
        sys.exit('There was an issue connecting to the Google Maps API. Please'
                 ' check network status and try again.')
    starting_latlon = geo_data.latlng
    if not starting_latlon:
        sys.exit('The Google Maps API did not return a result. Please check'
                 ' your API credentials and the provided address or zip code'
                 ' before trying again.')

    script_path = path.abspath(path.dirname(__file__))
    data_path = path.join(script_path, '../data/store_locations.csv')
    closest_store = {}
    closest_distance = EARTH_RADIUS_MI * pi
    with open(data_path, 'rU') as store_data_file:
        store_reader = DictReader(store_data_file, encoding='utf-8-sig')
        for store in store_reader:
            start_lat, start_lon = starting_latlon
            store_lat = float(store['Latitude'])
            store_lon = float(store['Longitude'])
            distance = haversine(start_lat, start_lon, store_lat, store_lon)
            if distance < closest_distance:
                closest_store = store
                closest_distance = distance

    if args.units == 'km':
        closest_distance = closest_distance * EARTH_RADIUS_KM / EARTH_RADIUS_MI
    else:
        args.units = 'mi'

    if args.output == 'json':
        closest_store['Distance'] = closest_distance
        closest_store['Distance Units'] = args.units
        closest_store['Latitude'] = float(closest_store['Latitude'])
        closest_store['Longitude'] = float(closest_store['Longitude'])
        return json.dumps(closest_store)
    else:
        print '%s Location' % closest_store['Store Name']
        print closest_store['Store Location']
        print closest_store['Address']
        print '%s, %s %s' % (
            closest_store['City'],
            closest_store['State'],
            closest_store['Zip Code'],
        )
        print '%s %s' % (round(closest_distance, 2), args.units)


if __name__ == '__main__':
    main()
