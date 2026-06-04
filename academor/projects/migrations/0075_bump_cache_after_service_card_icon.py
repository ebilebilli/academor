"""Invalidate versioned query/page cache after card_icon field is deployed."""

from django.db import migrations


def bump_service_category_display_cache(apps, schema_editor):
    from projects.utils.cache_utils import invalidate_model_cache

    invalidate_model_cache('ServiceCategory')


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0074_alter_coursepricepackage_lesson_minutes'),
    ]

    operations = [
        migrations.RunPython(
            bump_service_category_display_cache,
            migrations.RunPython.noop,
        ),
    ]
