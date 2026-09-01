from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0032_coursepricepackage_is_bron'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='is_test_take_poster_image',
            field=models.BooleanField(
                default=False,
                help_text='Responsive advertising poster shown on individual test pages (/tests/<id>/).',
                verbose_name='Test take page ad poster',
            ),
        ),
    ]
