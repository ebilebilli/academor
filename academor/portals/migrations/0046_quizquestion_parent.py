from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0045_clear_auto_student_service_enrollments'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizquestion',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sub_questions',
                to='portals.quizquestion',
                verbose_name='Parent audio question',
            ),
        ),
    ]
