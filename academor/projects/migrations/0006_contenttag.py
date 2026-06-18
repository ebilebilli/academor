# Generated manually for ContentTag + M2M tags on blog/services

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_blogpost_video_cover'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, db_index=True, max_length=255, unique=True, verbose_name='Slug')),
                ('name_az', models.CharField(max_length=100, verbose_name='Name (AZ)')),
                ('name_en', models.CharField(blank=True, max_length=100, verbose_name='Name (EN)')),
                ('name_ru', models.CharField(blank=True, max_length=100, verbose_name='Name (RU)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Order')),
            ],
            options={
                'verbose_name': 'Content tag',
                'verbose_name_plural': 'Content tags',
                'ordering': ('order', 'name_az', 'id'),
            },
        ),
        migrations.AddField(
            model_name='blogpost',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='blog_posts', to='projects.contenttag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='service',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='services', to='projects.contenttag', verbose_name='Tags'),
        ),
    ]
