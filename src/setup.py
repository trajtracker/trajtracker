from setuptools import setup, find_packages
from os import listdir
import trajtracker

ver = trajtracker.version()

setup(name='trajtracker',
      version='{:}.{:}.{:}'.format(ver[0], ver[1], ver[2]),
      description='Framework for creating trajectory-tracking experiments',
      url='http://trajtracker.com',
      author='Dror Dotan',
      author_email='dror@trajtracker.com',
      license='GPL',
      packages=find_packages(),
      install_requires=['expyriment', 'numpy', 'enum34', 'pandas', 'pygame'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6'
      ],
      zip_safe=False)
