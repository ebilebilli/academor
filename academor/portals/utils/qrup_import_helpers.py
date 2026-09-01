"""Shared helpers for Qrup Excel → portal import (JSON + management command)."""

IELTS_COURSE_SLUGS = ('ielts-course', 'ielts')
IELTS_COURSE_NAMES = ('ielts course',)

ENGLISH_LANGUAGE_COURSE_SLUGS = (
    'english-language-course',
    'english-language',
    'general-english',
)
ENGLISH_LANGUAGE_COURSE_NAMES = ('english language course', 'english language')

IELTS_DEFAULT_ENROLLMENT_SLUGS = IELTS_COURSE_SLUGS + ENGLISH_LANGUAGE_COURSE_SLUGS


def normalize_course_slug(slug):
    slug = (slug or '').strip().lower()
    if slug in ('foundation-ielts', 'foundation_ielts'):
        return 'ielts'
    return slug


def is_ielts_track(subject='', course_slug=''):
    subject_l = (subject or '').strip().lower()
    slug = normalize_course_slug(course_slug)
    if slug == 'ielts' or 'ielts' in slug:
        return True
    return subject_l in ('ielts', 'foundation ielts') or 'ielts' in subject_l


def student_course_enrollment_slugs(subject='', course_slug=''):
    slug = normalize_course_slug(course_slug or subject)
    if is_ielts_track(subject, slug):
        return list(IELTS_DEFAULT_ENROLLMENT_SLUGS)
    if slug:
        return [slug]
    return []
