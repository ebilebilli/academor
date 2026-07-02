from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0046_quizquestion_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListeningAudio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Order')),
                ('title', models.CharField(blank=True, help_text='Short label, e.g. Section 1.', max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, help_text='Instructions or context shown with the audio.', verbose_name='Description')),
                ('audio_file', models.FileField(blank=True, null=True, upload_to='portals/listening/audio/', verbose_name='Audio file')),
                ('audio_url', models.URLField(blank=True, help_text='Optional external audio link instead of an uploaded file.', verbose_name='Audio URL')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listening_audios', to='portals.quizcategory', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Listening audio',
                'verbose_name_plural': 'Listening audio clips',
                'ordering': ('order', 'id'),
            },
        ),
        migrations.CreateModel(
            name='ListeningQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Order')),
                ('question', models.TextField(blank=True, help_text='Prompt shown to the student. Leave blank for a numbered answer line only.', verbose_name='Question')),
                ('audio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='portals.listeningaudio', verbose_name='Audio section')),
            ],
            options={
                'verbose_name': 'Listening question',
                'verbose_name_plural': 'Listening questions',
                'ordering': ('order', 'id'),
            },
        ),
    ]
