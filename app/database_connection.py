#!/usr/bin/python3

import psycopg2
from psycopg2.extensions import cursor

from .config import database as database_config


class PostgreSQLConnection:
    """ PostgreSQL Connection. """

    def __init__(self, config):
        self._connect(config)

    def _connect(self, database):
        """ Connect to the PostgreSQL database server. """
        conn = None
        try:

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')

            conn = psycopg2.connect(
                host=database["host"],
                database=database["database"],
                user=database["user"],
                password=database["password"],
                port=database["port"])

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        self.connection = conn

    def disconnect(self):
        """ Disconnect to the PostgreSQL database server. """

        print('Disconnecting from the PostgreSQL database server...')

        if self.connection is not None:
            self.connection.close()
            print('Database connection closed.')

    def get_cursor(self) -> cursor:
        """ Creates and returns a cursor for a certain connection. """
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()


# Singleton
connection = PostgreSQLConnection(database_config)
