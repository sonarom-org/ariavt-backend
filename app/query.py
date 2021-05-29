#!/usr/bin/python3

from typing import Any, List

from icecream import ic

from psycopg2.extensions import cursor

from .database_connection import connection


class Query:

    def __init__(self):
        self.query = None

    def run_query(self):

        # create a cursor for the query
        with connection.get_cursor() as query_cursor:

            query_cursor.execute(self.query)

            results = self.fetch_results(query_cursor)

        return results

    def fetch_results(self, query_cursor: cursor) -> Any:
        raise NotImplemented


class SelectAll(Query):

    def __init__(self, table: str):
        super().__init__()
        self.query = 'SELECT * FROM {}'.format(table)

    def fetch_results(self, query_cursor: cursor):
        results = query_cursor.fetchall()
        return results


class Insert(Query):

    def __init__(self, table: str, columns: List[str], values: List[str]):
        super().__init__()

        # Build columns string
        columns_str = ', '.join(map(str, columns))
        # Build values string
        values_str = str(values)[1:-1]

        ic(columns_str, values_str)

        query_template = """INSERT INTO {} ({}) VALUES ({});"""

        self.query = query_template.format(table, columns_str, values_str)

    def fetch_results(self, query_cursor: cursor):
        connection.commit()
        return True

