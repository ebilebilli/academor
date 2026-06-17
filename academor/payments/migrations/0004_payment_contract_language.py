from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_enrollment_contract'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='contract_language',
            field=models.CharField(
                blank=True,
                default='az',
                max_length=2,
                verbose_name='Contract language',
            ),
        ),
    ]
