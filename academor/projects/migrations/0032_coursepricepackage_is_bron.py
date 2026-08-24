from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0031_mocktestresult_program_i18n'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursepricepackage',
            name='is_bron',
            field=models.BooleanField(
                default=False,
                help_text='If enabled, checkout shows the bron agreement instead of the standard training agreement.',
                verbose_name='Bron contract',
            ),
        ),
    ]
