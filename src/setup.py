from setuptools import setup, find_packages
from os import listdir


setup(name='trajtracker',
      version='1.0.0',
      description='Framework for creating trajectory-tracking experiments',
      url='http://trajtracker.com',
      author='Dror Dotan',
      author_email='dror@trajtracker.com',
      license='GPL',
      packages=find_packages(),
      install_requires=['expyriment', 'numpy', 'enum34'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6'
      ],
      zip_safe=False)
