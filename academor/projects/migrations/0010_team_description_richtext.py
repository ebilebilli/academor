import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_team_descriptor_and_description_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='description',
            field=ckeditor.fields.RichTextField(
                blank=True,
                null=True,
                verbose_name='Description',
            ),
        ),
    ]
