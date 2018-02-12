from setuptools import setup, find_packages

setup(name='gis_inventory',
      version='0.0.1',
      packages=find_packages(),
      entry_points={
           'console_scripts': [
               'gis_inventory=gis_inventory.cli:main',
           ],
      }
     )
