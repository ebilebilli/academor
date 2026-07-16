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


def forwards_quiz_category_services(apps, schema_editor):
    QuizCategory = apps.get_model('portals', 'QuizCategory')
    Service = apps.get_model('projects', 'Service')

    for category in QuizCategory.objects.all().iterator():
        services = _services_for_course_type(Service, category.service)
        if services:
            category.services.set(services)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0093_portal_notification_homework'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizcategory',
            name='services',
            field=models.ManyToManyField(
                blank=True,
                help_text='Site courses linked to this quiz category.',
                related_name='quiz_categories',
                to='projects.service',
                verbose_name='Services',
            ),
        ),
        migrations.RunPython(forwards_quiz_category_services, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='quizcategory',
            name='portals_quiz_category_uniq',
        ),
        migrations.RemoveField(
            model_name='quizcategory',
            name='service',
        ),
        migrations.AlterModelOptions(
            name='quizcategory',
            options={
                'ordering': ('name', 'id'),
                'verbose_name': 'Quiz category',
                'verbose_name_plural': 'Quiz categories',
            },
        ),
    ]
