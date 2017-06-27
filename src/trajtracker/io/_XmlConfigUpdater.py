"""
@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

This file is part of TrajTracker.

TrajTracker is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TrajTracker is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with TrajTracker.  If not, see <http://www.gnu.org/licenses/>.
"""
import inspect, re
import xml.etree.ElementTree as ET
import expyriment as xpy

import trajtracker as ttrk


class XmlConfigUpdater(ttrk.TTrkObject):
    """

    """

    _vars_for_eval = {}

    def __init__(self):
        super(XmlConfigUpdater, self).__init__()


    #--------------------------------------------------
    def configure_objects(self, xml, objects, xml_source):

        for one_obj_config in xml:
            obj_id = one_obj_config.tag

            #-- Make sure that this object in fact exists
            if obj_id not in objects:
                raise ttrk.BadFormatError("Invalid xml configuration in {:} (<'{:}' ...>): there is no object to configure named {:}".format(
                    xml_source, obj_id, obj_id))

            self.configure_object(one_obj_config, objects[obj_id])


    #--------------------------------------------------
    def configure_object(self, xml, obj):

        self._init_vars_for_eval()

        #-- Update by XML attributes
        for attr_name in xml.attrib:
            self._validate_attr(obj, attr_name)
            value = self._eval_value(xml.attrib[attr_name])
            setattr(obj, attr_name, _ValueFromXML(xml.tag, value))

        #-- Update by XML elements: this must be done via functions
        for sub_element in xml:
            self._validate_attr(obj, sub_element.tag)
            setattr(obj, sub_element.tag, _ValueFromXML(xml.tag, sub_element))


    #--------------------------------------------------
    def _validate_attr(self, obj, attr_name):
        try:
            setattr(obj, attr_name, _TestIfXmlSupported())
            raise ttrk.BadFormatError('Invalid XML configuration: {:}.{:} cannot be configured from XML'.format(type(obj).__name__, attr_name))
        except _TestIfXmlSupported:
            pass


    #---------------------------------------------------
    # Initialize constants for evaluation by _eval_value()
    #
    def _init_vars_for_eval(self):
        XmlConfigUpdater._vars_for_eval = {}
        if xpy._internals.active_exp.screen is None:
            print("trajtracker WARNING: Expyriment screen was not yet initialized; its size will not be available for XML configuration")
            XmlConfigUpdater._vars_for_eval['screen_width'] = 'N/A'
            XmlConfigUpdater._vars_for_eval['screen_height'] = 'N/A'
        else:
            XmlConfigUpdater._vars_for_eval['screen_width'] = xpy._internals.active_exp.screen.size[0]
            XmlConfigUpdater._vars_for_eval['screen_height'] = xpy._internals.active_exp.screen.size[1]

    #---------------------------------------------------
    # If a string value is ${....} - evaluate it as a python expression
    #
    @staticmethod
    def _eval_value(attr_value):
        m = re.match('^\${(.*)}$', attr_value)
        if m is None:
            return attr_value
        else:
            return eval(m.group(1), XmlConfigUpdater._vars_for_eval)

#==================================================================
# Annotations to define on the class
#==================================================================


#------------------------------------------------------------------------------------
# When setting attribute value from XML, we set it to this value
#
class _ValueFromXML(object):
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value


class _TestIfXmlSupported(Exception):
    pass




#------------------------------------------------------------------------------------
# Actually convert the value from the XML (string if it was an attribute; or an XML Element) to the
# target object's expected attribute value
#
def _convert_xml_value_to_attr_value(obj, attr_name, xml_value, converter, convert_raw_xml):

    value = xml_value.value

    if convert_raw_xml:
        #-- Make sure that we got the XML node
        if not isinstance(xml_value.value, ET.Element):
            raise ttrk.BadFormatError(
                'Invalid XML configuration <{:} ...>: to configure {:}.{:} via XML, you must define a sub-block'.format(
                xml_value.tag, type(obj).__name__, attr_name))

    elif isinstance(xml_value.value, ET.Element):
        #-- We got the XML element (node), but we need its text value
        value = XmlConfigUpdater._eval_value(xml_value.value.text.strip())

    if converter is None:
        return value
    else:
        return converter(value)


#------------------------------------------------------------------------------------
# The annotation
#
# noinspection PyPep8Naming
def fromXML(converter, raw_xml=False):

    #-- Define the real decorator
    def real_decorator(setter):

        #-- Create a setter for the attribute
        def set_attr_from_xml(self, value):
            if isinstance(value, _ValueFromXML):
                setter(self, _convert_xml_value_to_attr_value(self, setter.__name__, value, converter, raw_xml))
            elif isinstance(value, _TestIfXmlSupported):
                raise _TestIfXmlSupported()
            else:
                setter(self, value)

        return set_attr_from_xml

    return real_decorator

