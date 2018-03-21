from argparse import ArgumentParser
from geocoder import google as google_geo
from requests import RequestException
import sys
import pdb


def main():
    parser = ArgumentParser()
    main_arg_group = parser.add_mutually_exclusive_group(required=True)
    main_arg_group.add_argument('--address', type=str)
    main_arg_group.add_argument('--zip', type=str)
    args = parser.parse_args()

    # Use Geocoder library (https://github.com/DenisCarriere/geocoder) to
    # convert address or zip into coordinates via Google Maps API
    try:
        address = args.address if args.address else args.zip
        geo_data = google_geo(address)
    except RequestException:
        sys.exit('There was an issue connecting to the Google Maps API. Please'
                 ' check network status and try again.')
    location_latlng = geo_data.latlng
    if not location_latlng:
        sys.exit('The Google Maps API did not return a result. Please check'
                 ' your API credentials and the provided address or zip code'
                 ' before trying again.')

    # pdb.set_trace()
    print('Running!')


if __name__ == '__main__':
    main()
