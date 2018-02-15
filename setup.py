from setuptools import setup, find_packages

setup(name='sde_inventory',
      version='0.0.1',
      packages=find_packages(),
      entry_points={
           'console_scripts': [
               'sde_inventory=sde_inventory.cli:main',
           ],
      },
      install_requires=['click', 'PyYAML',]
     )
