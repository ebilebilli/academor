from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_servicecategory_description_az_ru'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceHighlight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_az', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title (AZ)')),
                ('title_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title (EN)')),
                ('title_ru', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title (RU)')),
                ('description_az', models.TextField(blank=True, null=True, verbose_name='Description (AZ)')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description (EN)')),
                ('description_ru', models.TextField(blank=True, null=True, verbose_name='Description (RU)')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Order')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
            ],
            options={
                'verbose_name': 'Service highlight',
                'verbose_name_plural': 'Service highlights',
                'ordering': ('order', 'id'),
            },
        ),
    ]
