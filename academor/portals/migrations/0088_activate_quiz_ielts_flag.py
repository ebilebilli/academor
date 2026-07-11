from django.db import migrations


IELTS_SERVICE = 'ielts'


def activate_ielts_quiz_flags(apps, schema_editor):
    Quiz = apps.get_model('portals', 'Quiz')
    Quiz.objects.filter(
        category__service=IELTS_SERVICE,
        is_ielts=False,
        is_sat=False,
    ).update(is_ielts=True)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0087_quiz_single_mock_program'),
    ]

    operations = [
        migrations.RunPython(activate_ielts_quiz_flags, migrations.RunPython.noop),
    ]
