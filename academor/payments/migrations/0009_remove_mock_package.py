from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0008_courseenrollment_mock_fields'),
        ('portals', '0083_mock_test_program_sections'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='courseenrollment',
            name='mock_package',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='mock_package',
        ),
    ]
