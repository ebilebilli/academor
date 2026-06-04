from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_payment_buyer_email_payment_buyer_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='buyer_phone',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='buyer_phone',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
