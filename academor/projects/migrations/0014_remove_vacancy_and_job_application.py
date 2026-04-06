from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_remove_service_program_expand_category'),
    ]

    operations = [
        migrations.DeleteModel(
            name='JobApplication',
        ),
        migrations.RemoveField(
            model_name='media',
            name='vacancy',
        ),
        migrations.DeleteModel(
            name='CareerOpening',
        ),
        migrations.RemoveField(
            model_name='media',
            name='is_vacany_page_background_image',
        ),
    ]
