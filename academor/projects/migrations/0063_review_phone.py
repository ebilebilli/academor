from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0062_servicecategory_instructors_m2m'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='phone',
            field=models.CharField(
                default='',
                max_length=30,
                verbose_name='Mobile number',
            ),
        ),
    ]
