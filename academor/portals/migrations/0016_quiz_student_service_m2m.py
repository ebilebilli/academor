from django.db import migrations, models


def forwards_quiz_services(apps, schema_editor):
    Quiz = apps.get_model('portals', 'Quiz')
    QuizCourseSpecialization = apps.get_model('portals', 'QuizCourseSpecialization')
    for quiz in Quiz.objects.all().iterator():
        course_type = getattr(quiz, 'course_type', '') or ''
        if course_type:
            QuizCourseSpecialization.objects.get_or_create(
                quiz_id=quiz.pk,
                course_type=course_type,
            )


def forwards_student_services(apps, schema_editor):
    StudentProfile = apps.get_model('portals', 'StudentProfile')
    StudyGroup = apps.get_model('portals', 'StudyGroup')
    StudentCourseSpecialization = apps.get_model('portals', 'StudentCourseSpecialization')
    for student in StudentProfile.objects.all().iterator():
        course_types = (
            StudyGroup.objects.filter(students__pk=student.pk)
            .values_list('course_type', flat=True)
            .distinct()
        )
        for course_type in course_types:
            if course_type:
                StudentCourseSpecialization.objects.get_or_create(
                    student_id=student.pk,
                    course_type=course_type,
                )


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0015_lesson_name_date_classroom'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='assigned_teacher',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='assigned_students',
                to='portals.teacherprofile',
                verbose_name='Assigned teacher',
            ),
        ),
        migrations.CreateModel(
            name='StudentCourseSpecialization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_type', models.CharField(
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
                    max_length=32,
                    verbose_name='Service',
                )),
                ('student', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='course_specializations',
                    to='portals.studentprofile',
                    verbose_name='Student',
                )),
            ],
            options={
                'verbose_name': 'Student service',
                'verbose_name_plural': 'Student services',
                'ordering': ('course_type', 'id'),
            },
        ),
        migrations.CreateModel(
            name='QuizCourseSpecialization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_type', models.CharField(max_length=32, verbose_name='Service')),
                ('quiz', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='course_specializations',
                    to='portals.quiz',
                    verbose_name='Quiz',
                )),
            ],
            options={
                'verbose_name': 'Quiz service',
                'verbose_name_plural': 'Quiz services',
                'ordering': ('course_type', 'id'),
            },
        ),
        migrations.AddConstraint(
            model_name='studentcoursespecialization',
            constraint=models.UniqueConstraint(
                fields=('student', 'course_type'),
                name='portals_student_course_type_uniq',
            ),
        ),
        migrations.AddConstraint(
            model_name='quizcoursespecialization',
            constraint=models.UniqueConstraint(
                fields=('quiz', 'course_type'),
                name='portals_quiz_course_type_uniq',
            ),
        ),
        migrations.RunPython(forwards_quiz_services, migrations.RunPython.noop),
        migrations.RunPython(forwards_student_services, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='quiz',
            name='course_type',
        ),
    ]
