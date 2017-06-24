from setuptools import setup, find_packages

setup(name='trajtracker',
      version='0.2.0',
      description='Framework for creating trajectory-tracking experiments',
      url='http://trajtracker.com',
      author='Dror Dotan',
      author_email='dror@trajtracker.com',
      license='GPL',
      packages = find_packages(),
      # packages=['trajtracker',
      #           'trajtracker.events',
      #           'trajtracker.io',
      #           'trajtracker.misc',
      #           'trajtracker.misc.nvshapes',
      #           'trajtracker.movement',
      #           'trajtracker.paradigms',
      #           'trajtracker.paradigms.common',
      #           'trajtracker.paradigms.dchoice',
      #           'trajtracker.paradigms.num2pos',
      #           'trajtracker.stimuli',
      #           'trajtracker.validators'],
      install_requires=['expyriment'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6'
      ],
      zip_safe=False)

