import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0062_textbook_group_lesson_attachments'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpeakingPart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_type', models.CharField(
                    choices=[
                        ('part_1', 'Part 1 — Introduction & interview'),
                        ('part_2', 'Part 2 — Individual long turn'),
                        ('part_3', 'Part 3 — Two-way discussion'),
                    ],
                    max_length=16,
                    verbose_name='Part',
                )),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Order')),
                ('title', models.CharField(
                    blank=True,
                    help_text='Optional label shown to the student.',
                    max_length=255,
                    verbose_name='Title',
                )),
                ('instructions', ckeditor.fields.RichTextField(
                    blank=True,
                    help_text='Official-style task instructions for this part.',
                    verbose_name='Instructions',
                )),
                ('cue_card_topic', ckeditor.fields.RichTextField(
                    blank=True,
                    help_text='Part 2 only — main topic line on the cue card.',
                    verbose_name='Cue card topic',
                )),
                ('cue_card_bullets', models.JSONField(
                    blank=True,
                    default=list,
                    help_text='Part 2 only — "You should say" bullet list.',
                    verbose_name='Cue card bullet points',
                )),
                ('preparation_seconds', models.PositiveIntegerField(
                    blank=True,
                    help_text='Leave blank to use the IELTS default for this part.',
                    null=True,
                    verbose_name='Preparation time (seconds)',
                )),
                ('default_answer_seconds', models.PositiveIntegerField(
                    blank=True,
                    help_text='Per-question recording limit when a question has no override.',
                    null=True,
                    verbose_name='Default answer time (seconds)',
                )),
                ('quiz', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='speaking_parts',
                    to='portals.quiz',
                    verbose_name='Quiz',
                )),
            ],
            options={
                'verbose_name': 'Speaking part',
                'verbose_name_plural': 'Speaking parts',
                'ordering': ('order', 'id'),
            },
        ),
        migrations.CreateModel(
            name='SpeakingQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Order')),
                ('question', ckeditor.fields.RichTextField(
                    blank=True,
                    help_text='Examiner question. Leave blank for Part 2 when the cue card is the prompt.',
                    verbose_name='Question',
                )),
                ('preparation_seconds', models.PositiveIntegerField(
                    blank=True,
                    help_text='Override part default. Part 2 uses this before the long-turn recording.',
                    null=True,
                    verbose_name='Preparation time (seconds)',
                )),
                ('answer_seconds', models.PositiveIntegerField(
                    blank=True,
                    help_text='Maximum recording length for this question.',
                    null=True,
                    verbose_name='Answer time (seconds)',
                )),
                ('part', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='questions',
                    to='portals.speakingpart',
                    verbose_name='Part',
                )),
            ],
            options={
                'verbose_name': 'Speaking question',
                'verbose_name_plural': 'Speaking questions',
                'ordering': ('order', 'id'),
            },
        ),
        migrations.CreateModel(
            name='SpeakingRecording',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio_file', models.FileField(
                    upload_to='portals/speaking/recordings/%Y/%m/',
                    verbose_name='Audio recording',
                )),
                ('duration_sec', models.PositiveIntegerField(default=0, verbose_name='Duration (seconds)')),
                ('question', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='recordings',
                    to='portals.speakingquestion',
                    verbose_name='Question',
                )),
                ('result', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='speaking_recordings',
                    to='portals.quizresult',
                    verbose_name='Quiz result',
                )),
            ],
            options={
                'verbose_name': 'Speaking recording',
                'verbose_name_plural': 'Speaking recordings',
                'ordering': ('question__part__order', 'question__order', 'id'),
            },
        ),
        migrations.AddConstraint(
            model_name='speakingrecording',
            constraint=models.UniqueConstraint(
                fields=('result', 'question'),
                name='portals_speaking_recording_uniq',
            ),
        ),
    ]
