from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0068_about_show_on_homepage'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='gallery_order',
            field=models.PositiveIntegerField(
                db_index=True,
                default=0,
                help_text='About page strip gallery sort order (lower first). Only used for About media.',
                verbose_name='Gallery order',
            ),
        ),
        migrations.AddField(
            model_name='media',
            name='gallery_name_az',
            field=models.CharField(blank=True, max_length=120, verbose_name='Gallery name (AZ)'),
        ),
        migrations.AddField(
            model_name='media',
            name='gallery_name_en',
            field=models.CharField(blank=True, max_length=120, verbose_name='Gallery name (EN)'),
        ),
        migrations.AddField(
            model_name='media',
            name='gallery_name_ru',
            field=models.CharField(blank=True, max_length=120, verbose_name='Gallery name (RU)'),
        ),
        migrations.AddField(
            model_name='media',
            name='gallery_role_az',
            field=models.CharField(blank=True, max_length=160, verbose_name='Gallery role (AZ)'),
        ),
        migrations.AddField(
            model_name='media',
            name='gallery_role_en',
            field=models.CharField(blank=True, max_length=160, verbose_name='Gallery role (EN)'),
        ),
        migrations.AddField(
            model_name='media',
            name='gallery_role_ru',
            field=models.CharField(blank=True, max_length=160, verbose_name='Gallery role (RU)'),
        ),
        migrations.AddField(
            model_name='media',
            name='gallery_tag_az',
            field=models.CharField(blank=True, max_length=60, verbose_name='Gallery tag (AZ)'),
        ),
        migrations.AddField(
            model_name='media',
            name='gallery_tag_en',
            field=models.CharField(blank=True, max_length=60, verbose_name='Gallery tag (EN)'),
        ),
        migrations.AddField(
            model_name='media',
            name='gallery_tag_ru',
            field=models.CharField(blank=True, max_length=60, verbose_name='Gallery tag (RU)'),
        ),
        migrations.DeleteModel(
            name='AboutGalleryItem',
        ),
    ]
