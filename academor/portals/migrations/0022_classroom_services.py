from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0021_quizquestion_answer_options_blank'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassroomService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(
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
                    max_length=32,
                    verbose_name='Service',
                )),
                ('classroom', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='services',
                    to='portals.classroom',
                    verbose_name='Classroom',
                )),
            ],
            options={
                'verbose_name': 'Classroom service',
                'verbose_name_plural': 'Classroom services',
                'ordering': ('service', 'id'),
            },
        ),
        migrations.AddConstraint(
            model_name='classroomservice',
            constraint=models.UniqueConstraint(
                fields=('classroom', 'service'),
                name='portals_classroom_service_uniq',
            ),
        ),
    ]
