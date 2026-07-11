from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0089_quiz_sat_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentmockaccess',
            name='exam_program',
            field=models.CharField(
                default='ielts',
                help_text='Mock exam program code, e.g. ielts or sat.',
                max_length=16,
                verbose_name='Exam program',
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studentmockaccess',
            name='is_active',
            field=models.BooleanField(
                default=False,
                help_text='When enabled, the student can start this mock test program.',
                verbose_name='Active',
            ),
        ),
        migrations.AlterField(
            model_name='studentmockaccess',
            name='student',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='mock_access_entries',
                to='portals.studentprofile',
                verbose_name='Student',
            ),
        ),
        migrations.AddConstraint(
            model_name='studentmockaccess',
            constraint=models.UniqueConstraint(
                fields=('student', 'exam_program'),
                name='portals_student_mock_access_program_uniq',
            ),
        ),
    ]
