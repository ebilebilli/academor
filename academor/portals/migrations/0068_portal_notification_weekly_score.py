from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0067_weekly_student_score'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='portalnotification',
            name='portals_notification_has_target',
        ),
        migrations.RemoveConstraint(
            model_name='portalnotification',
            name='portals_notification_parent_result_unique',
        ),
        migrations.RemoveConstraint(
            model_name='portalnotification',
            name='portals_notification_student_result_unique',
        ),
        migrations.AddField(
            model_name='portalnotification',
            name='weekly_student_score',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications',
                to='portals.weeklystudentscore',
                verbose_name='Weekly student score',
            ),
        ),
        migrations.AlterField(
            model_name='portalnotification',
            name='kind',
            field=models.CharField(
                choices=[
                    ('submission_pending', 'Submission awaiting review'),
                    ('result_published', 'Result published'),
                    ('mock_test_completed', 'IELTS mock test completed'),
                    ('weekly_score_published', 'Weekly score published'),
                ],
                default='result_published',
                max_length=32,
                verbose_name='Type',
            ),
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(quiz_result__isnull=False)
                    | models.Q(ielts_mock_test__isnull=False)
                    | models.Q(weekly_student_score__isnull=False)
                ),
                name='portals_notification_has_target',
            ),
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.UniqueConstraint(
                condition=models.Q(parent__isnull=False, quiz_result__isnull=False),
                fields=('parent', 'quiz_result'),
                name='portals_notification_parent_result_unique',
            ),
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.UniqueConstraint(
                condition=models.Q(student__isnull=False, quiz_result__isnull=False),
                fields=('student', 'quiz_result'),
                name='portals_notification_student_result_unique',
            ),
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.UniqueConstraint(
                condition=models.Q(parent__isnull=False, weekly_student_score__isnull=False),
                fields=('parent', 'weekly_student_score'),
                name='portals_notification_parent_weekly_unique',
            ),
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.UniqueConstraint(
                condition=models.Q(student__isnull=False, weekly_student_score__isnull=False),
                fields=('student', 'weekly_student_score'),
                name='portals_notification_student_weekly_unique',
            ),
        ),
    ]
