
import unittest

from app.query import SelectAll, Insert


class TestQuery(unittest.TestCase):

    def test_select_all(self):
        # Select all
        query = SelectAll()
        results = query.run_query(table='images')
        print(results)

    def test_insert(self):
        # Insert
        query = Insert()
        results = query.run_query(table='images',
                                  columns=['relative_path'],
                                  values=['sample_img'])
        print(results)
