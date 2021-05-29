
import unittest

from app.query import SelectAll, Insert


class TestQuery(unittest.TestCase):

    def test_select_all(self):
        # Select all
        results = SelectAll(table='images').run_query()
        print(results)

    def test_insert(self):
        # Insert
        results = Insert(table='images',
                         columns=['relative_path'],
                         values=['sample_img']).run_query()
        print(results)
