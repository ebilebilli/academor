from django.db import migrations, models
import django.db.models.deletion


def seed_quiz_assignments(apps, schema_editor):
    StudentCourseSpecialization = apps.get_model('portals', 'StudentCourseSpecialization')
    Quiz = apps.get_model('portals', 'Quiz')
    QuizAssignment = apps.get_model('portals', 'QuizAssignment')

    student_services = {}
    for student_id, course_type in (
        StudentCourseSpecialization.objects.filter(is_active=True)
        .values_list('student_id', 'course_type')
        .iterator()
    ):
        student_services.setdefault(student_id, set()).add(course_type)

    quizzes_by_service = {}
    for quiz_id, service in (
        Quiz.objects.select_related('category')
        .values_list('id', 'category__service')
        .iterator()
    ):
        if not service:
            continue
        quizzes_by_service.setdefault(service, []).append(quiz_id)

    batch = []
    for student_id, services in student_services.items():
        for service in services:
            for quiz_id in quizzes_by_service.get(service, []):
                batch.append(
                    QuizAssignment(
                        student_id=student_id,
                        quiz_id=quiz_id,
                        is_active=True,
                    )
                )
                if len(batch) >= 500:
                    QuizAssignment.objects.bulk_create(batch, ignore_conflicts=True)
                    batch = []
    if batch:
        QuizAssignment.objects.bulk_create(batch, ignore_conflicts=True)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0072_schedule_unique_slot'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False, help_text='When enabled, the student can see and take this quiz.', verbose_name='Active')),
                ('assigned_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                (
                    'assigned_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='quiz_assignments_created',
                        to='portals.teacherprofile',
                        verbose_name='Assigned by',
                    ),
                ),
                (
                    'quiz',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='student_assignments',
                        to='portals.quiz',
                        verbose_name='Quiz',
                    ),
                ),
                (
                    'student',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='quiz_assignments',
                        to='portals.studentprofile',
                        verbose_name='Student',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Quiz assignment',
                'verbose_name_plural': 'Quiz assignments',
                'ordering': ('-assigned_at', 'id'),
            },
        ),
        migrations.AddConstraint(
            model_name='quizassignment',
            constraint=models.UniqueConstraint(fields=('student', 'quiz'), name='portals_quiz_assignment_uniq'),
        ),
        migrations.RunPython(seed_quiz_assignments, migrations.RunPython.noop),
    ]
