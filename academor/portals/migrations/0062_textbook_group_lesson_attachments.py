from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0061_listeningquestion_answer_keys'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='textbooks',
                to='portals.studygroup',
                verbose_name='Group',
            ),
        ),
        migrations.AddField(
            model_name='classroom',
            name='teacher',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='textbooks',
                to='portals.teacherprofile',
                verbose_name='Teacher',
            ),
        ),
        migrations.AlterModelOptions(
            name='classroom',
            options={
                'ordering': ('name', 'id'),
                'verbose_name': 'Textbook',
                'verbose_name_plural': 'Textbooks',
            },
        ),
        migrations.AlterField(
            model_name='classroom',
            name='services',
            field=models.ManyToManyField(
                blank=True,
                help_text='Legacy admin field — portal textbooks use group access instead.',
                related_name='classrooms',
                to='projects.service',
                verbose_name='Services',
            ),
        ),
        migrations.CreateModel(
            name='LessonAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(
                    choices=[('pdf', 'PDF'), ('image', 'Image')],
                    max_length=16,
                    verbose_name='Type',
                )),
                ('file', models.FileField(upload_to='portals/lessons/attachments/', verbose_name='File')),
                ('lesson', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='attachments',
                    to='portals.lesson',
                    verbose_name='Lesson',
                )),
            ],
            options={
                'verbose_name': 'Lesson attachment',
                'verbose_name_plural': 'Lesson attachments',
                'ordering': ('id',),
            },
        ),
    ]
