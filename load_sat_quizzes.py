"""Load SAT quiz JSON files into the database (local helper).

Prefer the management command on deploy:

    python academor/manage.py load_sat_quiz_resources
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'academor'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academor.settings')

import django

django.setup()

from django.core.management import call_command


if __name__ == '__main__':
    call_command('load_sat_quiz_resources', *sys.argv[1:])
