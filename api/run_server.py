#!/usr/bin/env python
import os
from psycopg2 import connect, OperationalError
from time import sleep
from django.core.management import ManagementUtility


def database_available():
    try:
        connect(os.environ['DATABASE_URL'])
        return True
    except OperationalError:
        return False

if __name__ == "__main__":
    while not database_available():
        print('Database is unavailable - Sleeping')
        sleep(2)

    print('Database is available - Starting Django Server')
    ManagementUtility(['django', 'migrate']).execute()
    ManagementUtility(['staticfiles', 'runserver', '0.0.0.0:8000']).execute()
