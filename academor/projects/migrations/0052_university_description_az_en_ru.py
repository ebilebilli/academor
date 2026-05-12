import ckeditor.fields
from django.db import migrations


def copy_description_to_az(apps, schema_editor):
    University = apps.get_model('projects', 'University')
    for row in University.objects.all().iterator():
        legacy = getattr(row, 'description', None) or ''
        if str(legacy).strip():
            University.objects.filter(pk=row.pk).update(description_az=legacy)


def copy_az_to_legacy_description(apps, schema_editor):
    University = apps.get_model('projects', 'University')
    for row in University.objects.all().iterator():
        az = getattr(row, 'description_az', None) or ''
        if str(az).strip():
            University.objects.filter(pk=row.pk).update(description=az)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0051_team_description_az_en_ru'),
    ]

    operations = [
        migrations.AddField(
            model_name='university',
            name='description_az',
            field=ckeditor.fields.RichTextField(
                blank=True,
                null=True,
                verbose_name='Description (AZ)',
            ),
        ),
        migrations.AddField(
            model_name='university',
            name='description_en',
            field=ckeditor.fields.RichTextField(
                blank=True,
                null=True,
                verbose_name='Description (EN)',
            ),
        ),
        migrations.AddField(
            model_name='university',
            name='description_ru',
            field=ckeditor.fields.RichTextField(
                blank=True,
                null=True,
                verbose_name='Description (RU)',
            ),
        ),
        migrations.RunPython(copy_description_to_az, copy_az_to_legacy_description),
        migrations.RemoveField(
            model_name='university',
            name='description',
        ),
    ]
