#-------------------------------------------------------------------------------------
#
# Given a font size, find its height (in pixels) on the current display.
# This is useful so you can coordinate between an expyriment TextBox's "size" and "text_size"
# properties
#
#-------------------------------------------------------------------------------------

from trajtracker.utils import get_font_height_to_size_ratio


font_name = "Arial"

ratio = get_font_height_to_size_ratio(font_name)

print("For font {:}, the height/size ratio is {:}".format(font_name, ratio))
