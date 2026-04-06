from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_remove_vacancy_and_job_application'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AcademyStatistic',
        ),
    ]
