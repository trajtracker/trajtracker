import unittest
import xml.etree.ElementTree as ET

from trajtracker.data import XmlConfigUpdater, fromXML
import trajtracker as ttrk


class SimpleSampleObject(object):
    @property
    def x(self):
        return self._x

    @x.setter
    @fromXML(str)
    def x(self, value):
        self._x = value




class Sample1:
    def __init__(self):
        self.x = None

    @property
    def x(self):
        return self._x

    @x.setter
    @fromXML(lambda value: int(value) + 1)
    def x(self, value):
        self._x = value


class XmlConfigUpdaterTests(unittest.TestCase):


    #-----------------------------------------------------------
    def test_configure_unsupported_attr(self):
        updater = XmlConfigUpdater()
        obj = SimpleSampleObject()
        xml = ET.fromstring('<data z="x"/>')
        self.assertRaises(ttrk.BadFormatError, lambda: updater.configure_object(xml, obj))


    #-----------------------------------------------------------
    def test_cant_cast_element_without_func(self):
        class Sample(object):
            @property
            def x(self):
                return self._x

            @x.setter
            @fromXML(str)
            def x(self, value):
                self._x = value

        updater = XmlConfigUpdater()
        obj = Sample()
        xml = ET.fromstring('<data> <x> hello there! </x>  </data>')
        updater.configure_object(xml, obj)
        self.assertEqual("hello there!", obj.x)



    #==========================================================================
    # Configure to predefined types
    #==========================================================================


    #-----------------------------------------------------------
    def test_configure_attribute(self):
        updater = XmlConfigUpdater()
        obj = SimpleSampleObject()
        xml = ET.fromstring('<data x="1"/>')
        updater.configure_object(xml, obj)
        self.assertEqual('1', obj.x)


    #-----------------------------------------------------------
    def test_configure_element(self):
        updater = XmlConfigUpdater()
        obj = SimpleSampleObject()
        xml = ET.fromstring('<data> <x> hello there! </x>  </data>')
        updater.configure_object(xml, obj)
        self.assertEqual("hello there!", obj.x)



    #-----------------------------------------------------------
    def test_configure_cast_by_type(self):
        class Sample(object):
            @property
            def x(self):
                return self._x

            @x.setter
            @fromXML(int)
            def x(self, value):
                self._x = value

        updater = XmlConfigUpdater()
        obj = Sample()
        xml = ET.fromstring('<data x="1"/>')
        updater.configure_object(xml, obj)
        self.assertEqual(1, obj.x)


    #==========================================================================
    # Convert values by functions
    #==========================================================================


    #-----------------------------------------------------------
    def test_configure_attr_via_func(self):
        class Sample(object):
            @property
            def x(self):
                return self._x

            @x.setter
            @fromXML(lambda value: int(value) + 1)
            def x(self, value):
                self._x = value

        updater = XmlConfigUpdater()
        obj = Sample()
        xml = ET.fromstring('<data x="1"/>')
        updater.configure_object(xml, obj)
        self.assertEqual(2, obj.x)


    #-----------------------------------------------------------
    def test_configure_element_via_func(self):
        class Sample(object):
            def __init__(self):
                self.x = None

            @property
            def x(self):
                return self._x

            @x.setter
            @fromXML(lambda v: int(v))
            def x(self, value):
                self._x = value

        updater = XmlConfigUpdater()
        obj = Sample()
        xml = ET.fromstring('<data> <x>1</x> </data>')
        updater.configure_object(xml, obj)
        self.assertEqual(1, obj.x)


    #-----------------------------------------------------------
    def test_configure_element_via_func_strip(self):
        class Sample(object):
            @property
            def x(self):
                return self._x

            @x.setter
            @fromXML(lambda elem: elem.text.strip(), convert_raw_xml=True)
            def x(self, value):
                self._x = value

        updater = XmlConfigUpdater()
        obj = Sample()
        xml = ET.fromstring('<data> <x> hello there! </x>  </data>')
        updater.configure_object(xml, obj)
        self.assertEqual("hello there!", obj.x)



    #============================================================================
    #   Multiple objects
    #============================================================================

    #-----------------------------------------------------------
    def test_configure_multiple_objects(self):
        updater = XmlConfigUpdater()
        a = SimpleSampleObject()
        b = SimpleSampleObject()
        xml = ET.fromstring("""
        <data>
            <a x="a"/>
            <b x="b"/>
        </data>
        """)
        updater.configure_objects(xml, {'a': a, 'b': b}, "")
        self.assertEqual('a', a.x)
        self.assertEqual('b', b.x)

    #-----------------------------------------------------------
    def test_object_missing(self):
        updater = XmlConfigUpdater()
        a = SimpleSampleObject()

        xml = ET.fromstring("""
        <data>
            <a x="a"/>
            <b x="b"/>
        </data>
        """)

        self.assertRaises(ttrk.BadFormatError, lambda: updater.configure_objects(xml, {'a': a}, ""))





if __name__ == '__main__':
    unittest.main()
