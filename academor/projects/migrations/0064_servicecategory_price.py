from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0063_review_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecategory',
            name='price',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Course fee in AZN. Leave empty to hide the pay button.',
                null=True,
                verbose_name='Price (AZN)',
            ),
        ),
    ]
