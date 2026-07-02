import json

from django.db import migrations, models


def forwards(apps, schema_editor):
    QuizQuestion = apps.get_model('portals', 'QuizQuestion')
    for question in QuizQuestion.objects.all().iterator():
        media_type = getattr(question, 'media_type', 'none') or 'none'
        if media_type == 'image':
            question.prompt_type = 'image'
        elif media_type == 'video':
            question.prompt_type = 'video'
        else:
            question.prompt_type = 'text'

        options = question.answer_options or []
        if not isinstance(options, list):
            options = []
        options = [str(item).strip() for item in options if str(item).strip()]
        question.answer_options = options

        correct = (question.correct_answer or '').strip()
        if correct and correct in options:
            question.correct_option_index = options.index(correct)
        elif options:
            question.correct_option_index = 0
        else:
            question.correct_option_index = 0

        question.save(update_fields=[
            'prompt_type',
            'answer_options',
            'correct_option_index',
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0012_remove_quiz_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizquestion',
            name='prompt_type',
            field=models.CharField(
                choices=[
                    ('text', 'Text'),
                    ('image', 'Image'),
                    ('video', 'Video'),
                    ('audio', 'Audio'),
                ],
                default='text',
                max_length=16,
                verbose_name='Question type',
            ),
        ),
        migrations.AddField(
            model_name='quizquestion',
            name='media_file',
            field=models.FileField(
                blank=True,
                help_text='Upload image, video, or audio when the question type is not text.',
                null=True,
                upload_to='portals/quiz/media/',
                verbose_name='Media file',
            ),
        ),
        migrations.AddField(
            model_name='quizquestion',
            name='correct_option_index',
            field=models.PositiveIntegerField(default=0, verbose_name='Correct option index'),
        ),
        migrations.AlterField(
            model_name='quizquestion',
            name='question',
            field=models.TextField(
                blank=True,
                help_text='Written question or caption shown with image / video / audio.',
                verbose_name='Question text',
            ),
        ),
        migrations.AlterField(
            model_name='quizquestion',
            name='correct_answer',
            field=models.CharField(blank=True, max_length=500, verbose_name='Correct answer'),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='quizquestion',
            name='media_type',
        ),
    ]
