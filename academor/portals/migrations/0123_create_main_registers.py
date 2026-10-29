"""Give every teacher one general attendance register and move manual names into it.

Teachers keep their attendance on one table with every student on it, written as manual
names (register guests) inside whichever group they happened to pick. This creates the
teacher's "Ümumi davamiyyət cədvəli" (is_main_register) and moves each guest, with all of
their marks, into it. Groups, their courses and their real students are left as they are;
real students show up on the general register through their group membership.
"""

from django.db import migrations

MAIN_REGISTER_NAME = 'Ümumi davamiyyət cədvəli'


def create_main_registers(apps, schema_editor):
    TeacherProfile = apps.get_model('portals', 'TeacherProfile')
    StudyGroup = apps.get_model('portals', 'StudyGroup')
    Guest = apps.get_model('portals', 'AttendanceRegisterGuest')
    Attendance = apps.get_model('portals', 'Attendance')

    for teacher in TeacherProfile.objects.all():
        main = StudyGroup.objects.filter(teacher=teacher, is_main_register=True).order_by('id').first()
        if main is None:
            main = StudyGroup.objects.create(
                teacher=teacher,
                name=MAIN_REGISTER_NAME,
                is_register_only=True,
                is_main_register=True,
                is_active=True,
                max_students=500,
            )

        for guest in Guest.objects.filter(group__teacher=teacher).exclude(group=main).order_by('id'):
            # same name already on the general register: merge into that row
            target = (
                Guest.objects.filter(group=main, name__iexact=guest.name).order_by('-is_active', 'id').first()
            )
            if target is None:
                Guest.objects.filter(pk=guest.pk).update(group=main)
                target = guest
            for row in Attendance.objects.filter(guest=guest).order_by('marked_at', 'id'):
                clash = (
                    Attendance.objects.filter(
                        group=main, guest=target, session_date=row.session_date, schedule__isnull=True,
                    ).exclude(pk=row.pk).first()
                )
                if clash is not None:
                    if clash.marked_at >= row.marked_at:
                        row.delete()
                        continue
                    clash.delete()
                Attendance.objects.filter(pk=row.pk).update(group=main, schedule=None, guest=target)
            if target.pk != guest.pk:
                if guest.is_active and not target.is_active:
                    Guest.objects.filter(pk=target.pk).update(is_active=True)
                guest.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0122_studygroup_is_main_register'),
    ]

    operations = [
        migrations.RunPython(create_main_registers, migrations.RunPython.noop),
    ]
