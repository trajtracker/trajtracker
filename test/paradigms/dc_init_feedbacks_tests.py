import unittest

import trajtracker as ttrk
from trajtracker.paradigms import common, dchoice
from trajtracker.paradigms.dchoice._dc_init import _get_feedback_rect_sizes, _get_feedback_stim_positions


class MyExpInfo(dchoice.ExperimentInfo):

    def __init__(self, feedback_mode):
        config = dchoice.Config("exp", None, 1, feedback_mode=feedback_mode)
        super(MyExpInfo, self).__init__(config, None, "id", "name")
        self._screen_size = 200, 100

    @property
    def screen_size(self):
        return self._screen_size

    def set_screen_size(self, value):
        self._screen_size = value



#============================================================================

class InitFeedbackTests(unittest.TestCase):

    #----------------------------------------------------------------------
    def test_size_to_pixels(self):
        self.assertEqual(common.size_to_pixels((10, 5), (200, 100)), (10, 5))
        self.assertEqual(common.size_to_pixels((0.1, 5), (200, 100)), (20, 5))
        self.assertIsNone(common.size_to_pixels((0, 10)))
        self.assertIsNone(common.size_to_pixels((0.1, 10)))


    #===================================================
    #    Size of feedback area
    #===================================================

    #----------------------------------------------------------------------
    def test_get_feedback_rect_sizes_explicit(self):
        exp_info = MyExpInfo('button')
        exp_info.config.feedback_rect_size = 40, 30
        exp_info.response_button_size = 20, 10
        sizes = _get_feedback_rect_sizes(exp_info)
        self.assertEqual(sizes[0], (40, 30))
        self.assertEqual(sizes[1], (40, 30))


    #----------------------------------------------------------------------
    def test_get_feedback_rect_sizes_explicit_pcnt(self):
        exp_info = MyExpInfo('button')
        exp_info.config.feedback_rect_size = 0.1, 0.05
        exp_info.response_button_size = 20, 10
        sizes = _get_feedback_rect_sizes(exp_info)
        self.assertEqual(sizes[0], (20, 5))


    #----------------------------------------------------------------------
    def test_get_feedback_rect_sizes_explicit_2(self):
        exp_info = MyExpInfo('button')
        exp_info.config.feedback_rect_size = (40, 30), (10, 20)
        exp_info.response_button_size = 20, 10
        sizes = _get_feedback_rect_sizes(exp_info)
        self.assertEqual(sizes[0], (40, 30))
        self.assertEqual(sizes[1], (10, 20))


    #----------------------------------------------------------------------
    def test_get_feedback_rect_sizes_default_button(self):
        exp_info = MyExpInfo('button')
        exp_info.response_button_size = 20, 10
        sizes = _get_feedback_rect_sizes(exp_info)
        self.assertEqual(sizes[0], (20, 10))
        self.assertEqual(sizes[1], (20, 10))


    #----------------------------------------------------------------------
    def test_get_feedback_rect_sizes_default_single(self):
        exp_info = MyExpInfo('single')
        exp_info.response_button_size = 20, 10
        sizes = _get_feedback_rect_sizes(exp_info)
        self.assertEqual(sizes[0], (160, 2))
        self.assertEqual(sizes[1], (160, 2))


    #----------------------------------------------------------------------
    def test_get_feedback_rect_sizes_default_single_with_y(self):
        exp_info = MyExpInfo('single')
        exp_info.config.feedback_rect_size = 5
        exp_info.response_button_size = 20, 10
        sizes = _get_feedback_rect_sizes(exp_info)
        self.assertEqual(sizes[0], (160, 5))
        self.assertEqual(sizes[1], (160, 5))


    #----------------------------------------------------------------------
    def test_get_feedback_rect_sizes_default_single_with_y_pcnt(self):
        exp_info = MyExpInfo('single')
        exp_info.config.feedback_rect_size = 0.05
        exp_info.response_button_size = 20, 10
        sizes = _get_feedback_rect_sizes(exp_info)
        self.assertEqual(sizes[0], (160, 5))
        self.assertEqual(sizes[1], (160, 5))

    #===================================================
    #    Position of feedback area
    #===================================================

    #----------------------------------------------------------------------
    def test_get_feedback_pos_explicit(self):
        exp_info = MyExpInfo('button')
        exp_info.config.feedback_stim_position = 10, 20
        pos = _get_feedback_stim_positions(exp_info, [(20, 10), (40, 30)])
        self.assertEqual(pos[0], (10, 20))
        self.assertEqual(pos[1], (10, 20))


    #----------------------------------------------------------------------
    def test_get_feedback_pos_explicit_two(self):
        exp_info = MyExpInfo('button')
        exp_info.config.feedback_stim_position = (-10, 20), (10, 20)
        pos = _get_feedback_stim_positions(exp_info, [(20, 10), (40, 30)])
        self.assertEqual(pos[0], (-10, 20))
        self.assertEqual(pos[1], (10, 20))


    #----------------------------------------------------------------------
    def test_get_feedback_pos_default_button(self):
        exp_info = MyExpInfo('button')
        pos = _get_feedback_stim_positions(exp_info, [(20, 10), (40, 30)])
        self.assertEqual(pos[0], (-90, 45))
        self.assertEqual(pos[1], (80, 35))


    #----------------------------------------------------------------------
    def test_get_feedback_pos_default_single(self):
        exp_info = MyExpInfo('single')
        pos = _get_feedback_stim_positions(exp_info, [(20, 10), (40, 30)])
        self.assertEqual(pos[0], (0, 45))
        self.assertEqual(pos[1], (0, 35))




if __name__ == '__main__':
    unittest.main()
