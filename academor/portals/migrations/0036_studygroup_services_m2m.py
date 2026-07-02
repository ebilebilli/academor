from django.db import migrations, models


def _services_for_course_type(Service, course_type):
    code = (course_type or '').strip().lower()
    if not code:
        return []
    matched = []
    seen = set()
    for service in Service.objects.filter(is_active=True).iterator():
        slug = (service.slug or '').strip().lower()
        if not slug or service.pk in seen:
            continue
        normalized_slug = slug.replace('-', '_')
        normalized_code = code.replace('-', '_')
        if slug == code or normalized_slug == normalized_code or code in slug:
            matched.append(service)
            seen.add(service.pk)
    return matched


def forwards_studygroup_services(apps, schema_editor):
    StudyGroup = apps.get_model('portals', 'StudyGroup')
    Service = apps.get_model('projects', 'Service')

    for group in StudyGroup.objects.all().iterator():
        services = _services_for_course_type(Service, group.course_type)
        if services:
            group.services.set(services)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0035_remove_quiz_teacher'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='services',
            field=models.ManyToManyField(
                blank=True,
                help_text='Courses for this group — linked to active site services.',
                related_name='study_groups',
                to='projects.service',
                verbose_name='Services',
            ),
        ),
        migrations.RunPython(forwards_studygroup_services, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='studygroup',
            name='course_type',
        ),
    ]
