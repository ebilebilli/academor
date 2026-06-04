from decimal import Decimal

from django.db import migrations


def seed_packages_from_legacy_price(apps, schema_editor):
    ServiceCategory = apps.get_model('projects', 'ServiceCategory')
    CoursePricePackage = apps.get_model('projects', 'CoursePricePackage')

    for course in ServiceCategory.objects.all():
        if not course.price or course.price <= 0:
            continue
        if CoursePricePackage.objects.filter(course_id=course.pk).exists():
            continue
        duration = (course.duration_months_az or '').strip()
        CoursePricePackage.objects.create(
            course_id=course.pk,
            name_az=(course.name_az or 'Standart paket').strip()[:255],
            name_en=(course.name_en or '').strip()[:255],
            name_ru=(course.name_ru or '').strip()[:255],
            duration=duration,
            price=Decimal(str(course.price)),
            order=0,
            is_active=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0070_course_price_packages'),
    ]

    operations = [
        migrations.RunPython(seed_packages_from_legacy_price, migrations.RunPython.noop),
    ]
