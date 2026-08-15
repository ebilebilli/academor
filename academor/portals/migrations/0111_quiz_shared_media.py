from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0110_listening_question_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='shared_audio_file',
            field=models.FileField(
                blank=True,
                help_text='Optional audio shown with the shared passage.',
                null=True,
                upload_to='portals/quiz/shared-media/',
                verbose_name='Shared audio file',
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='shared_youtube_url',
            field=models.URLField(
                blank=True,
                help_text='Optional YouTube video shown with the shared passage.',
                verbose_name='Shared YouTube URL',
            ),
        ),
    ]
