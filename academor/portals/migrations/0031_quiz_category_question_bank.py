from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0030_rename_portals_not_student_6d2a1b_idx_portals_por_student_941cad_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='use_random_questions_20',
            field=models.BooleanField(
                default=False,
                help_text='Pick 8 easy, 8 medium, and 4 hard questions from the category bank for each student attempt. Only one random size can be enabled.',
                verbose_name='Random 20 questions',
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='use_random_questions_30',
            field=models.BooleanField(
                default=False,
                help_text='Pick 12 easy, 12 medium, and 6 hard questions from the category bank for each student attempt. Only one random size can be enabled.',
                verbose_name='Random 30 questions',
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='use_random_questions_50',
            field=models.BooleanField(
                default=False,
                help_text='Pick 20 easy, 20 medium, and 10 hard questions from the category bank for each student attempt. Only one random size can be enabled.',
                verbose_name='Random 50 questions',
            ),
        ),
        migrations.CreateModel(
            name='QuizCategoryQuestionBank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difficulty', models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], db_index=True, max_length=16, verbose_name='Difficulty')),
                ('prompt_type', models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video'), ('audio', 'Audio')], default='text', max_length=16, verbose_name='Question type')),
                ('question', models.TextField(blank=True, help_text='Written question or caption shown with image / video / audio.', verbose_name='Question text')),
                ('media_file', models.FileField(blank=True, help_text='Upload image, video, or audio when the question type is not text.', null=True, upload_to='portals/quiz/bank-media/', verbose_name='Media file')),
                ('media_url', models.URLField(blank=True, help_text='Optional external link (e.g. YouTube) instead of an uploaded file.', verbose_name='Media URL')),
                ('answer_options', models.JSONField(blank=True, default=list, help_text='List of answer choices shown to the student.', verbose_name='Answer options')),
                ('correct_option_index', models.PositiveIntegerField(default=0, verbose_name='Correct option index')),
                ('correct_answer', models.CharField(blank=True, max_length=500, verbose_name='Correct answer')),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Inactive questions are excluded from random quiz selection.', verbose_name='Active')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bank_questions', to='portals.quizcategory', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Category question bank item',
                'verbose_name_plural': 'Category question bank',
                'ordering': ('difficulty', 'id'),
            },
        ),
    ]
