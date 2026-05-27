from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(db_index=True, max_length=64, unique=True)),
                ('client_order_id', models.CharField(blank=True, db_index=True, max_length=64)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(default='AZN', max_length=3)),
                ('status', models.CharField(choices=[('pending', 'Gözləyir'), ('success', 'Uğurlu'), ('cancelled', 'Ləğv'), ('declined', 'Rədd'), ('failed', 'Uğursuz')], db_index=True, default='pending', max_length=20)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
