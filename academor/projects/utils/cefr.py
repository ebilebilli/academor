"""CEFR scale copy and the result offer rules for the level test pages (tests list and result)."""

from django.utils.translation import gettext as _

CEFR_LEVELS = ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')

# Results at or above this level get the IELTS-prep wording (button, WhatsApp message);
# every level gets the free trial lesson, the consultation and the test-takers' discount.
IELTS_READY_LEVEL = 'B2'
LEVEL_TEST_DISCOUNT_PERCENT = 25

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
    # result page: the level explained to the person who got it, and our advice for them
    about = {
        'A1': _('You are just starting to learn English. You understand simple words, everyday expressions and short sentences.'),
        'A2': _('You can talk in simple sentences about familiar topics such as your family, work, daily life and shopping.'),
        'B1': _('You can express yourself in everyday conversation, handle most situations while travelling and talk about your experiences and future plans.'),
        'B2': _('You speak English fairly freely, understand complex texts and can express your ideas in detail.'),
        'C1': _('You use English comfortably in study and work, understand long and complex texts and express your ideas clearly and in detail.'),
        'C2': _('You understand almost everything in English with ease, notice fine shades of meaning and express your ideas precisely.'),
    }
    advice = {
        'A1': _('Start learning English from scratch, build a solid foundation and take your first steps with us!'),
        'A2': _('Grow your vocabulary, develop your speaking skills and start communicating in English more comfortably!'),
        'B1': _('Make your speaking more fluent, broaden your vocabulary and express yourself in English with more confidence!'),
        'B2': _('Your English is a good base to start IELTS preparation. Now it is time to move towards your target band!'),
        'C1': _('Your English is at a high level. Prepare for your IELTS target and strengthen your knowledge with exam strategies!'),
        'C2': _('Your English is at a very high level. To reach your IELTS target, focus on exam techniques and your academic language skills!'),
    }
    return [
        {
            'code': code,
            'name': names[code],
            'description': descriptions[code],
            'about': about[code],
            'advice': advice[code],
            'step': index + 1,
            'is_current': code == current,
        }
        for index, code in enumerate(CEFR_LEVELS)
    ]


def level_test_takers_label(count):
    """Rounded-down taker count for the trust line, never below the floor."""
    return max(LEVEL_TEST_TAKERS_FLOOR, (count // 100) * 100)


def level_test_offer_track(level):
    """'ielts' when the result reaches IELTS_READY_LEVEL, 'foundation' below it, None for no level."""
    if level not in CEFR_LEVELS:
        return None
    return 'ielts' if CEFR_LEVELS.index(level) >= CEFR_LEVELS.index(IELTS_READY_LEVEL) else 'foundation'
