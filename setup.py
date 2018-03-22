from setuptools import setup

setup(
    name='find_store',
    version='1.0.0',
    packages=['find_store'],
    entry_points={
        'console_scripts': ['find_store = find_store.__main__:main'],
    },
    install_requires=['geocoder', 'unicodecsv'],
)
