from django.db import migrations, models


def copy_group_course_type_to_lesson_subject(apps, schema_editor):
    Lesson = apps.get_model('portals', 'Lesson')
    for lesson in Lesson.objects.select_related('group').iterator():
        if lesson.group_id and lesson.group.course_type:
            Lesson.objects.filter(pk=lesson.pk).update(subject=lesson.group.course_type)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0007_alter_teachercoursespecialization_course_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='subject',
            field=models.CharField(
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
                default='general_english',
                max_length=32,
                verbose_name='Subject',
            ),
            preserve_default=False,
        ),
        migrations.RunPython(
            copy_group_course_type_to_lesson_subject,
            migrations.RunPython.noop,
        ),
    ]
