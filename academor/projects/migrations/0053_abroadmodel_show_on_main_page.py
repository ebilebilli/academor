from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0052_university_description_az_en_ru'),
    ]

    operations = [
        migrations.AddField(
            model_name='abroadmodel',
            name='show_on_main_page',
            field=models.BooleanField(
                default=True,
                help_text='If enabled, this country and its linked universities appear in the study-abroad block on the homepage.',
                verbose_name='Show on home page',
            ),
        ),
    ]
