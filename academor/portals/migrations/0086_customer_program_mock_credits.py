from django.db import migrations, models


def migrate_mock_credits_to_ielts(apps, schema_editor):
    CustomerProfile = apps.get_model('portals', 'CustomerProfile')
    for profile in CustomerProfile.objects.all().only('pk', 'mock_credits'):
        CustomerProfile.objects.filter(pk=profile.pk).update(
            ielts_mock_credits=profile.mock_credits or 0,
            sat_mock_credits=0,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0085_alter_quiz_is_math_alter_studentmockaccess_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerprofile',
            name='ielts_mock_credits',
            field=models.PositiveIntegerField(
                default=0,
                help_text='One credit is consumed when the customer starts an IELTS mock test.',
                verbose_name='IELTS mock credits',
            ),
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='sat_mock_credits',
            field=models.PositiveIntegerField(
                default=0,
                help_text='One credit is consumed when the customer starts a SAT mock test.',
                verbose_name='SAT mock credits',
            ),
        ),
        migrations.RunPython(migrate_mock_credits_to_ielts, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='customerprofile',
            name='mock_credits',
        ),
    ]
