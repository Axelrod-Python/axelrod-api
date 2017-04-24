"""
import all default settings and then over write any settings
that are specific to testing

"""
import sys

from api.config.settings import *


if 'test' in sys.argv or 'test_coverage' in sys.argv:

    # use an in memory sqlite3 backend for performance
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'default',
        },
    }
