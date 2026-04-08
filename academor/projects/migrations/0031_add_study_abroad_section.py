from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0030_add_heroslide_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudyAbroadSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_az', models.TextField(blank=True, null=True, verbose_name='Text (AZ)')),
                ('text_en', models.TextField(blank=True, null=True, verbose_name='Text (EN)')),
                ('text_ru', models.TextField(blank=True, null=True, verbose_name='Text (RU)')),
            ],
            options={
                'verbose_name': 'Study Abroad Section Text',
                'verbose_name_plural': 'Study Abroad Section Text',
            },
        ),
    ]
