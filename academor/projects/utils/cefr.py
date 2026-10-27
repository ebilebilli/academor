"""CEFR scale copy for the level test pages (tests list and result)."""

from django.utils.translation import gettext as _

from projects.models.service_models import CEFR_LEVELS

# Shown as "1000+" on the tests page until the real count passes it.
LEVEL_TEST_TAKERS_FLOOR = 1000


def cefr_scale(current=None):
    names = {
        'A1': _('Beginner'),
        'A2': _('Elementary'),
        'B1': _('Intermediate'),
        'B2': _('Upper-Intermediate'),
        'C1': _('Advanced'),
        'C2': _('Proficiency'),
    }
    descriptions = {
        'A1': _('Understands and uses everyday expressions and very basic phrases.'),
        'A2': _('Talks about familiar topics such as shopping, family and work in simple terms.'),
        'B1': _('Handles most travel situations and describes experiences and plans.'),
        'B2': _('Speaks fluently with native speakers and follows complex texts.'),
        'C1': _('Uses English flexibly for study and work; understands long, demanding texts.'),
        'C2': _('Understands virtually everything and expresses ideas precisely.'),
    }
    return [
        {
            'code': code,
            'name': names[code],
            'description': descriptions[code],
            'step': index + 1,
            'is_current': code == current,
        }
        for index, code in enumerate(CEFR_LEVELS)
    ]


def level_test_takers_label(count):
    """Rounded-down taker count for the trust line, never below the floor."""
    return max(LEVEL_TEST_TAKERS_FLOOR, (count // 100) * 100)
