from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0054_alter_listeningquestion_question'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListeningAudioPlay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempt_key', models.CharField(help_text='Portal session value identifying the active quiz attempt.', max_length=64, verbose_name='Attempt key')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='Started at')),
                ('listening_audio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plays', to='portals.listeningaudio', verbose_name='Listening audio')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listening_audio_plays', to='portals.quiz', verbose_name='Quiz')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listening_audio_plays', to='portals.studentprofile', verbose_name='Student')),
            ],
            options={
                'verbose_name': 'Listening audio play',
                'verbose_name_plural': 'Listening audio plays',
                'indexes': [models.Index(fields=['student', 'quiz', 'attempt_key'], name='portals_lis_student_6f0f0d_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='listeningaudioplay',
            constraint=models.UniqueConstraint(fields=('student', 'quiz', 'listening_audio', 'attempt_key'), name='portals_listening_audio_play_unique_attempt'),
        ),
    ]
