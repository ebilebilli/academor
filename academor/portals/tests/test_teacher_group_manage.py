"""Teacher schedule management for owned study groups."""

from datetime import time

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from portals.models import Schedule, StudentProfile, StudyGroup, TeacherProfile
from portals.tests.portal_helpers import portal_client_login
from portals.utils.teacher_schedule_form import validate_schedule_slots

User = get_user_model()


class TeacherScheduleFormUtilsTests(SimpleTestCase):
    def test_validate_requires_at_least_one_slot(self):
        _cleaned, errors = validate_schedule_slots([])
        self.assertTrue(errors)

    def test_validate_rejects_duplicate_rows(self):
        rows = [
            {'index': 0, 'weekday': '0', 'start_time': '10:00', 'duration_min': '90'},
            {'index': 1, 'weekday': '0', 'start_time': '10:00', 'duration_min': '60'},
        ]
        cleaned, errors = validate_schedule_slots(rows)
        self.assertEqual(len(cleaned), 1)
        self.assertTrue(errors)


class TeacherScheduleManageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='schedule_teacher', password='pass'),
        )
        self.other_teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='schedule_other_teacher', password='pass'),
        )
        self.student = StudentProfile.objects.create(
            user=User.objects.create_user(username='schedule_student', password='pass'),
        )
        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS Morning',
            max_students=10,
        )
        self.group.students.add(self.student)
        portal_client_login(self.client, self.teacher.user)

    def _bulk_post(self, slots):
        payload = {'slot_count': str(len(slots))}
        for index, slot in enumerate(slots):
            payload[f'slots-{index}-weekday'] = str(slot['weekday'])
            payload[f'slots-{index}-start_time'] = slot['start_time']
            payload[f'slots-{index}-duration_min'] = str(slot.get('duration_min', 90))
        return payload

    def test_teacher_can_create_multiple_schedule_slots(self):
        create_url = reverse(
            'portals:teacher-schedule-create',
            kwargs={'group_pk': self.group.pk},
        )
        response = self.client.post(
            create_url,
            self._bulk_post([
                {'weekday': Schedule.Weekday.MONDAY, 'start_time': '10:00'},
                {'weekday': Schedule.Weekday.WEDNESDAY, 'start_time': '14:30', 'duration_min': 60},
            ]),
        )
        self.assertEqual(response.status_code, 302)
        schedules = list(Schedule.objects.filter(group=self.group).order_by('weekday'))
        self.assertEqual(len(schedules), 2)
        self.assertEqual(schedules[0].start_time, time(10, 0))
        self.assertEqual(schedules[0].room_or_link, '')
        self.assertEqual(schedules[1].duration_min, 60)

    def test_teacher_can_edit_schedule_without_room_or_active_from(self):
        schedule = Schedule.objects.create(
            group=self.group,
            weekday=Schedule.Weekday.MONDAY,
            start_time=time(10, 0),
            duration_min=90,
            room_or_link='Room 1',
        )
        edit_url = reverse('portals:teacher-schedule-edit', kwargs={'schedule_pk': schedule.pk})
        response = self.client.post(
            edit_url,
            {
                'group': self.group.pk,
                'weekday': Schedule.Weekday.TUESDAY,
                'start_time': '11:30',
                'duration_min': 60,
            },
        )
        self.assertEqual(response.status_code, 302)
        schedule.refresh_from_db()
        self.assertEqual(schedule.weekday, Schedule.Weekday.TUESDAY)
        self.assertEqual(schedule.start_time, time(11, 30))
        self.assertEqual(schedule.room_or_link, 'Room 1')

    def test_teacher_can_delete_schedule(self):
        schedule = Schedule.objects.create(
            group=self.group,
            weekday=Schedule.Weekday.WEDNESDAY,
            start_time=time(9, 0),
            duration_min=90,
        )
        delete_url = reverse('portals:teacher-schedule-delete', kwargs={'schedule_pk': schedule.pk})
        response = self.client.post(delete_url, {'return_to': 'group'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Schedule.objects.filter(pk=schedule.pk).exists())

    def test_other_teacher_cannot_edit_schedule(self):
        schedule = Schedule.objects.create(
            group=self.group,
            weekday=Schedule.Weekday.FRIDAY,
            start_time=time(14, 0),
            duration_min=90,
        )
        portal_client_login(self.client, self.other_teacher.user)
        edit_url = reverse('portals:teacher-schedule-edit', kwargs={'schedule_pk': schedule.pk})
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 404)

    def test_teacher_can_rename_own_group(self):
        url = reverse('portals:teacher-group-rename', kwargs={'pk': self.group.pk})
        response = self.client.post(url, {'name': 'IELTS Advanced'})
        self.assertEqual(response.status_code, 302)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'IELTS Advanced')

    def test_other_teacher_cannot_rename_group(self):
        portal_client_login(self.client, self.other_teacher.user)
        url = reverse('portals:teacher-group-rename', kwargs={'pk': self.group.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
