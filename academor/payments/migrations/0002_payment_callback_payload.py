from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='callback_up',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='callback_payload',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='payment',
            name='callback_received_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

