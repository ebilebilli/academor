import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0054_servicecategory_show_on_main_page'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, db_index=True, max_length=255, unique=True, verbose_name='Slug')),
                ('name_az', models.CharField(max_length=200, verbose_name='Name (AZ)')),
                ('name_en', models.CharField(blank=True, max_length=200, verbose_name='Name (EN)')),
                ('name_ru', models.CharField(blank=True, max_length=200, verbose_name='Name (RU)')),
                ('description_az', ckeditor.fields.RichTextField(blank=True, verbose_name='Description (AZ)')),
                ('description_en', ckeditor.fields.RichTextField(blank=True, verbose_name='Description (EN)')),
                ('description_ru', ckeditor.fields.RichTextField(blank=True, verbose_name='Description (RU)')),
                ('date', models.DateField(blank=True, help_text='Display date (set manually).', null=True, verbose_name='Date')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('on_top', models.BooleanField(default=False, help_text='Pinned posts appear first on the blog list.', verbose_name='On top')),
                ('on_main_page', models.BooleanField(default=False, help_text='Show this post on the homepage when active.', verbose_name='On main page')),
            ],
            options={
                'verbose_name': 'Blog post',
                'verbose_name_plural': 'Blog',
                'ordering': ('-on_top', '-date', '-id'),
            },
        ),
    ]
