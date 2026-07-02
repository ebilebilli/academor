from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0041_schedule_effective_from'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessoncategory',
            name='service',
            field=models.CharField(db_index=True, max_length=32, verbose_name='Service'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='subject',
            field=models.CharField(db_index=True, max_length=32, verbose_name='Service'),
        ),
        migrations.AlterField(
            model_name='quizcategory',
            name='service',
            field=models.CharField(db_index=True, max_length=32, verbose_name='Service'),
        ),
        migrations.AlterField(
            model_name='teachercoursespecialization',
            name='course_type',
            field=models.CharField(max_length=32, verbose_name='Course type'),
        ),
    ]
