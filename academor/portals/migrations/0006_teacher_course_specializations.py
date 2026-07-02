from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0005_profile_bio_social_links'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherCourseSpecialization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_type', models.CharField(max_length=32, verbose_name='Course type')),
                (
                    'teacher',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='course_specializations',
                        to='portals.teacherprofile',
                        verbose_name='Teacher',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Course specialization',
                'verbose_name_plural': 'Course specializations',
                'ordering': ('course_type', 'id'),
            },
        ),
        migrations.AddConstraint(
            model_name='teachercoursespecialization',
            constraint=models.UniqueConstraint(
                fields=('teacher', 'course_type'),
                name='portals_teacher_course_type_uniq',
            ),
        ),
    ]
