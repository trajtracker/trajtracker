import unittest
import xml.etree.ElementTree as ET

from trajtracker.data import XmlConfigUpdater
import trajtracker as ttrk


class SampleObjectNoAttrTypes(object):

    def __init__(self):
        self._z = None
        self._y = None

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value



class SampleObject(SampleObjectNoAttrTypes):

    def __init__(self, attr_types):
        super(SampleObject, self).__init__()
        self._attr_types = attr_types


    @property
    def config_attr_types(self):
        return self._attr_types


class XmlConfigUpdaterTests(unittest.TestCase):


    #-----------------------------------------------------------
    def test_configure_basic(self):
        updater = XmlConfigUpdater()
        obj = SampleObject({})
        xml = ET.fromstring('<data x="x" y="y"/>')
        updater.configure_object(xml, obj)
        self.assertEqual('x', obj.x)
        self.assertEqual('y', obj.y)


    #-----------------------------------------------------------
    def test_configure_no_attr_types(self):
        updater = XmlConfigUpdater()
        obj = SampleObjectNoAttrTypes()
        xml = ET.fromstring('<data x="x" y="y"/>')
        updater.configure_object(xml, obj)
        self.assertEqual('x', obj.x)
        self.assertEqual('y', obj.y)


    #-----------------------------------------------------------
    def test_configure_cast_by_type(self):
        updater = XmlConfigUpdater()
        obj = SampleObject({'x': int})
        xml = ET.fromstring('<data x="1" y="2"/>')
        updater.configure_object(xml, obj)
        self.assertEqual(1, obj.x)
        self.assertEqual('2', obj.y)


    #-----------------------------------------------------------
    def test_configure_cast_by_func(self):
        updater = XmlConfigUpdater()
        obj = SampleObject({'x': lambda value: int(value) + 1})
        xml = ET.fromstring('<data x="1" y="2"/>')
        updater.configure_object(xml, obj)
        self.assertEqual(2, obj.x)
        self.assertEqual('2', obj.y)


    #-----------------------------------------------------------
    def test_configure_cast_element_by_func(self):
        updater = XmlConfigUpdater()
        obj = SampleObject({'x': lambda elem: elem.text.strip()})
        xml = ET.fromstring('<data y="2"> <x> hello there! </x>  </data>')
        updater.configure_object(xml, obj)
        self.assertEqual("hello there!", obj.x)

    #-----------------------------------------------------------
    def test_cant_cast_element_without_func(self):
        updater = XmlConfigUpdater()
        obj = SampleObject({'x': int})
        xml = ET.fromstring('<data> <x> hello there! </x>  </data>')
        self.assertRaises(ttrk.BadFormatError, lambda: updater.configure_object(xml, obj))

    #-----------------------------------------------------------
    def test_cant_cast_element_without_explicit_def(self):
        updater = XmlConfigUpdater()
        obj = SampleObject({})
        xml = ET.fromstring('<data> <x> hello there! </x>  </data>')
        self.assertRaises(ttrk.BadFormatError, lambda: updater.configure_object(xml, obj))



    #============================================================================
    #   Multiple objects
    #============================================================================

    #-----------------------------------------------------------
    def test_configure_multiple_objects(self):
        updater = XmlConfigUpdater()
        a = SampleObject({})
        b = SampleObject({})
        xml = ET.fromstring("""
        <data>
            <a x="ax" y="ay"/>
            <b x="bx" y="by"/>
        </data>
        """)
        updater.configure_objects(xml, {'a': a, 'b': b}, "")
        self.assertEqual('ax', a.x)
        self.assertEqual('by', b.y)

    #-----------------------------------------------------------
    def test_object_missing(self):
        updater = XmlConfigUpdater()
        a = SampleObject({})

        xml = ET.fromstring("""
        <data>
            <a x="ax" y="ay"/>
            <b x="bx" y="by"/>
        </data>
        """)

        self.assertRaises(ttrk.BadFormatError, lambda: updater.configure_objects(xml, {'a': a}, ""))





if __name__ == '__main__':
    unittest.main()
