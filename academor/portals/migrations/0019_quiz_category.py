from django.db import migrations, models
import django.db.models.deletion


def forwards_quiz_categories(apps, schema_editor):
    Quiz = apps.get_model('portals', 'Quiz')
    QuizCategory = apps.get_model('portals', 'QuizCategory')
    QuizCourseSpecialization = apps.get_model('portals', 'QuizCourseSpecialization')

    for quiz in Quiz.objects.all().iterator():
        specs = list(
            QuizCourseSpecialization.objects.filter(quiz_id=quiz.pk)
            .order_by('id')
            .values_list('course_type', flat=True)
        )
        service = specs[0] if specs else 'other'
        name = (quiz.topic or 'General').strip()[:255] or 'General'
        category, _ = QuizCategory.objects.get_or_create(
            service=service,
            name=name,
        )
        quiz.category_id = category.pk
        quiz.save(update_fields=['category_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0018_remove_student_quiz_direct_links'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(
                    choices=[
                        ('general_english', 'General English'),
                        ('speaking', 'Speaking'),
                        ('ielts', 'IELTS'),
                        ('gmat', 'GMAT'),
                        ('gre', 'GRE'),
                        ('sat', 'SAT'),
                        ('yos', 'YÖS'),
                        ('ales', 'ALES'),
                        ('study_abroad', 'Study abroad'),
                        ('other', 'Other'),
                    ],
                    db_index=True,
                    max_length=32,
                    verbose_name='Service',
                )),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Quiz category',
                'verbose_name_plural': 'Quiz categories',
                'ordering': ('service', 'name', 'id'),
            },
        ),
        migrations.AddConstraint(
            model_name='quizcategory',
            constraint=models.UniqueConstraint(
                fields=('service', 'name'),
                name='portals_quiz_category_uniq',
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='category',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='quizzes',
                to='portals.quizcategory',
                verbose_name='Category',
            ),
        ),
        migrations.RunPython(forwards_quiz_categories, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='quiz',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='quizzes',
                to='portals.quizcategory',
                verbose_name='Category',
            ),
        ),
        migrations.DeleteModel(
            name='QuizCourseSpecialization',
        ),
    ]
