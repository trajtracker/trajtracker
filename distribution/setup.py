from setuptools import setup

setup(name='trajtracker',
      version='0.0.1',
      description='Framework for creating trajectory-tracking experiments',
      url='http://trajtracker.com',
      author='Dror Dotan',
      author_email='dror@trajtracker.com',
      license='MIT',
      packages=['trajtracker',
                'trajtracker.events',
                'trajtracker.io',
                'trajtracker.misc',
                'trajtracker.misc.nvshapes',
                'trajtracker.movement',
                'trajtracker.paradigms',
                'trajtracker.paradigms.general',
                'trajtracker.paradigms.num2pos',
                'trajtracker.stimuli',
                'trajtracker.validators'],
      install_requires=['expyriment'],
      zip_safe=False)

