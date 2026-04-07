from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_contactinquiry_mobile_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag', models.ImageField(upload_to='universities/', verbose_name='Flag image')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'University',
                'verbose_name_plural': 'Universities',
                'ordering': ('id',),
            },
        ),
    ]
