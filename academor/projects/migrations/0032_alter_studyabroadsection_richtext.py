from django.db import migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0031_add_study_abroad_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studyabroadsection',
            name='text_az',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Text (AZ)'),
        ),
        migrations.AlterField(
            model_name='studyabroadsection',
            name='text_en',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Text (EN)'),
        ),
        migrations.AlterField(
            model_name='studyabroadsection',
            name='text_ru',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Text (RU)'),
        ),
    ]
