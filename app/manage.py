#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DB_HOST', 'localhost')
    os.environ.setdefault('DB_NAME', 'social_app_db')
    os.environ.setdefault('DB_USER', 'postgres')
    os.environ.setdefault('DB_PASS', 'maen_1234')
    os.environ.setdefault('PORT', '5432')
    os.environ.setdefault('DEBUG', 'False')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.production_settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
