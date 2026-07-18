from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0095_alter_quizcategory_services'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentcoursespecialization',
            name='course_type',
            field=models.CharField(max_length=255, verbose_name='Service'),
        ),
        migrations.AlterField(
            model_name='teachercoursespecialization',
            name='course_type',
            field=models.CharField(max_length=255, verbose_name='Course type'),
        ),
        migrations.AlterField(
            model_name='lessoncategory',
            name='service',
            field=models.CharField(db_index=True, max_length=255, verbose_name='Service'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='subject',
            field=models.CharField(db_index=True, max_length=255, verbose_name='Service'),
        ),
    ]
