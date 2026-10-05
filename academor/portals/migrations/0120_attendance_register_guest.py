from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0119_attendance_register_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceRegisterGuest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Full name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                (
                    'group',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='register_guests',
                        to='portals.studygroup',
                        verbose_name='Group',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Register guest student',
                'verbose_name_plural': 'Register guest students',
                'ordering': ('name', 'id'),
            },
        ),
        migrations.AddField(
            model_name='attendance',
            name='guest',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='attendances',
                to='portals.attendanceregisterguest',
                verbose_name='Guest student',
            ),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='student',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='attendances',
                to='portals.studentprofile',
                verbose_name='Student',
            ),
        ),
        migrations.RemoveConstraint(
            model_name='attendance',
            name='portals_attendance_unique_register_day',
        ),
        migrations.AddConstraint(
            model_name='attendance',
            constraint=models.UniqueConstraint(
                condition=models.Q(('schedule__isnull', True), ('student__isnull', False)),
                fields=('group', 'student', 'session_date'),
                name='portals_attendance_unique_register_day',
            ),
        ),
        migrations.AddConstraint(
            model_name='attendance',
            constraint=models.UniqueConstraint(
                condition=models.Q(('guest__isnull', False), ('schedule__isnull', True)),
                fields=('group', 'guest', 'session_date'),
                name='portals_attendance_unique_guest_day',
            ),
        ),
        migrations.AddConstraint(
            model_name='attendance',
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(('guest__isnull', True), ('student__isnull', False)),
                    models.Q(('guest__isnull', False), ('student__isnull', True)),
                    _connector='OR',
                ),
                name='portals_attendance_student_xor_guest',
            ),
        ),
    ]
