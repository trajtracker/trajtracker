"""

Picture set: A dictionary-like interface for a set of named pictures

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from enum import Enum
import re

from expyriment.stimuli import Picture

import trajtracker

class PictureSet(trajtracker._TTrkObject):
    """
     A class that holds a set of expyriment.stimuli.Picture objects, each with a logical name.
     It can retrieve each picture, and rescale all pictures to the same size
    """

    #
    # Defines how images are scaled to the dictionary's size:
    # None: No scaling
    # Stretch: scale width & height
    # Zoom: scale width & height while keeping proportions
    ScaleMethod = Enum('ScaleMethod', 'None Stretch Zoom')

    #=======================================================================================
    #    Configure set
    #=======================================================================================

    #------------------------------------------------------------------
    # Constructor
    def __init__(self, width, height, base_dir='/'):
        """
        Constructor

        :param width: Width of the picture returned
        :param height: Height of the picture returned
        :param base_dir: Base directory for all picture files
        """

        super(PictureSet, self).__init__()

        self._width = width
        self._height = height
        self._position = (0,0)

        self._scale_method = PictureSet.ScaleMethod.None
        self._base_dir = base_dir
        self._pics = {}
        self._unloaded_pic_configs = {}
        self._preloaded = False


    #------------------------------------------------------------------
    def add_picture(self, pic_name, pic_spec):
        """
        Add a picture to the set
        :param pic_name: A logical name of the picture
        :param pic_spec: The picture file name, or an expyriment.stimuli.Picture object
        """
        if self._preloaded:
            raise trajtracker.InvalidStateError('Pictures cannot be added to a PictureSet after it was preloaded')

        if pic_name in self._pics or pic_name in self._unloaded_pic_configs:
            print('trajtracker warning: Picture "{0}" already exists in the PictureSet, definition is overriden'.format(pic_name))

        if isinstance(pic_spec, str):
            self._unloaded_pic_configs[pic_name] = pic_spec

        elif isinstance(pic_spec, Picture):
            self._preload_pic(pic_name, pic_spec)

        else:
            raise ValueError('trajtracker error in ImageHolder.set_image() - Invalid file name: %s' % pic_spec)

    #------------------------------------------------------------------
    def add_pictures(self, config_string):
        """
        Add several images to the holder
        :param config_string: String of the format name1=file1;name2=file2;name3=file3 etc.
        You can use either comma or semicolon separators
        """

        config_list = re.split("[;,]", config_string)
        for cfg in config_list:
            try:
                ind = cfg.index('=')
                self.add_picture(cfg[:ind], cfg[ind + 1:])
            except ValueError:
                raise ValueError('trajtracker error in ImageHolder.set_images() - Invalid value given: %s' % cfg)

    #------------------------------------------------------------------
    def preload(self):
        if self._preloaded:
            return

        for img_name, filename in enumerate(self._unloaded_pic_configs):
            file_path = self._base_dir + '/' + filename
            img = Picture(file_path)
            self._preload_pic(img_name, img)

        self._preloaded = True

    #------------------------------------------------------------------
    # Preload one picture
    #
    def _preload_pic(self, img_name, img):
        img.preload()
        img.position = self._position

        if self._scale_method != PictureSet.ScaleMethod.None:
            w, h = img.surface_size
            w_proportion = self._width / w
            h_proportion = self._height / h

            if self._scale_method == PictureSet.ScaleMethod.Scale:
                #-- Keep width/height proportions
                img.scale(min(w_proportion, h_proportion))
            else:
                #-- Fully stretch to the available size
                img.scale((w_proportion, h_proportion))

        self._pics[img_name] = img

        self._unloaded_pic_configs = {}  # Clear the already-loaded configs, to allow more calls to preload()

    # =======================================================================================
    #    Manipulate pictures
    # =======================================================================================

    #------------------------------------------------------------------
    #  Run an operation per picture in the set
    #
    def _run_per_picture(self, callable):
        if not self._preloaded:
            raise trajtracker.InvalidStateError('The pictures in PictureSet cannot be manipulated before the set is pre-loaded')

        for name in self._pics:
            callable(self._pics[name])

    #------------------------------------------------------------------
    def scale(self, factors):
        self._run_per_picture(lambda pic: pic.scale(factors))

    #------------------------------------------------------------------
    def rotate(self, degrees):
        self._run_per_picture(lambda pic: pic.rotate(degrees))

    #------------------------------------------------------------------
    def flip(self, flip_xy):
        self._run_per_picture(lambda pic: pic.flip(flip_xy))

    #------------------------------------------------------------------
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = position
        self._log_setter("position")

        if self._preloaded:
            for name in self._pics:
                self._pics[name].position = position

    # =======================================================================================
    #    Access pictures
    # =======================================================================================

    #------------------------------------------------------------------
    # Get a single picture by calling PictureSet[pic_name]
    def __getitem__(self, pic_name):
        """
        Return a pre-loaded picture
        :param pic_name:
        """
        return self._pics[pic_name]


    def get_picture(self, item):
        return self[item]
