from django.db import migrations, models


def forwards_classroom_services(apps, schema_editor):
    Classroom = apps.get_model('portals', 'Classroom')
    ClassroomService = apps.get_model('portals', 'ClassroomService')
    Service = apps.get_model('projects', 'Service')

    services_by_slug = {
        (service.slug or '').strip().lower(): service
        for service in Service.objects.all().iterator()
        if service.slug
    }

    for link in ClassroomService.objects.select_related('classroom').iterator():
        code = (link.service or '').strip().lower()
        if not code:
            continue
        service = services_by_slug.get(code)
        if service is None:
            for slug, row in services_by_slug.items():
                if code in slug or slug in code:
                    service = row
                    break
        if service is not None:
            link.classroom.services.add(service)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0024_alter_quizresult_duration_sec'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroomservice',
            name='classroom',
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name='service_links',
                to='portals.classroom',
                verbose_name='Classroom',
            ),
        ),
        migrations.AddField(
            model_name='classroom',
            name='services',
            field=models.ManyToManyField(
                blank=True,
                help_text='Active site services — students and teachers see this room when their group matches.',
                related_name='classrooms',
                to='projects.service',
                verbose_name='Services',
            ),
        ),
        migrations.RunPython(forwards_classroom_services, migrations.RunPython.noop),
        migrations.DeleteModel(
            name='ClassroomService',
        ),
    ]
