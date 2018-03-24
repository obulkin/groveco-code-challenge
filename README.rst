==========
find_store
==========

This package provides the ``find_store`` CLI utility, which takes in an address
or ZIP code and returns the closest store to that location based on an included
CSV file with store data. Under the hood, it works as follows:

#. Command line input is parsed and validated with the help of the ``argparse``
   library, and error messages are generated as needed.
#. The ``geocoder`` library is used to call the Google Maps Geocoding API,
   which converts the provided address or zip code into latitude and longitude
   coordinates. Several errors may arise during this process and are handled by
   notifying the user and terminating the program.
#. Store data in the included CSV file is proccessed linearly, and the distance
   between the starting point and each store is calculated using the haversine
   formula, which is implemented in a separate function. The closest store is
   tracked along the way and retained at the end of the process, along with its
   distance from the starting point.
#. The distance is converted from miles to kilometers if necessary.
#. Info about the closest store and its distance from the starting point is
   printed to the screen in a human-readable format or returned as a JSON
   string (this depends on which option was selected).

Installation
============

To install the package, download the full contents of this repo into the
directory of your choice and then do the following::

    cd {package_directory}
    python setup.py install

You will need Python ``2.7`` (other versions have not been tested and may not
be supported) and credentials for the Google Maps Geocoding API. Please ensure
that the latter are present in your environment and named ``GOOGLE_API_KEY`` or
``GOOGLE_CLIENT`` and ``GOOGLE_CLIENT_SECRET``. If necessary, you can obtain a
key `here <https://developers.google.com/maps/documentation/geocoding/get-api-key>`_.

Usage
=====

Usage instructions can be found in the
`original exercise <https://github.com/groveco/code-challenge>`_.

Unit Tests
==========

To run unit tests, first install the package and then::

    cd {package_directory}
    python -m unittest -bv find_store.test_find_store
