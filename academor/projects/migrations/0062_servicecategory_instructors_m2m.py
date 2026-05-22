from django.db import migrations, models


def copy_instructor_to_instructors(apps, schema_editor):
    ServiceCategory = apps.get_model('projects', 'ServiceCategory')
    for category in ServiceCategory.objects.exclude(instructor_id=None).iterator():
        category.instructors.add(category.instructor_id)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0061_alter_blogpost_on_top'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecategory',
            name='instructors',
            field=models.ManyToManyField(
                blank=True,
                help_text='Team members shown on the course detail page (Trainers tab).',
                related_name='service_categories',
                to='projects.team',
                verbose_name='Trainers',
            ),
        ),
        migrations.RunPython(copy_instructor_to_instructors, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='servicecategory',
            name='instructor',
        ),
    ]
