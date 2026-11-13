"""Students own their services; groups are only names; lessons go to groups or students.

Fictional names only.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from portals.models import (
    Attendance,
    Lesson,
    Quiz,
    QuizQuestion,
    QuizResult,
    StudentCourseSpecialization,
    StudentProfile,
    StudyGroup,
    TeacherCourseSpecialization,
    TeacherProfile,
)
from portals.tests.group_helpers import create_quiz_category
from portals.tests.portal_helpers import ensure_active_portal_services, portal_client_login
from portals.utils.cache_utils import invalidate_model_cache
from portals.utils.lesson_quizzes import get_student_homework_quiz_ids
from portals.utils.portal_services import reset_active_service_snapshot, services_for_portal_codes
from portals.utils.queries import get_student_lessons
from portals.utils.student_courses import (
    get_student_course_type_codes,
    quiz_visible_to_student,
    student_course_enrollment,
    teacher_can_see_quiz_result,
)
from portals.utils.teacher_students import create_teacher_student, teacher_students_qs
from projects.models.service_models import Service

User = get_user_model()


def _refresh():
    """Signals defer cache bumps to on_commit, which TestCase never fires."""
    invalidate_model_cache('StudentCourseSpecialization')
    reset_active_service_snapshot()


class StudentOwnServicesBase(TestCase):
    def setUp(self):
        ensure_active_portal_services('ielts', 'sat')
        Service.objects.get_or_create(
            slug='general-english',
            defaults={'name_az': 'General English', 'name_en': 'General English', 'is_active': True},
        )
        Service.objects.get_or_create(
            slug='gmat',
            defaults={'name_az': 'GMAT', 'name_en': 'GMAT', 'is_active': True},
        )
        reset_active_service_snapshot()
        self.teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='Svc Teacher', password='pass12345'),
        )
        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='ielts')
        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='gmat')
        self.other_teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='Other Teacher', password='pass12345'),
        )
        self.group = StudyGroup.objects.create(teacher=self.teacher, name='Morning', max_students=10)
        # legacy data: a group still has an IELTS course row, which must not matter any more
        self.group.courses.set(services_for_portal_codes(['sat']))

        self.ge_category = create_quiz_category('Grammar', 'general_english')
        self.gmat_category = create_quiz_category('GMAT Verbal', 'gmat')
        self.ge_quiz = self._quiz(self.ge_category, 'Present Simple')
        self.gmat_quiz = self._quiz(self.gmat_category, 'Sentence Correction')
        invalidate_model_cache('Quiz')

    @staticmethod
    def _quiz(category, topic):
        quiz = Quiz.objects.create(category=category, topic=topic)
        QuizQuestion.objects.create(
            quiz=quiz,
            order=1,
            question='<p>?</p>',
            answer_options=['A', 'B'],
            correct_answer='A',
            correct_option_index=0,
        )
        return quiz

    def _student(self, name, *codes, group=None):
        student = StudentProfile.objects.create(
            user=User.objects.create_user(username=name, password='pass12345'),
        )
        for code in codes:
            StudentCourseSpecialization.objects.create(student=student, course_type=code, is_active=True)
        if group is not None:
            group.students.add(student)
        _refresh()
        return student


class GroupIsOnlyANameTests(StudentOwnServicesBase):
    def test_joining_a_group_gives_no_services(self):
        student = self._student('Plain Student')
        self.group.students.add(student)
        _refresh()
        self.assertEqual(get_student_course_type_codes(student.pk), [])

    def test_quiz_follows_the_students_own_service(self):
        student = self._student('GE Student', 'general_english', group=self.group)
        self.assertTrue(quiz_visible_to_student(self.ge_quiz, student.pk))
        self.assertFalse(quiz_visible_to_student(self.gmat_quiz, student.pk))

    def test_student_without_group_belongs_to_teacher_directly(self):
        student = self._student('Lone Student', 'ielts')
        student.teachers.add(self.teacher)
        self.assertIn(student, list(teacher_students_qs(self.teacher.pk)))
        self.assertNotIn(student, list(teacher_students_qs(self.other_teacher.pk)))


class GeneralEnglishDefaultTests(StudentOwnServicesBase):
    def test_ielts_student_gets_general_english_on(self):
        student = self._student('Ielts Student', 'ielts')
        row = student_course_enrollment(student.pk, 'general_english')
        self.assertIsNotNone(row)
        self.assertTrue(row.is_active)

    def test_teacher_switches_general_english_off_and_on(self):
        student = self._student('Toggle Student', 'ielts', group=self.group)
        client = Client()
        portal_client_login(client, self.teacher.user)
        url = reverse(
            'portals:teacher-student-service-toggle',
            kwargs={'student_pk': student.pk, 'code': 'general_english'},
        )
        response = client.post(url, data='{"is_active": false}', content_type='application/json')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertFalse(response.json()['is_active'])
        _refresh()
        self.assertFalse(quiz_visible_to_student(self.ge_quiz, student.pk))

        response = client.post(url, data='{"is_active": true}', content_type='application/json')
        self.assertTrue(response.json()['is_active'])
        _refresh()
        self.assertTrue(quiz_visible_to_student(self.ge_quiz, student.pk))

    def test_other_teacher_cannot_toggle(self):
        student = self._student('Guarded Student', 'ielts', group=self.group)
        client = Client()
        portal_client_login(client, self.other_teacher.user)
        url = reverse(
            'portals:teacher-student-service-toggle',
            kwargs={'student_pk': student.pk, 'code': 'general_english'},
        )
        response = client.post(url, data='{"is_active": false}', content_type='application/json')
        self.assertEqual(response.status_code, 404)


class TeacherCreatesStudentAndGroupTests(StudentOwnServicesBase):
    def test_teacher_creates_student_without_group(self):
        client = Client()
        portal_client_login(client, self.teacher.user)
        response = client.post(
            reverse('portals:teacher-student-create'),
            {'full_name': 'New Lone Student', 'services': ['gmat'], 'group': '', 'password': ''},
        )
        self.assertEqual(response.status_code, 302, getattr(response, 'context', None) and response.context['form'].errors)
        student = StudentProfile.objects.get(user__username='New Lone Student')
        self.assertFalse(student.groups.exists())
        self.assertIn(self.teacher, student.teachers.all())
        self.assertFalse(student.user.has_usable_password())
        _refresh()
        self.assertEqual(get_student_course_type_codes(student.pk), ['gmat'])

    def test_unticked_general_english_stays_off_for_ielts(self):
        student = create_teacher_student(self.teacher.pk, 'Ielts Only', services=['ielts'], group=self.group)
        _refresh()
        row = student_course_enrollment(student.pk, 'general_english')
        self.assertIsNotNone(row)
        self.assertFalse(row.is_active)
        self.assertTrue(student.groups.filter(pk=self.group.pk).exists())

    def test_teacher_creates_a_real_group(self):
        client = Client()
        portal_client_login(client, self.teacher.user)
        response = client.post(reverse('portals:teacher-group-create'), {'name': 'Evening'})
        self.assertEqual(response.status_code, 302)
        group = StudyGroup.objects.get(teacher=self.teacher, name='Evening')
        self.assertFalse(group.is_register_only)

    def test_students_page_filters_by_group(self):
        in_group = self._student('In Group', 'ielts', group=self.group)
        alone = self._student('Alone', 'ielts')
        alone.teachers.add(self.teacher)
        client = Client()
        portal_client_login(client, self.teacher.user)
        page = client.get(reverse('portals:teacher-groups'))
        self.assertContains(page, 'In Group')
        self.assertContains(page, 'Alone')
        only_group = client.get(reverse('portals:teacher-groups') + f'?group={self.group.pk}')
        self.assertContains(only_group, 'In Group')
        self.assertNotContains(only_group, 'data-student-name="alone"')
        no_group = client.get(reverse('portals:teacher-groups') + '?group=none')
        self.assertContains(no_group, 'data-student-name="alone"')
        self.assertNotContains(no_group, 'data-student-name="in group"')
        del in_group


class HomeworkQuizTests(StudentOwnServicesBase):
    def test_direct_lesson_quiz_opens_without_the_service(self):
        student = self._student('Hw Student', 'ielts')  # no GMAT service, no group
        student.teachers.add(self.teacher)
        lesson = Lesson.objects.create(teacher=self.teacher, subject='gmat', name='Hw', group=None)
        lesson.students.add(student)
        lesson.quizzes.add(self.gmat_quiz)
        invalidate_model_cache('Lesson')

        self.assertIn(self.gmat_quiz.pk, get_student_homework_quiz_ids(student.pk))
        self.assertTrue(quiz_visible_to_student(self.gmat_quiz, student.pk))
        self.assertEqual([row['id'] for row in get_student_lessons(student.pk)], [lesson.pk])

        client = Client()
        portal_client_login(client, student.user)
        page = client.get(reverse('portals:student-lesson-detail', kwargs={'pk': lesson.pk}))
        self.assertContains(page, 'data-lesson-homework-quizzes')
        self.assertContains(page, reverse('portals:student-quiz-take', kwargs={'pk': self.gmat_quiz.pk}))
        take = client.get(reverse('portals:student-quiz-take', kwargs={'pk': self.gmat_quiz.pk}))
        self.assertEqual(take.status_code, 200)

    def test_group_lesson_quiz_reaches_group_members_only(self):
        member = self._student('Member', 'ielts', group=self.group)
        outsider = self._student('Outsider', 'ielts')
        lesson = Lesson.objects.create(teacher=self.teacher, subject='gmat', name='Group hw', group=self.group)
        lesson.quizzes.add(self.gmat_quiz)
        invalidate_model_cache('Lesson')
        self.assertTrue(quiz_visible_to_student(self.gmat_quiz, member.pk))
        self.assertFalse(quiz_visible_to_student(self.gmat_quiz, outsider.pk))

    def test_teacher_sees_homework_quiz_result_on_lesson_page(self):
        student = self._student('Result Student', 'ielts')
        student.teachers.add(self.teacher)
        lesson = Lesson.objects.create(teacher=self.teacher, subject='gmat', name='Hw result', group=None)
        lesson.students.add(student)
        lesson.quizzes.add(self.gmat_quiz)
        invalidate_model_cache('Lesson')
        result = QuizResult.objects.create(student=student, quiz=self.gmat_quiz, total_score=1)
        self.assertTrue(teacher_can_see_quiz_result(self.teacher.pk, student.pk, self.gmat_quiz))
        client = Client()
        portal_client_login(client, self.teacher.user)
        page = client.get(reverse('portals:teacher-lesson-detail', kwargs={'pk': lesson.pk}))
        self.assertContains(page, '1 / 1')
        self.assertContains(page, reverse('portals:teacher-score-detail', kwargs={'result_pk': result.pk}))

    def test_teacher_results_list_includes_homework_quiz(self):
        from portals.utils.student_courses import filter_quiz_results_for_teacher

        direct = self._student('List Direct', 'ielts')
        direct.teachers.add(self.teacher)
        member = self._student('List Member', 'ielts', group=self.group)
        stranger = self._student('List Stranger', 'ielts')
        direct_lesson = Lesson.objects.create(teacher=self.teacher, subject='gmat', name='D', group=None)
        direct_lesson.students.add(direct)
        direct_lesson.quizzes.add(self.gmat_quiz)
        group_lesson = Lesson.objects.create(teacher=self.teacher, subject='gmat', name='G', group=self.group)
        group_lesson.quizzes.add(self.gmat_quiz)
        invalidate_model_cache('Lesson')
        rows = [
            QuizResult.objects.create(student=student, quiz=self.gmat_quiz, total_score=1)
            for student in (direct, member, stranger)
        ]
        visible = {row.student_id for row in filter_quiz_results_for_teacher(rows, self.teacher.pk)}
        self.assertEqual(visible, {direct.pk, member.pk})

    def test_lesson_form_sends_to_chosen_students(self):
        from portals.teacher_forms import TeacherLessonForm

        student = self._student('Chosen', 'ielts')
        student.teachers.add(self.teacher)
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'name': 'Direct unit',
                'lesson_date': date.today().isoformat(),
                'students': [student.pk],
                'quizzes': [self.gmat_quiz.pk],
                'service': 'gmat',
                'new_video_urls': ['https://www.youtube.com/watch?v=test12345'],
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        lessons = form.save_for_groups(self.teacher)
        self.assertEqual(len(lessons), 1)
        self.assertIsNone(lessons[0].group_id)
        self.assertEqual(list(lessons[0].students.all()), [student])
        self.assertEqual(list(lessons[0].quizzes.all()), [self.gmat_quiz])
        self.assertEqual(lessons[0].subject, 'gmat')

    def test_lesson_form_needs_a_group_or_a_student(self):
        from portals.teacher_forms import TeacherLessonForm

        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'name': 'Nobody',
                'lesson_date': date.today().isoformat(),
                'new_video_urls': ['https://www.youtube.com/watch?v=test12345'],
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn('groups', form.errors)


class InactiveStudentTests(StudentOwnServicesBase):
    def test_inactive_student_cannot_sign_in(self):
        student = self._student('Paused Student', 'ielts', group=self.group)
        StudentProfile.objects.filter(pk=student.pk).update(is_active=False)
        response = Client().post(
            reverse('portals:login'),
            {'username': 'Paused Student', 'password': 'pass12345'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('portals:login'), response['Location'])

    def test_existing_session_ends_when_deactivated(self):
        student = self._student('Session Student', 'ielts', group=self.group)
        client = Client()
        portal_client_login(client, student.user)
        self.assertEqual(client.get(reverse('portals:student-dashboard')).status_code, 200)
        StudentProfile.objects.filter(pk=student.pk).update(is_active=False)
        response = client.get(reverse('portals:student-dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_inactive_student_hidden_from_students_page_but_kept_on_register(self):
        from portals.utils.teacher_attendance_register import (
            build_teacher_attendance_register,
            teacher_main_register,
        )

        student = self._student('Hidden Student', 'ielts', group=self.group)
        Attendance.objects.create(
            group=self.group,
            student=student,
            session_date=date(2026, 11, 3),
            status=Attendance.Status.PRESENT,
        )
        StudentProfile.objects.filter(pk=student.pk).update(is_active=False)
        invalidate_model_cache('StudentProfile')

        client = Client()
        portal_client_login(client, self.teacher.user)
        page = client.get(reverse('portals:teacher-groups'))
        self.assertNotContains(page, 'Hidden Student')

        main = teacher_main_register(self.teacher)
        register = build_teacher_attendance_register(self.teacher, year=2026, month=11, group=main)
        names = {row['name'] for row in register['students']}
        self.assertIn('Hidden Student', names)
        group_register = build_teacher_attendance_register(self.teacher, year=2026, month=11, group=self.group)
        row = next(row for row in group_register['students'] if row['name'] == 'Hidden Student')
        self.assertFalse(row['is_active'])
        self.assertEqual(row['present_count'], 1)

    def test_admin_list_can_switch_student_off(self):
        admin = User.objects.create_superuser(username='svc_admin', password='pass12345', email='a@example.com')
        student = self._student('Admin Toggle', 'ielts')
        client = Client()
        client.force_login(admin)
        page = client.get(reverse('admin:portals_studentprofile_changelist'))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, f'name="form-0-is_active"')
        del student


class RegisterAddsRealStudentsTests(StudentOwnServicesBase):
    def test_register_name_becomes_a_real_student(self):
        from portals.utils.teacher_attendance_register import add_register_guest, teacher_main_register

        result = add_register_guest(group=self.group, name='Register Student')
        self.assertTrue(result['ok'], result)
        student = StudentProfile.objects.get(pk=result['student']['id'])
        self.assertTrue(student.groups.filter(pk=self.group.pk).exists())
        self.assertIn(self.teacher, student.teachers.all())
        _refresh()
        # teacher teaches IELTS + GMAT: the new student gets those, and General English for IELTS
        codes = set(get_student_course_type_codes(student.pk))
        self.assertTrue({'ielts', 'gmat', 'general_english'} <= codes, codes)

        again = add_register_guest(group=teacher_main_register(self.teacher), name='register student')
        self.assertTrue(again['ok'])
        self.assertFalse(again['created'])
        self.assertEqual(again['student']['id'], student.pk)

    def test_someone_elses_name_is_refused(self):
        from portals.utils.teacher_attendance_register import add_register_guest

        result = add_register_guest(group=self.group, name='Other Teacher')
        self.assertFalse(result['ok'])
        self.assertEqual(result['error'], 'name_taken')


class OfferNotificationTargetingTests(StudentOwnServicesBase):
    def test_service_filter_uses_students_own_services(self):
        from django.contrib.admin.sites import site

        from portals.models import OfferNotification, OfferNotificationDelivery

        gmat_student = self._student('Offer Gmat', 'gmat', group=self.group)
        ielts_student = self._student('Offer Ielts', 'ielts', group=self.group)
        paused = self._student('Offer Paused', 'gmat')
        StudentProfile.objects.filter(pk=paused.pk).update(is_active=False)

        offer = OfferNotification.objects.create(
            name='GMAT offer',
            description='-',
            target_role=OfferNotification.TargetRole.STUDENT,
        )
        offer.services.set(services_for_portal_codes(['gmat']))
        site._registry[OfferNotification]._send_notifications(offer)

        delivered = set(
            OfferNotificationDelivery.objects.filter(offer_notification=offer)
            .values_list('student_id', flat=True)
        )
        self.assertEqual(delivered, {gmat_student.pk})
        del ielts_student
