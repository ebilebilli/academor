from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0084_media_sale'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='end_date',
            field=models.DateField(
                blank=True,
                help_text='Optional. Promotion is hidden from the homepage after this date.',
                null=True,
                verbose_name='End date',
            ),
        ),
        migrations.AddField(
            model_name='sale',
            name='old_price',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Optional. Shown on the homepage promotion banner with the discounted price.',
                max_digits=12,
                null=True,
                verbose_name='Original price (AZN)',
            ),
        ),
    ]
