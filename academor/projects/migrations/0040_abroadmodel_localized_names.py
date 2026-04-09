# Generated manually for localized AbroadModel names

from django.db import migrations, models


def copy_name_to_localized(apps, schema_editor):
    AbroadModel = apps.get_model('projects', 'AbroadModel')
    for row in AbroadModel.objects.all():
        n = (getattr(row, 'name', None) or '').strip()
        if n:
            row.name_az = n
            row.name_en = n
            row.name_ru = n
            row.save(update_fields=['name_az', 'name_en', 'name_ru'])


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0039_media_is_abroad_page_background_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='abroadmodel',
            name='name_az',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name='Name (AZ)'),
        ),
        migrations.AddField(
            model_name='abroadmodel',
            name='name_en',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name='Name (EN)'),
        ),
        migrations.AddField(
            model_name='abroadmodel',
            name='name_ru',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name='Name (RU)'),
        ),
        migrations.RunPython(copy_name_to_localized, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='abroadmodel',
            name='name',
        ),
    ]
