import ckeditor.fields
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0012_about_only_richtext_descriptions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='project',
        ),
        migrations.RemoveField(
            model_name='media',
            name='service',
        ),
        migrations.DeleteModel(
            name='Service',
        ),
        migrations.DeleteModel(
            name='Program',
        ),
        migrations.AddField(
            model_name='servicecategory',
            name='description_en',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Description (EN)'),
        ),
        migrations.AddField(
            model_name='servicecategory',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Active'),
        ),
        migrations.AddField(
            model_name='servicecategory',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Created at',
            ),
            preserve_default=False,
        ),
    ]
