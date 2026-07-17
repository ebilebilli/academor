from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from portals.models import (
    Attendance,
    ParentProfile,
    Quiz,
    QuizCategory,
    QuizResult,
    Schedule,
    StudentCourseSpecialization,
    StudentProfile,
    StudyGroup,
    TeacherCourseSpecialization,
    TeacherProfile,
    WeeklyStudentScore,
)
from portals.tests.group_helpers import link_study_group_services
from portals.tests.portal_helpers import portal_client_login
from portals.tests.test_quiz_visibility import _ensure_active_portal_services
from portals.utils.group_services import students_matching_group_courses
from portals.utils.queries import (
    build_student_performance_by_groups,
    filter_attendance_detail_by_group,
    get_teacher_student_attendance_detail,
    get_teacher_student_profile_groups,
    prepare_student_scores_with_groups,
    resolve_teacher_profile_group,
    serialize_quiz_result_as_score,
)
from portals.utils.student_groups import (
    enrich_score_group_counts,
    get_student_study_groups,
    merge_parent_group_context,
    resolve_student_group,
    student_group_context,
)
from portals.utils.weekly_scores import serialize_weekly_score

User = get_user_model()


class StudentMultiGroupPortalTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()
        self.teacher_a = TeacherProfile.objects.create(
            user=User.objects.create_user(username='multi_teacher_a', password='pass'),
        )
        self.teacher_b = TeacherProfile.objects.create(
            user=User.objects.create_user(username='multi_teacher_b', password='pass'),
        )
        self.student_user = User.objects.create_user(username='multi_group_student', password='pass')
        self.student = StudentProfile.objects.create(user=self.student_user)
        self.group_a = StudyGroup.objects.create(
            teacher=self.teacher_a,
            name='IELTS group A',
            max_students=10,
        )
        self.group_b = StudyGroup.objects.create(
            teacher=self.teacher_b,
            name='SAT group B',
            max_students=10,
        )
        link_study_group_services(self.group_a, 'ielts')
        link_study_group_services(self.group_b, 'sat')

    def test_student_can_be_added_to_second_group_with_different_course(self):
        self.group_a.students.add(self.student)
        eligible = list(students_matching_group_courses(self.group_b))
        self.assertIn(self.student, eligible)
        self.group_b.students.add(self.student)
        group_ids = {group['id'] for group in get_student_study_groups(self.student.pk)}
        self.assertEqual(group_ids, {self.group_a.pk, self.group_b.pk})

    def test_student_group_context_defaults_to_first_group(self):
        self.group_a.students.add(self.student)
        self.group_b.students.add(self.student)
        request = RequestFactory().get('/portal/student/lessons/')
        ctx = student_group_context(request, self.student.pk)
        self.assertEqual(len(ctx['score_groups']), 2)
        self.assertEqual(ctx['active_score_group'], str(self.group_a.pk))
        self.assertIn(f'group={self.group_a.pk}', ctx['week_nav_prefix'])

    def test_resolve_student_group_from_query_param(self):
        self.group_a.students.add(self.student)
        self.group_b.students.add(self.student)
        groups = get_student_study_groups(self.student.pk)
        request = RequestFactory().get(f'/portal/student/lessons/?group={self.group_b.pk}')
        self.assertEqual(resolve_student_group(request, groups), self.group_b.pk)

    def test_prepare_student_scores_attaches_course_group_ids(self):
        self.group_a.students.add(self.student)
        self.group_b.students.add(self.student)
        StudentCourseSpecialization.objects.get_or_create(
            student=self.student,
            course_type='ielts',
            defaults={'is_active': True},
        )
        from portals.tests.group_helpers import create_quiz_category

        category = create_quiz_category('IELTS Cat', 'ielts')
        quiz = Quiz.objects.create(topic='Listening', category=category)
        result = QuizResult.objects.create(
            student=self.student,
            quiz=quiz,
            total_score=8,
            duration_sec=60,
            completed_at=timezone.now(),
        )
        score_row = serialize_quiz_result_as_score(result)
        self.assertEqual(score_row.get('course_type'), 'ielts')
        weekly = WeeklyStudentScore.objects.create(
            student=self.student,
            teacher=self.teacher_a,
            study_group=self.group_a,
            week_start=date(2026, 7, 6),
            score=7,
        )
        grouped = prepare_student_scores_with_groups(
            self.student.pk,
            [score_row],
            [serialize_weekly_score(weekly)],
        )
        self.assertEqual(len(grouped['score_groups']), 2)
        quiz_ids = grouped['quiz_scores'][0]['group_ids']
        self.assertIn(self.group_a.pk, quiz_ids)
        self.assertNotIn(self.group_b.pk, quiz_ids)
        weekly_ids = grouped['weekly_scores'][0]['group_ids']
        self.assertIn(self.group_a.pk, weekly_ids)

    def test_teacher_performance_cards_only_include_teacher_groups(self):
        self.group_a.students.add(self.student)
        self.group_b.students.add(self.student)
        cards = build_student_performance_by_groups(
            self.student.pk,
            teacher_id=self.teacher_a.pk,
        )
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]['group_id'], self.group_a.pk)

    def test_teacher_focus_group_shows_single_course_card(self):
        self.group_a.students.add(self.student)
        self.group_b.students.add(self.student)
        cards = build_student_performance_by_groups(
            self.student.pk,
            teacher_id=self.teacher_a.pk,
            focus_group_id=self.group_a.pk,
        )
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]['group_name'], 'IELTS group A')

    def test_enrich_score_group_counts_accumulates(self):
        groups = [
            {'id': self.group_a.pk, 'name': 'A', 'total_count': 0},
            {'id': self.group_b.pk, 'name': 'B', 'total_count': 0},
        ]
        enrich_score_group_counts(
            groups,
            [{'group_id': self.group_a.pk}, {'group_id': self.group_a.pk}],
            replace=True,
        )
        enrich_score_group_counts(
            groups,
            [{'group_id': self.group_a.pk}, {'group_id': self.group_b.pk}],
        )
        by_id = {row['id']: row['total_count'] for row in groups}
        self.assertEqual(by_id[self.group_a.pk], 3)
        self.assertEqual(by_id[self.group_b.pk], 1)

    def test_parent_group_query_preserves_student_and_group(self):
        parent = ParentProfile.objects.create(
            user=User.objects.create_user(username='multi_parent', password='pass'),
        )
        other = StudentProfile.objects.create(
            user=User.objects.create_user(username='other_child', password='pass'),
        )
        parent.students.add(self.student, other)
        self.group_a.students.add(self.student)
        self.group_b.students.add(self.student)
        request = RequestFactory().get(
            f'/portal/parent/lessons/?student={self.student.pk}&group={self.group_b.pk}'
        )
        child_ctx = {
            'children': [{'id': self.student.pk}, {'id': other.pk}],
            'selected_student': {'id': self.student.pk},
            'student_query': '',
            'week_nav_prefix': '',
        }
        merge_parent_group_context(child_ctx, self.student.pk, request)
        self.assertIn(f'student={self.student.pk}', child_ctx['student_query'])
        self.assertIn(f'group={self.group_b.pk}', child_ctx['student_query'])
        self.assertIn(f'group={self.group_b.pk}', child_ctx['week_nav_prefix'])

    def test_student_lessons_page_shows_group_filter(self):
        self.group_a.students.add(self.student)
        self.group_b.students.add(self.student)
        client = Client()
        portal_client_login(client, self.student_user)
        response = client.get(reverse('portals:student-lessons'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IELTS group A')
        self.assertContains(response, 'SAT group B')
        self.assertContains(response, 'data-score-group')

    def test_student_attendance_page_available(self):
        self.group_a.students.add(self.student)
        self.group_b.students.add(self.student)
        client = Client()
        portal_client_login(client, self.student_user)
        response = client.get(reverse('portals:student-attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-portal-attendance-filter')
        self.assertContains(response, 'IELTS group A')
        self.assertContains(response, 'SAT group B')
        self.assertNotContains(response, 'portal-attendance-hub-cards')

    def test_student_classrooms_page_shows_group_filter(self):
        self.group_a.students.add(self.student)
        self.group_b.students.add(self.student)
        client = Client()
        portal_client_login(client, self.student_user)
        response = client.get(reverse('portals:student-classrooms'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IELTS group A')
        self.assertContains(response, 'SAT group B')
        self.assertContains(response, 'data-score-group')

    def test_teacher_student_duration_tab_shows_group_filter_for_same_teacher(self):
        TeacherCourseSpecialization.objects.create(
            teacher=self.teacher_a,
            course_type='ielts',
        )
        TeacherCourseSpecialization.objects.create(
            teacher=self.teacher_a,
            course_type='sat',
        )
        group_a2 = StudyGroup.objects.create(
            teacher=self.teacher_a,
            name='IELTS group A2',
            max_students=10,
        )
        link_study_group_services(group_a2, 'sat')
        self.group_a.students.add(self.student)
        group_a2.students.add(self.student)

        schedule_a = Schedule.objects.create(
            group=self.group_a,
            weekday=date.today().weekday(),
            start_time=time(10, 0),
            duration_min=90,
        )
        schedule_a2 = Schedule.objects.create(
            group=group_a2,
            weekday=date.today().weekday(),
            start_time=time(14, 0),
            duration_min=90,
        )
        session_date = date.today()
        Attendance.objects.create(
            schedule=schedule_a,
            student=self.student,
            session_date=session_date,
            status=Attendance.Status.PRESENT,
        )
        Attendance.objects.create(
            schedule=schedule_a2,
            student=self.student,
            session_date=session_date,
            status=Attendance.Status.ABSENT,
        )

        client = Client()
        portal_client_login(client, self.teacher_a.user)
        response = client.get(
            reverse('portals:teacher-student-profile', kwargs={'student_pk': self.student.pk}),
            {'tab': 'duration', 'from_group': group_a2.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-profile-group-filter')
        self.assertContains(response, 'IELTS group A')
        self.assertContains(response, 'IELTS group A2')
        self.assertNotContains(response, 'data-profile-duration-group-filter')
        self.assertContains(response, 'Gəlmədi')
        self.assertNotContains(response, 'İştirak etdi')

        ajax = client.get(
            reverse('portals:teacher-student-profile', kwargs={'student_pk': self.student.pk}),
            {'tab': 'duration', 'from_group': self.group_a.pk},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(ajax.status_code, 200)
        self.assertContains(ajax, 'İştirak etdi')
        self.assertNotContains(ajax, 'Gəlmədi')

    def test_teacher_profile_duration_group_helpers(self):
        self.group_a.students.add(self.student)
        group_a2 = StudyGroup.objects.create(
            teacher=self.teacher_a,
            name='IELTS group A2',
            max_students=10,
        )
        group_a2.students.add(self.student)
        groups = get_teacher_student_profile_groups(self.teacher_a.pk, self.student.pk)
        self.assertEqual(len(groups), 2)
        request = RequestFactory().get(
            f'/portal/teacher/students/{self.student.pk}/?from_group={group_a2.pk}&tab=duration'
        )
        self.assertEqual(
            resolve_teacher_profile_group(request, groups),
            group_a2.pk,
        )
        detail = get_teacher_student_attendance_detail(self.teacher_a.pk, self.student.pk)
        filtered = filter_attendance_detail_by_group(detail, self.group_a.pk)
        self.assertEqual(filtered['summary']['total'], 0)
