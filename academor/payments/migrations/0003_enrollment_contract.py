from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_payment_buyer_email_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='contract_number',
            field=models.CharField(
                blank=True,
                max_length=32,
                verbose_name='Training agreement number',
            ),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='contract_number',
            field=models.CharField(
                blank=True,
                max_length=32,
                verbose_name='Training agreement number',
            ),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='contract_html',
            field=models.TextField(
                blank=True,
                verbose_name='Training agreement',
            ),
        ),
    ]
