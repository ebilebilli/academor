from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_tagline_text_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursepricepackage',
            name='show_on_homepage',
            field=models.BooleanField(
                default=False,
                help_text='If enabled, this package appears in the homepage "Most in demand" price carousel.',
                verbose_name='Show on homepage',
            ),
        ),
    ]
