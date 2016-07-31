#!/usr/bin/env python
import os
import sys


def read_environment():
    try:
        from environment import ENVIRONMENT
    except ImportError:
        return

    for variable, value in ENVIRONMENT.items():
        os.environ.setdefault(variable, str(value))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.management import execute_from_command_line

    read_environment()
    execute_from_command_line(sys.argv)
