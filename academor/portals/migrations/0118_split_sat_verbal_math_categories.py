# Split SAT Verbal / SAT Math quiz categories and enrollments.

from django.db import migrations


def forwards(apps, schema_editor):
    # Nothing to split on a fresh database. Returning early also keeps this migration working
    # there: the helpers below use the live Service model, whose later fields (added by newer
    # projects migrations) do not exist yet at this point of a from-scratch migrate.
    QuizCategory = apps.get_model('portals', 'QuizCategory')
    StudentCourseSpecialization = apps.get_model('portals', 'StudentCourseSpecialization')
    if not QuizCategory.objects.exists() and not StudentCourseSpecialization.objects.exists():
        return

    from portals.utils.quiz_category_services import (
        expand_generic_exam_track_enrollments,
        relink_sat_math_and_verbal_categories,
    )

    relink_sat_math_and_verbal_categories()
    expand_generic_exam_track_enrollments()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0117_quizcategory_parent'),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
