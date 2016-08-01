#!/usr/bin/env python
import sys
from psycopg2 import connect, OperationalError
from time import sleep


def database_available():
    try:
        connect("host=db dbname=postgres user=postgres")
        return True
    except OperationalError:
        return False

if __name__ == "__main__":
    while not database_available():
        print('Database is unavailable - Sleeping')
        sleep(2)

    print('Database is available - Starting Django Server')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
