from django.db import migrations


MATCHING_TYPES = {
    'matching_headings',
    'matching_info',
    'matching_features',
    'matching_sentence_endings',
}


def normalize_group_option_pools(apps, schema_editor):
    ReadingQuestionGroup = apps.get_model('portals', 'ReadingQuestionGroup')
    for group in ReadingQuestionGroup.objects.all():
        if group.question_type in MATCHING_TYPES:
            options = [str(item).strip() for item in (group.option_pool or []) if str(item).strip()]
            if len(options) < 2:
                group.option_pool = []
            else:
                group.option_pool = options
            group.save(update_fields=['option_pool'])
        else:
            group.option_pool = []
            group.save(update_fields=['option_pool'])


def reverse_noop(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ('portals', '0096_widen_portal_service_keys'),
    ]

    operations = [
        migrations.RunPython(normalize_group_option_pools, reverse_noop),
    ]
