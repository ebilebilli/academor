from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from portals.models import (
    CustomerProfile,
    IeltsMockTestAttempt,
    Quiz,
    Schedule,
    StudentProfile,
    StudyGroup,
    TeacherProfile,
)
from portals.tests.group_helpers import create_quiz_category, link_study_group_services
from portals.tests.portal_helpers import ensure_active_portal_services, portal_client_login
from portals.utils.customer_mock import build_customer_mock_dashboard_sections
from portals.utils.ielts_mock_test import IELTS_SERVICE, SAT_SERVICE
from portals.utils.portal_hero import customer_hero_stats, student_hero_stats
from portals.utils.teacher_schedule import build_student_today_agenda


def _at(day, hour, minute=0):
    return timezone.make_aware(datetime.combine(day, time(hour, minute)), timezone.get_current_timezone())


User = get_user_model()


class StudentTodayAgendaTests(TestCase):
    def setUp(self):
        ensure_active_portal_services('ielts', 'speaking')
        teacher = TeacherProfile.objects.create(user=User.objects.create_user(username='teacher1', password='pass'))
        self.student_user = User.objects.create_user(username='student1', password='pass')
        self.student = StudentProfile.objects.create(user=self.student_user)
        self.ielts_group = StudyGroup.objects.create(teacher=teacher, name='IELTS A', max_students=10)
        self.speaking_group = StudyGroup.objects.create(teacher=teacher, name='Speaking B', max_students=10)
        link_study_group_services(self.ielts_group, 'ielts')
        link_study_group_services(self.speaking_group, 'speaking')
        self.ielts_group.students.add(self.student)
        self.today = timezone.localdate()
        self.effective = self.today - timedelta(days=30)

    def _slot(self, weekday, start, minutes=60, room='Room 4'):
        return Schedule.objects.create(
            group=self.ielts_group,
            weekday=weekday,
            start_time=start,
            duration_min=minutes,
            room_or_link=room,
            effective_from=self.effective,
        )

    def test_marks_done_live_and_upcoming_sessions(self):
        weekday = self.today.weekday()
        self._slot(weekday, time(9, 0))
        self._slot(weekday, time(12, 0), minutes=90, room='https://meet.example.com/a')
        self._slot(weekday, time(18, 0))

        agenda = build_student_today_agenda(self.student.pk, now=_at(self.today, 12, 30))

        slots = agenda['today_schedule']
        self.assertEqual([slot['start_time'] for slot in slots], ['09:00', '12:00', '18:00'])
        self.assertTrue(slots[0]['is_done'])
        self.assertTrue(slots[1]['is_now'])
        self.assertEqual(slots[1]['end_time'], '13:30')
        self.assertEqual(slots[1]['join_url'], 'https://meet.example.com/a')
        self.assertNotIn('https://', slots[1]['details'])
        self.assertFalse(slots[2]['is_done'] or slots[2]['is_now'])
        self.assertEqual(agenda['today_remaining'], 2)
        self.assertIsNone(agenda['next_session'])

    def test_next_session_when_nothing_is_left_today(self):
        weekday = self.today.weekday()
        self._slot(weekday, time(9, 0))
        self._slot((weekday + 2) % 7, time(10, 0))

        agenda = build_student_today_agenda(self.student.pk, now=_at(self.today, 20, 0))

        self.assertEqual(agenda['today_remaining'], 0)
        self.assertIsNotNone(agenda['next_session'])
        self.assertEqual(agenda['next_session']['date'], self.today + timedelta(days=2))
        self.assertEqual(agenda['next_session']['start_time'], '10:00')

    def test_other_groups_do_not_leak_into_the_agenda(self):
        Schedule.objects.create(
            group=self.speaking_group,
            weekday=self.today.weekday(),
            start_time=time(15, 0),
            duration_min=60,
            room_or_link='Room 9',
            effective_from=self.effective,
        )
        agenda = build_student_today_agenda(self.student.pk, now=_at(self.today, 8, 0))
        self.assertEqual(agenda['today_schedule'], [])

    def test_dashboard_renders_today_lessons_and_hero(self):
        self._slot(self.today.weekday(), time(23, 30), minutes=20, room='Room 7')
        client = Client()
        portal_client_login(client, self.student_user)

        response = client.get(reverse('portals:student-dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="pb-hero')
        self.assertContains(response, 'IELTS A')
        self.assertContains(response, '23:30')
        self.assertContains(response, 'portal-brand.css')
        self.assertEqual(len(response.context['hero_stats']), 3)

    def test_hero_stats_round_percentages_and_fall_back_to_dash(self):
        stats = student_hero_stats(
            {'quiz_average': {'avg_score_pct': 83.6}, 'attendance_stats': {'attendance_rate': None}},
            {'today_schedule': [{}, {}]},
        )
        self.assertEqual([stat['value'] for stat in stats], [2, '84%', '—'])


class CustomerDashboardTests(TestCase):
    def setUp(self):
        ensure_active_portal_services('ielts', 'sat')
        self.customer_user = User.objects.create_user(username='customer1', password='pass')
        self.customer = CustomerProfile.objects.create(user=self.customer_user, ielts_mock_credits=1)
        self.teacher_user = User.objects.create_user(username='teacher1', password='pass')
        TeacherProfile.objects.create(user=self.teacher_user)

    def test_sections_carry_section_labels_and_completed_count(self):
        quiz = Quiz.objects.create(category=create_quiz_category('Reading', 'ielts'), topic='Reading 1')
        IeltsMockTestAttempt.objects.create(
            customer=self.customer,
            reading_quiz=quiz,
            exam_program=IELTS_SERVICE,
            status=IeltsMockTestAttempt.Status.COMPLETED,
            completed_at=timezone.now(),
        )

        sections = build_customer_mock_dashboard_sections(self.customer.pk)
        ielts = next(section for section in sections if section['program'] == IELTS_SERVICE)

        self.assertEqual(ielts['completed_count'], 1)
        self.assertEqual(len(ielts['section_labels']), 4)
        stats = customer_hero_stats(sections)
        self.assertEqual(stats[-1]['value'], 1)

    def test_dashboard_lists_programs_as_rows(self):
        self.customer.sat_mock_credits = 2
        self.customer.save(update_fields=['sat_mock_credits'])
        client = Client()
        portal_client_login(client, self.customer_user)

        response = client.get(reverse('portals:customer-dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="pb-row"', count=2)
        self.assertContains(response, reverse('portals:customer-mock-landing', kwargs={'program': SAT_SERVICE}))
        # a new customer sees how a mock test works, and the package upsell
        self.assertContains(response, 'pb-steps')
        self.assertContains(response, reverse('portals:customer-mock-packages'))

    def test_teacher_pages_do_not_load_the_brand_layer(self):
        client = Client()
        portal_client_login(client, self.teacher_user)
        response = client.get(reverse('portals:teacher-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'portal-brand.css')
