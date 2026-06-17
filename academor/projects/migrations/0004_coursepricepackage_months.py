from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_sale_show_on_homepage_fixup'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursepricepackage',
            name='months',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Course length in months (used in the training agreement).',
                null=True,
                verbose_name='Months',
            ),
        ),
    ]
