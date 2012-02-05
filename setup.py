from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='haifu',
      version=version,
      description="A social network backend service",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Izhar Firdaus',
      author_email='izhar@inigo-tech.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
        'grokcore.component',
        'tornado',
        'TornadIO',
        'argh',
        'simplejson',
        'xmldict'
      ],
      entry_points={
          'console_scripts': [
              'haifu-admin = haifu.scripts:main',
           ]
      }
      )
