import json
from mock import mock_open, patch
from os import path
from requests import RequestException
from sys import stdout
from unicodecsv import DictReader
from unittest import TestCase
from ..__main__ import haversine, main

MAIN_PATH = 'find_store.__main__'
PARSER_PATH = MAIN_PATH + '.ArgumentParser'
GEO_PATH = MAIN_PATH + '.google_geo'
OPEN_PATH = MAIN_PATH + '.open'
READER_PATH = MAIN_PATH + '.DictReader'
HAV_PATH = MAIN_PATH + '.haversine'
STDOUT_PATH = 'sys.stdout'

MOCK_CSV_DATA = [
    'Store Name,Store Location,Address,City,State,Zip Code,Latitude,Longitude,'
    'County\n',
    'Crystal,SWC Broadway & Bass Lake Rd,5537 W Broadway Ave,Crystal,MN,'
    '55428-3507,45.0521539,-93.364854,Hennepin County\n',
    'Mission Viejo,NEC Alicia Parkway & I-5,24500 Alicia Pkwy,Mission Viejo,'
    'CA,92691-4508,33.6063297,-117.6881656,Orange County\n',
]


class TestMain(TestCase):
    def csv_mock_creator():
        return mock_open(read_data=MOCK_CSV_DATA)

    def test_haversine_same_quadrant(self):
        """It should return correct distance when points in same quadrant"""
        result = haversine(3.2, 4.7, 53.61, 65.01)

        self.assertEqual(round(result, 2), 4852.35)

    def test_haversine_different_quadrants(self):
        """It should return correct distance if points not in same quadrant"""
        result = haversine(3.2, 4.7, -53.61, -65.01)

        self.assertEqual(round(result, 2), 5580.70)

    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_argument_parser_setup(self, parser_mock, geo_mock):
        """It should properly set up argument parser"""
        geo_mock().latlng = [0, 0]
        main()

        parser_mock.assert_called_once_with()
        parser_mock().add_mutually_exclusive_group.assert_called_once_with(
            required=True,
        )
        main_group_mock = parser_mock().add_mutually_exclusive_group()
        main_group_mock.add_argument.assert_any_call('--address', type=str)
        main_group_mock.add_argument.assert_any_call('--zip', type=str)
        self.assertEqual(main_group_mock.add_argument.call_count, 2)
        parser_mock().add_argument.assert_any_call(
            '--units',
            choices=['mi', 'km'],
        )
        parser_mock().add_argument.assert_any_call(
            '--output',
            choices=['text', 'json'],
        )
        self.assertEqual(parser_mock().add_argument.call_count, 2)

    @patch(PARSER_PATH)
    def test_main_blank_address(self, parser_mock):
        """It should exit with correct error message if blank address given"""
        parser_mock().parse_args().address = ''
        parser_mock().parse_args().zip = None

        with self.assertRaisesRegexp(SystemExit, 'provide a starting address'):
            main()

    @patch(PARSER_PATH)
    def test_main_blank_zip(self, parser_mock):
        """It should exit with correct error message if blank zip code given"""
        parser_mock().parse_args().address = None
        parser_mock().parse_args().zip = ''

        with self.assertRaisesRegexp(SystemExit, 'provide a starting address'):
            main()

    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_geocoding_address_provided(self, parser_mock, geo_mock):
        """It should call geocoding library with address if given"""
        parser_mock().parse_args().address = test_address = 'Test Address'
        parser_mock().parse_args().zip = None
        geo_mock.return_value.latlng = [0, 0]
        main()

        geo_mock.assert_called_once_with(test_address)

    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_geocoding_zip_provided(self, parser_mock, geo_mock):
        """It should call geocoding library with zip code if given"""
        parser_mock().parse_args().address = None
        parser_mock().parse_args().zip = test_zip = '94107'
        geo_mock.return_value.latlng = [0, 0]
        main()

        geo_mock.assert_called_once_with(test_zip)

    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_geocoding_not_responding(self, parser_mock, geo_mock):
        """It should exit with error message if geocoding API not responding"""
        parser_mock().parse_args().address = 'Test Address'
        parser_mock().parse_args().zip = None
        geo_mock.side_effect = RequestException

        with self.assertRaisesRegexp(SystemExit, 'issue connecting'):
            main()

    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_geocoding_no_coordinates(self, parser_mock, geo_mock):
        """It should exit with error message if API returns no coordinates"""
        parser_mock().parse_args().address = 'Test Address'
        parser_mock().parse_args().zip = None
        geo_mock().latlng = []

        with self.assertRaisesRegexp(SystemExit, 'API credentials'):
            main()

    @patch(OPEN_PATH, new_callable=csv_mock_creator)
    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_open_store_data(self, parser_mock, geo_mock, open_mock):
        """It should open correct data file"""
        parser_mock().parse_args().address = 'Test Address'
        parser_mock().parse_args().zip = None
        geo_mock().latlng = [0, 0]
        open_mock.return_value.__iter__ = lambda s: iter(MOCK_CSV_DATA)
        main()

        test_path = path.dirname(__file__)
        data_path = path.join(test_path, '../data/store_locations.csv')
        data_path = path.abspath(data_path)
        open_mock.assert_called_once_with(data_path, 'rU')

    @patch(READER_PATH, wraps=DictReader)
    @patch(OPEN_PATH, new_callable=csv_mock_creator)
    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_read_store_data(
        self, parser_mock, geo_mock, open_mock, reader_mock,
    ):
        """It should correctly pass store data file object to CSV reader"""
        parser_mock().parse_args().address = 'Test Address'
        parser_mock().parse_args().zip = None
        geo_mock().latlng = [0, 0]
        open_mock.return_value.__iter__ = lambda s: iter(MOCK_CSV_DATA)
        main()

        reader_mock.assert_called_once_with(open_mock(), encoding='utf-8-sig')

    @patch(HAV_PATH, wraps=haversine)
    @patch(OPEN_PATH, new_callable=csv_mock_creator)
    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_call_distance_helper(
        self, parser_mock, geo_mock, open_mock, hav_mock,
    ):
        """It should correctly call haversine helper once per store"""
        parser_mock().parse_args().address = 'Test Address'
        parser_mock().parse_args().zip = None
        geo_mock().latlng = [0, 0]
        open_mock.return_value.__iter__ = lambda s: iter(MOCK_CSV_DATA)
        main()

        hav_mock.assert_any_call(0, 0, 45.0521539, -93.364854)
        hav_mock.assert_any_call(0, 0, 33.6063297, -117.6881656)
        self.assertEqual(hav_mock.call_count, 2)

    @patch(STDOUT_PATH, wrap=stdout)
    @patch(OPEN_PATH, new_callable=csv_mock_creator)
    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_print_closest(
        self, parser_mock, geo_mock, open_mock, stdout_mock,
    ):
        """It should correctly find closest store and print its info"""
        parser_mock().parse_args().address = 'Test Address'
        parser_mock().parse_args().zip = None
        geo_mock().latlng = [0, 0]
        open_mock.return_value.__iter__ = lambda s: iter(MOCK_CSV_DATA)
        main()

        stdout_mock.write.assert_any_call('Crystal Location')
        stdout_mock.write.assert_any_call('SWC Broadway & Bass Lake Rd')
        stdout_mock.write.assert_any_call('5537 W Broadway Ave')
        stdout_mock.write.assert_any_call('Crystal, MN 55428-3507')
        stdout_mock.write.assert_any_call('6382.99 mi')
        # This includes newline calls automatically generated by print
        self.assertEqual(stdout_mock.write.call_count, 10)

    @patch(STDOUT_PATH, wrap=stdout)
    @patch(OPEN_PATH, new_callable=csv_mock_creator)
    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_print_closest_km(
        self, parser_mock, geo_mock, open_mock, stdout_mock,
    ):
        """It should convert distance to kilometers if option is provided"""
        parser_mock().parse_args().address = 'Test Address'
        parser_mock().parse_args().zip = None
        parser_mock().parse_args().units = 'km'
        geo_mock().latlng = [0, 0]
        open_mock.return_value.__iter__ = lambda s: iter(MOCK_CSV_DATA)
        main()

        stdout_mock.write.assert_any_call('10271.79 km')

    @patch(STDOUT_PATH, wrap=stdout)
    @patch(OPEN_PATH, new_callable=csv_mock_creator)
    @patch(GEO_PATH)
    @patch(PARSER_PATH)
    def test_main_print_json(
        self, parser_mock, geo_mock, open_mock, stdout_mock,
    ):
        """It should return a JSON string and not print if option provided"""
        parser_mock().parse_args().address = 'Test Address'
        parser_mock().parse_args().zip = None
        parser_mock().parse_args().units = 'km'
        parser_mock().parse_args().output = 'json'
        geo_mock().latlng = [0, 0]
        open_mock.return_value.__iter__ = lambda s: iter(MOCK_CSV_DATA)
        result = main()
        result_data = json.loads(result)
        result_data['Distance'] = round(result_data['Distance'], 2)

        expected_data = {
            u'Address': u'5537 W Broadway Ave',
            u'City': u'Crystal',
            u'County': u'Hennepin County',
            u'Distance': 10271.79,
            u'Distance Units': u'km',
            u'Latitude': 45.0521539,
            u'Longitude': -93.364854,
            u'State': u'MN',
            u'Store Location': u'SWC Broadway & Bass Lake Rd',
            u'Store Name': u'Crystal',
            u'Zip Code': u'55428-3507',
        }
        stdout_mock.write.assert_not_called()
        self.assertEqual(expected_data, result_data)
