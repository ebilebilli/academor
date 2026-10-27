"""CEFR scale copy and per-level stickers for the level test pages (tests list and result)."""

from django.utils.translation import gettext as _

CEFR_LEVELS = ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')

# Shown as "1000+" on the tests page until the real count passes it.
LEVEL_TEST_TAKERS_FLOOR = 1000

# Result sticker per level: English slang on purpose (it is an English school), the hand is a
# halftone cut-out from assets/img/level-test/stickers/, tone picks the sticker colour.
LEVEL_STICKERS = {
    'A1': {'title': 'NEW ERA', 'tag': 'english unlocked', 'hand': 'point', 'tone': 'orange'},
    'A2': {'title': 'LOADING...', 'tag': 'level up in progress', 'hand': 'one', 'tone': 'orange'},
    'B1': {'title': 'MAIN CHARACTER', 'tag': 'B1 energy', 'hand': 'peace', 'tone': 'teal'},
    'B2': {'title': 'FLUENT-ISH', 'tag': 'no cap', 'hand': 'thumbs', 'tone': 'teal'},
    'C1': {'title': 'BIG BRAIN', 'tag': 'basically fluent', 'hand': 'ok', 'tone': 'dark'},
    'C2': {'title': 'FINAL BOSS', 'tag': 'english: mastered', 'hand': 'fist', 'tone': 'dark'},
}


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
            'sticker': LEVEL_STICKERS[code],
        }
        for index, code in enumerate(CEFR_LEVELS)
    ]


def level_test_takers_label(count):
    """Rounded-down taker count for the trust line, never below the floor."""
    return max(LEVEL_TEST_TAKERS_FLOOR, (count // 100) * 100)
