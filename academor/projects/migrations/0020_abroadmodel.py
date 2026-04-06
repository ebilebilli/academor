from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0019_merge_0018_conflict'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbroadModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Name')),
                ('img', models.ImageField(upload_to='abroad/', verbose_name='Image')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
            ],
            options={
                'verbose_name': 'Abroad item',
                'verbose_name_plural': 'Abroad items',
                'ordering': ('id',),
            },
        ),
    ]
