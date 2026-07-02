from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0026_quizresult_unique_attempt'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortalNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(default=False, verbose_name='Read')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='portals.parentprofile', verbose_name='Parent')),
                ('quiz_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='portals.quizresult', verbose_name='Quiz result')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='portals.teacherprofile', verbose_name='Teacher')),
            ],
            options={
                'verbose_name': 'Portal notification',
                'verbose_name_plural': 'Portal notifications',
                'ordering': ('-created_at', '-id'),
            },
        ),
        migrations.AddIndex(
            model_name='portalnotification',
            index=models.Index(fields=['teacher', 'is_read', '-created_at'], name='portals_not_teacher_8b0f0d_idx'),
        ),
        migrations.AddIndex(
            model_name='portalnotification',
            index=models.Index(fields=['parent', 'is_read', '-created_at'], name='portals_not_parent_4a8c2e_idx'),
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(('parent__isnull', True), ('teacher__isnull', False)),
                    models.Q(('parent__isnull', False), ('teacher__isnull', True)),
                    _connector='OR',
                ),
                name='portals_notification_single_recipient',
            ),
        ),
        migrations.AddConstraint(
            model_name='portalnotification',
            constraint=models.UniqueConstraint(
                condition=models.Q(('teacher__isnull', False)),
                fields=('teacher', 'quiz_result'),
                name='portals_notification_teacher_result_unique',
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
    ]
