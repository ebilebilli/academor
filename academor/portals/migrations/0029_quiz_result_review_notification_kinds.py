from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0028_rename_portals_not_teacher_8b0f0d_idx_portals_por_teacher_d75e4c_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizResultReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(verbose_name='Score')),
                ('feedback', models.TextField(blank=True, verbose_name='Feedback and corrections')),
                ('reviewed_at', models.DateTimeField(auto_now_add=True, verbose_name='Reviewed at')),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='portals.quizresult', verbose_name='Quiz result')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quiz_result_reviews', to='portals.teacherprofile', verbose_name='Reviewer')),
            ],
            options={
                'verbose_name': 'Quiz result review',
                'verbose_name_plural': 'Quiz result reviews',
                'ordering': ('-reviewed_at', 'id'),
            },
        ),
        migrations.AddField(
            model_name='portalnotification',
            name='kind',
            field=models.CharField(
                choices=[('submission_pending', 'Submission awaiting review'), ('result_published', 'Result published')],
                default='result_published',
                max_length=32,
                verbose_name='Type',
            ),
        ),
        migrations.AddField(
            model_name='portalnotification',
            name='student',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications',
                to='portals.studentprofile',
                verbose_name='Student',
            ),
        ),
        migrations.RemoveConstraint(
            model_name='portalnotification',
            name='portals_notification_single_recipient',
        ),
        migrations.RemoveConstraint(
            model_name='portalnotification',
            name='portals_notification_teacher_result_unique',
        ),
        migrations.RemoveConstraint(
            model_name='portalnotification',
            name='portals_notification_parent_result_unique',
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(('parent__isnull', True), ('student__isnull', True), ('teacher__isnull', False)),
                    models.Q(('parent__isnull', False), ('student__isnull', True), ('teacher__isnull', True)),
                    models.Q(('parent__isnull', True), ('student__isnull', False), ('teacher__isnull', True)),
                    _connector='OR',
                ),
                name='portals_notification_single_recipient',
            ),
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.UniqueConstraint(
                condition=models.Q(('teacher__isnull', False)),
                fields=('teacher', 'quiz_result', 'kind'),
                name='portals_notification_teacher_result_kind_unique',
            ),
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.UniqueConstraint(
                condition=models.Q(('parent__isnull', False)),
                fields=('parent', 'quiz_result'),
                name='portals_notification_parent_result_unique',
            ),
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.UniqueConstraint(
                condition=models.Q(('student__isnull', False)),
                fields=('student', 'quiz_result'),
                name='portals_notification_student_result_unique',
            ),
        ),
        migrations.AddIndex(
            model_name='portalnotification',
            index=models.Index(fields=['student', 'is_read', '-created_at'], name='portals_not_student_6d2a1b_idx'),
        ),
    ]
