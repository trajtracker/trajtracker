import unittest

import trajtracker as ttrk
from trajtracker.data import CSVLoader


class DbgCSVLoader(CSVLoader):

    def __init__(self, fieldnames, data, case_sensitive_col_names=False):
        super(DbgCSVLoader, self).__init__(case_sensitive_col_names)
        self._data = data
        self._fieldnames = fieldnames

    def _read_data_from_file(self, filename):
        return self._data, self._fieldnames



class CSVLoaderTests(unittest.TestCase):

    def test_convert_to_type(self):

        loader = DbgCSVLoader(['a', 'b'], [{'a':'1', 'b':'2'}, {'a':'10', 'b':'20'}])
        loader.add_field('b', int)

        data = loader.load_file('xxx')

        self.assertEqual('1', data[0]['a'])
        self.assertEqual('10', data[1]['a'])

        self.assertEqual(2, data[0]['b'])
        self.assertEqual(20, data[1]['b'])


    def test_convert_to_func(self):
        loader = DbgCSVLoader(['a', 'b'], [{'a': '1', 'b': '2'}, {'a': '10', 'b': '20'}])
        loader.add_field('b', lambda x: int(x)+1)

        data = loader.load_file('xxx')

        self.assertEqual('1', data[0]['a'])
        self.assertEqual('10', data[1]['a'])

        self.assertEqual(3, data[0]['b'])
        self.assertEqual(21, data[1]['b'])


    def test_mandatory(self):
        loader = DbgCSVLoader(['a', 'b'], [{'a': '1', 'b': '2'}])
        loader.add_field('c', optional=True)
        loader.load_file('xxx')

        loader.add_field('c', optional=False)
        self.assertRaises(ttrk.BadFormatError, lambda: loader.load_file('xxx'))


if __name__ == '__main__':
    unittest.main()
