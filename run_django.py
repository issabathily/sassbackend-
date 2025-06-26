import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sassbackend.settings')

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000', '--noreload']) 