from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0009_remove_mock_package'),
        ('portals', '0083_mock_test_program_sections'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MockTestPackage',
        ),
    ]
