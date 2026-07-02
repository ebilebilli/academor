from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0043_alter_quizresult_total_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentCourseSpecialization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_type', models.CharField(max_length=32, verbose_name='Service')),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Only active enrollments grant quiz and classroom access for this service.',
                    verbose_name='Active',
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
        migrations.AddConstraint(
            model_name='studentcoursespecialization',
            constraint=models.UniqueConstraint(
                fields=('student', 'course_type'),
                name='portals_student_course_type_uniq',
            ),
        ),
    ]
