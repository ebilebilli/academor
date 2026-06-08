from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0077_study_abroad_advantages'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ServiceCategory',
            new_name='Service',
        ),
        migrations.AlterModelOptions(
            name='service',
            options={
                'ordering': ('order', 'id'),
                'verbose_name': 'Service',
                'verbose_name_plural': 'Services',
            },
        ),
        migrations.AlterField(
            model_name='service',
            name='instructors',
            field=models.ManyToManyField(
                blank=True,
                help_text='Team members shown on the course detail page (Trainers tab).',
                related_name='services',
                to='projects.team',
                verbose_name='Trainers',
            ),
        ),
        migrations.AlterField(
            model_name='media',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name='medias',
                to='projects.service',
                verbose_name='Service',
            ),
        ),
        migrations.DeleteModel(
            name='ServiceHighlight',
        ),
        migrations.RemoveField(
            model_name='media',
            name='partner',
        ),
        migrations.DeleteModel(
            name='Instructor',
        ),
    ]
