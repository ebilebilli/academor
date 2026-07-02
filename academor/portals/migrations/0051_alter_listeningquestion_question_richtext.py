import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0050_remove_listeningaudio_time_and_review_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listeningquestion',
            name='question',
            field=ckeditor.fields.RichTextField(
                blank=True,
                help_text='Prompt shown to the student. Leave blank for a numbered answer line only.',
                verbose_name='Question',
            ),
        ),
    ]
