
import xml.etree.ElementTree as ET
import trajtracker as ttrk


class XmlConfigUpdater(ttrk._TTrkObject):
    """

    """

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

        obj_attr_types = obj.config_attr_types if 'config_attr_types' in dir(obj) else {}

        #-- Update by XML attributes
        for attr_name in xml.attrib:
            value = xml.attrib[attr_name]
            value_converter = self._get_attr_type(obj, attr_name, obj_attr_types)
            if value_converter is not None:
                value = value_converter(value)
            obj.__setattr__(attr_name, value)

        #-- Update by XML elements: this must be done via functions
        for sub_element in xml:
            value_converter = self._get_attr_type(obj, sub_element.tag, obj_attr_types)
            if value_converter is None:
                raise ttrk.BadFormatError(
                    ('Invalid XML configuration: to configure {:}.{:}, use <{:} {:}="..."/>' +
                     ' should be defined as an XML attribute, not as an element').format(
                        type(obj).__name__, sub_element.tag, type(obj).__name__, sub_element.tag))
            if not isinstance(value_converter, type(lambda:1)):
                raise ttrk.BadFormatError(
                    ('Invalid XML configuration fo {:}.{:}: to configure an attribute with an XML block (<{:} ...>), ' +
                     'you must explicitly specify the function that parses this block').format(
                        type(obj).__name__, sub_element.tag, sub_element.tag))
            obj.__setattr__(sub_element.tag, value_converter(sub_element))

    #--------------------------------------------------
    def _get_attr_type(self, obj, attr_name, attr_types):
        if attr_name not in dir(obj):
            raise TypeError(
                "trajtracker error: invalid XML configuration - object {:} does not have a '{:}' attribute".format(
                    type(obj).__name__, attr_name))

        return attr_types[attr_name] if attr_name in attr_types else None



#--------------------------------------------------
def load_xml(filename):

    root = ET.parse(filename)
    return _xml_to_object(root.getroot())

