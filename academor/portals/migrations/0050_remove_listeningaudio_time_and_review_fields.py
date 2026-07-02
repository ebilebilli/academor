from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0049_listening_audio_quiz_fk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listeningaudio',
            name='is_time_limited',
        ),
        migrations.RemoveField(
            model_name='listeningaudio',
            name='requires_manual_review',
        ),
        migrations.RemoveField(
            model_name='listeningaudio',
            name='time_limit_minutes',
        ),
    ]
