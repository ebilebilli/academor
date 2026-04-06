from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0017_servicehighlight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicehighlight',
            name='description_az',
            field=models.TextField(blank=True, max_length=186, null=True, verbose_name='Description (AZ)'),
        ),
        migrations.AlterField(
            model_name='servicehighlight',
            name='description_en',
            field=models.TextField(blank=True, max_length=186, null=True, verbose_name='Description (EN)'),
        ),
        migrations.AlterField(
            model_name='servicehighlight',
            name='description_ru',
            field=models.TextField(blank=True, max_length=186, null=True, verbose_name='Description (RU)'),
        ),
    ]
