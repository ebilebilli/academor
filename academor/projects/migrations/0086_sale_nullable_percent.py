import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0085_sale_end_date_old_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='percent',
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text='Optional. Leave empty for a general promotion or event without a discount.',
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100),
                ],
                verbose_name='Discount (%)',
            ),
        ),
    ]
