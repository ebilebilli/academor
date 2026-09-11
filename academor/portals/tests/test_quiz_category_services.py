from django.test import TestCase
from django.utils.translation import override

from portals.models import (
    Quiz,
    QuizCategory,
    QuizQuestion,
    StudentCourseSpecialization,
    StudentProfile,
    StudyGroup,
    TeacherCourseSpecialization,
    TeacherProfile,
)
from portals.tests.group_helpers import create_quiz_category, link_study_group_services
from portals.utils.portal_services import reset_active_service_snapshot
from portals.utils.queries import serialize_quiz_category
from portals.utils.quiz_category_services import (
    ensure_quiz_category,
    expand_generic_exam_track_enrollments,
    quiz_category_display_name,
    relink_sat_math_and_verbal_categories,
)
from portals.utils.student_courses import quiz_visible_to_student
from projects.models.service_models import Service
from django.contrib.auth import get_user_model

User = get_user_model()


class QuizCategoryServiceNameTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            slug='english-language-course',
            name_az='İngilis dili kursu',
            name_en='English language course',
            is_active=True,
        )
        reset_active_service_snapshot()
        self.category = QuizCategory.objects.create(name='English language course')
        self.category.services.add(self.service)

    def test_top_level_category_keeps_its_explicit_name(self):
        with override('az'):
            self.assertEqual(
                quiz_category_display_name(self.category),
                'English language course',
            )
            self.assertEqual(
                serialize_quiz_category(self.category)['name'],
                'English language course',
            )

    def test_top_level_category_without_name_falls_back_to_service_name(self):
        self.category.name = ''
        self.category.save(update_fields=['name'])
        with override('az'):
            self.assertEqual(
                quiz_category_display_name(self.category),
                'İngilis dili kursu',
            )

    def test_nested_category_keeps_its_own_name(self):
        child = QuizCategory.objects.create(name='Reading', parent=self.category)
        child.services.add(self.service)
        with override('az'):
            self.assertEqual(quiz_category_display_name(child), 'Reading')


class SatVerbalMathSeparationTests(TestCase):
    def setUp(self):
        self.verbal_service = Service.objects.create(
            slug='sat-verbal',
            name_az='SAT Verbal kursu',
            name_en='SAT Verbal Course',
            is_active=True,
        )
        self.math_service = Service.objects.create(
            slug='sat-math',
            name_az='SAT Math kursu',
            name_en='SAT Math Course',
            is_active=True,
        )
        reset_active_service_snapshot()

        self.teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='sat_sep_teacher', password='pass'),
        )
        self.student = StudentProfile.objects.create(
            user=User.objects.create_user(username='sat_sep_student', password='pass'),
        )
        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='SAT Verbal A',
            max_students=10,
        )
        link_study_group_services(self.group, 'sat-verbal')
        self.group.students.add(self.student)
        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='sat-verbal')

    def test_ensure_sat_math_loader_links_only_math_service(self):
        category, _ = ensure_quiz_category('sat', 'SAT Math')
        slugs = set(category.services.values_list('slug', flat=True))
        self.assertEqual(slugs, {'sat-math'})

    def test_ensure_sat_verbal_loader_links_only_verbal_service(self):
        category, _ = ensure_quiz_category('sat', 'SAT Reading and Writing')
        slugs = set(category.services.values_list('slug', flat=True))
        self.assertEqual(slugs, {'sat-verbal'})

    def test_verbal_student_does_not_see_math_quiz(self):
        verbal_category = create_quiz_category('SAT Verbal Course', 'sat-verbal')
        math_category = create_quiz_category('SAT Math', 'sat-math')
        verbal_quiz = Quiz.objects.create(
            category=verbal_category,
            topic='SAT Practice Test 1 Reading and Writing',
        )
        math_quiz = Quiz.objects.create(
            category=math_category,
            topic='SAT Practice Test 1 Math',
        )
        self.assertTrue(quiz_visible_to_student(verbal_quiz, self.student.pk))
        self.assertFalse(quiz_visible_to_student(math_quiz, self.student.pk))

    def test_relink_moves_math_quizzes_out_of_verbal_category(self):
        mixed = QuizCategory.objects.create(name='SAT Verbal Course')
        mixed.services.set([self.verbal_service, self.math_service])
        verbal_quiz = Quiz.objects.create(
            category=mixed,
            topic='SAT Practice Test 1 Reading and Writing',
            is_sat=True,
            sat_section='reading',
        )
        math_quiz = Quiz.objects.create(
            category=mixed,
            topic='SAT Practice Test 1 Math',
            is_sat=True,
            sat_section='algebra',
        )
        QuizQuestion.objects.create(
            quiz=verbal_quiz,
            order=1,
            question='<p>RW?</p>',
            answer_options=['A', 'B'],
            correct_answer='A',
            correct_option_index=0,
        )
        QuizQuestion.objects.create(
            quiz=math_quiz,
            order=1,
            question='<p>2+2?</p>',
            answer_options=['3', '4'],
            correct_answer='4',
            correct_option_index=1,
        )

        result = relink_sat_math_and_verbal_categories()
        self.assertFalse(result.get('skipped'))
        math_quiz.refresh_from_db()
        verbal_quiz.refresh_from_db()
        mixed.refresh_from_db()

        math_slugs = set(math_quiz.category.services.values_list('slug', flat=True))
        verbal_slugs = set(verbal_quiz.category.services.values_list('slug', flat=True))
        self.assertEqual(math_slugs, {'sat-math'})
        self.assertEqual(verbal_slugs, {'sat-verbal'})
        self.assertNotEqual(math_quiz.category_id, verbal_quiz.category_id)
        self.assertEqual(set(mixed.services.values_list('slug', flat=True)), {'sat-verbal'})

    def test_generic_sat_enrollment_expands_from_group_service(self):
        Service.objects.create(
            slug='sat-mock-test',
            name_az='SAT Mock',
            name_en='SAT Mock',
            is_active=True,
            sat_mock_test=True,
        )
        reset_active_service_snapshot()
        StudentCourseSpecialization.objects.filter(student=self.student).delete()
        StudentCourseSpecialization.objects.create(
            student=self.student,
            course_type='sat',
            is_active=True,
        )
        expand_generic_exam_track_enrollments()
        codes = set(
            StudentCourseSpecialization.objects.filter(
                student=self.student,
                is_active=True,
            ).values_list('course_type', flat=True)
        )
        self.assertIn('sat-verbal', codes)
        self.assertNotIn('sat', codes)
        self.assertNotIn('sat-math', codes)
