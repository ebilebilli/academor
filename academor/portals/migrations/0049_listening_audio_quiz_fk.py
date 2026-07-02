from django.db import migrations, models
import django.db.models.deletion


def assign_listening_audios_to_quizzes(apps, schema_editor):
    ListeningAudio = apps.get_model('portals', 'ListeningAudio')
    Quiz = apps.get_model('portals', 'Quiz')

    for audio in ListeningAudio.objects.filter(quiz__isnull=True).iterator():
        quiz = (
            Quiz.objects.filter(category_id=audio.category_id, is_listening=True)
            .order_by('id')
            .first()
        )
        if quiz is None:
            quiz = (
                Quiz.objects.filter(category_id=audio.category_id)
                .order_by('id')
                .first()
            )
        if quiz is not None:
            audio.quiz_id = quiz.pk
            audio.save(update_fields=['quiz_id'])

    ListeningAudio.objects.filter(quiz__isnull=True).delete()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0048_remove_quizquestion_parent_listening_time_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='listeningaudio',
            name='quiz',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='listening_audios',
                to='portals.quiz',
                verbose_name='Quiz',
            ),
        ),
        migrations.RunPython(assign_listening_audios_to_quizzes, noop),
        migrations.RemoveField(
            model_name='listeningaudio',
            name='category',
        ),
        migrations.AlterField(
            model_name='listeningaudio',
            name='quiz',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='listening_audios',
                to='portals.quiz',
                verbose_name='Quiz',
            ),
        ),
    ]
