from datetime import timedelta

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from portals.models import (
    Quiz,
    QuizCategory,
    QuizResult,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionGroup,
    ReadingQuestionType,
)
from portals.tests.test_quiz_visibility import QuizVisibilityTests
from portals.utils.queries import get_student_reading_quiz_take_data, serialize_quiz
from portals.utils.quiz_reading_score import score_reading_question, score_reading_quiz
from portals.utils.quiz_submit import submit_reading_quiz_attempt


class QuizReadingTests(QuizVisibilityTests):
    def _create_reading_quiz(self, *, topic='IELTS Reading Test'):
        quiz = Quiz.objects.create(
            category=self.ielts_category,
            topic=topic,
            is_reading=True,
            is_time_limited=True,
            time_limit_minutes=60,
        )
        passage = ReadingPassage.objects.create(
            quiz=quiz,
            order=1,
            title='Passage 1',
            body='<p>Climate change affects global weather patterns.</p>',
        )
        ReadingQuestion.objects.create(
            passage=passage,
            order=1,
            question_type=ReadingQuestionType.MCQ,
            question='<p>What is the passage mainly about?</p>',
            answer_options=['Weather', 'Climate', 'Travel', 'Food'],
            correct_answer='Climate',
        )
        ReadingQuestion.objects.create(
            passage=passage,
            order=2,
            question_type=ReadingQuestionType.TFNG,
            question='<p>The passage mentions climate change.</p>',
            correct_answer='True',
        )
        ReadingQuestion.objects.create(
            passage=passage,
            order=3,
            question_type=ReadingQuestionType.SENTENCE_COMPLETION,
            question='<p>Climate change affects global ____ patterns.</p>',
            correct_answer='weather',
            question_config={'case_insensitive': True, 'word_limit': 1},
        )
        group = ReadingQuestionGroup.objects.create(
            passage=passage,
            order=1,
            title='Matching headings',
            question_type=ReadingQuestionType.MATCHING_HEADINGS,
            option_pool=['i. Weather systems', 'ii. Global warming', 'iii. Travel tips'],
        )
        ReadingQuestion.objects.create(
            passage=passage,
            group=group,
            order=4,
            question_type=ReadingQuestionType.MATCHING_HEADINGS,
            question='<p>Paragraph A</p>',
            correct_answer='ii. Global warming',
        )
        return quiz

    def test_only_one_format_allowed_with_reading(self):
        quiz = Quiz(
            category=self.ielts_category,
            topic='Invalid',
            is_reading=True,
            is_listening=True,
        )
        with self.assertRaises(ValidationError):
            quiz.full_clean()

    def test_serialize_quiz_includes_reading_mode(self):
        quiz = self._create_reading_quiz()
        data = serialize_quiz(quiz)
        self.assertTrue(data['is_reading'])
        self.assertFalse(data['is_manual_grading'])
        self.assertFalse(data['is_variant_quiz'])
        self.assertEqual(data['grading_mode'], 'reading')
        self.assertEqual(data['question_count'], 4)

    def test_reading_passage_requires_reading_quiz(self):
        passage = ReadingPassage(
            quiz=self.ielts_quiz,
            body='Some text',
        )
        with self.assertRaises(ValidationError):
            passage.full_clean()

    def test_scoring_choice_and_text(self):
        quiz = self._create_reading_quiz()
        questions = list(
            ReadingQuestion.objects.filter(passage__quiz=quiz).order_by('order', 'id'),
        )
        self.assertTrue(score_reading_question(questions[0], 1))
        self.assertFalse(score_reading_question(questions[0], 0))
        self.assertTrue(score_reading_question(questions[1], 0))
        self.assertTrue(score_reading_question(questions[2], 'Weather'))
        self.assertFalse(score_reading_question(questions[2], 'weather patterns'))

    def test_scoring_matching_group_pool(self):
        quiz = self._create_reading_quiz()
        matching = ReadingQuestion.objects.filter(
            question_type=ReadingQuestionType.MATCHING_HEADINGS,
        ).first()
        self.assertTrue(score_reading_question(matching, 1))

    def test_submit_reading_quiz_attempt(self):
        quiz = self._create_reading_quiz()
        questions = list(
            ReadingQuestion.objects.filter(passage__quiz=quiz).order_by('order', 'id'),
        )
        answers = {
            str(questions[0].pk): 1,
            str(questions[1].pk): 0,
            str(questions[2].pk): 'weather',
            str(questions[3].pk): 1,
        }
        outcome = submit_reading_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=quiz.pk,
            given_answers=answers,
            duration_sec=120,
            session_started_at='2026-07-03T10:00:00+00:00',
        )
        self.assertTrue(outcome['success'])
        self.assertEqual(outcome['total_score'], 4)
        self.assertEqual(outcome['max_score'], 4)
        result = QuizResult.objects.filter(student=self.student, quiz=quiz).order_by('-completed_at', '-id').first()
        self.assertEqual(result.total_score, 4)
        self.assertIsNone(result.reviewed_at)

    def test_submit_reading_quiz_allows_partial_answers(self):
        quiz = self._create_reading_quiz()
        questions = list(
            ReadingQuestion.objects.filter(passage__quiz=quiz).order_by('order', 'id'),
        )
        outcome = submit_reading_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=quiz.pk,
            given_answers={str(questions[0].pk): 1},
            duration_sec=30,
            session_started_at='2026-07-03T10:00:00+00:00',
            completion_trigger='auto_leave',
        )
        self.assertTrue(outcome['success'])
        self.assertEqual(outcome['total_score'], 1)
        self.assertEqual(outcome['max_score'], 4)
        self.assertNotIn('pending_review', outcome)
        self.assertEqual(len(outcome['breakdown']), 4)

    def test_get_student_reading_quiz_take_data(self):
        quiz = self._create_reading_quiz()
        data = get_student_reading_quiz_take_data(self.student.pk, quiz.pk)
        self.assertIsNotNone(data)
        self.assertEqual(len(data['reading_sections']), 1)
        self.assertEqual(data['response_question_count'], 4)
        self.assertEqual(len(data['questions']), 4)
        self.assertFalse(data['view_only'])
        self.assertFalse(data['is_pending_review'])
        self.assertIsNone(data['result_id'])

    def test_get_student_reading_quiz_take_data_after_attempt_allows_retake(self):
        quiz = self._create_reading_quiz()
        submit_reading_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=quiz.pk,
            given_answers={},
            duration_sec=10,
            session_started_at=timezone.now().isoformat(),
        )
        data = get_student_reading_quiz_take_data(self.student.pk, quiz.pk)
        self.assertIsNotNone(data)
        self.assertFalse(data['view_only'])
        self.assertFalse(data['is_pending_review'])
        self.assertIsNotNone(data['result_id'])

    def test_reading_quiz_does_not_require_teacher_review(self):
        quiz = self._create_reading_quiz()
        self.assertFalse(quiz.requires_teacher_review)

    def test_build_reading_sections_inline_group_instructions(self):
        from portals.utils.quiz_reading import build_reading_sections_for_quiz

        quiz = self._create_reading_quiz()
        sections = build_reading_sections_for_quiz(quiz.pk)
        questions = sections[0]['questions']
        self.assertEqual(len(questions), 4)
        self.assertFalse(questions[0].get('group_start'))
        self.assertFalse(questions[1].get('group_start'))
        self.assertFalse(questions[2].get('group_start'))
        self.assertTrue(questions[3].get('group_start'))
        self.assertEqual(questions[3]['group_instructions']['title'], 'Matching headings')

    def test_student_reading_take_view(self):
        quiz = self._create_reading_quiz()
        self.client.force_login(self.student_user)
        url = reverse('portals:student-reading-quiz-take', kwargs={'pk': quiz.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passage 1')
        self.assertContains(response, 'data-quiz-reading-take')

    def test_reading_cancel_auto_completes_active_attempt(self):
        from portals.tests.test_quiz_submit import _portal_client_login

        quiz = self._create_reading_quiz()
        client = self.client_class()
        _portal_client_login(client, self.student_user)

        start_url = reverse('portals:student-quiz-start', kwargs={'pk': quiz.pk})
        cancel_url = reverse('portals:student-quiz-cancel', kwargs={'pk': quiz.pk})

        start_response = client.post(start_url, content_type='application/json')
        self.assertEqual(start_response.status_code, 200)

        response = client.get(cancel_url)
        self.assertEqual(response.status_code, 302)

        result = QuizResult.objects.get(student=self.student, quiz=quiz)
        self.assertEqual(result.completion_trigger, QuizResult.CompletionTrigger.AUTO_LEAVE)
        self.assertEqual(result.duration_sec, 0)

    def test_score_reading_quiz_breakdown(self):
        quiz = self._create_reading_quiz()
        questions = list(
            ReadingQuestion.objects.filter(passage__quiz=quiz).order_by('order', 'id'),
        )
        score, max_score, breakdown = score_reading_quiz(
            quiz,
            {
                str(questions[0].pk): 1,
                str(questions[1].pk): 2,
                str(questions[2].pk): 'weather',
                str(questions[3].pk): 0,
            },
        )
        self.assertEqual(max_score, 4)
        self.assertEqual(score, 2)
        self.assertEqual(len(breakdown), 4)

    def test_reading_correct_answer_hidden_until_results(self):
        from portals.utils.quiz_reading import build_reading_sections_for_quiz, reading_correct_answer_display

        quiz = self._create_reading_quiz()
        question = ReadingQuestion.objects.filter(
            passage__quiz=quiz,
            question_type=ReadingQuestionType.SENTENCE_COMPLETION,
        ).first()
        question.question_config = {
            'case_insensitive': True,
            'accept_alternatives': ['scent'],
        }
        question.correct_answer = 'smell'
        question.save()

        take_sections = build_reading_sections_for_quiz(
            quiz.pk,
            response_map={str(question.pk): 'scent'},
        )
        take_row = take_sections[0]['questions'][2]
        self.assertNotIn('correct_answer', take_row)
        self.assertEqual(reading_correct_answer_display(question), 'smell (also: scent)')

        result_sections = build_reading_sections_for_quiz(
            quiz.pk,
            response_map={str(question.pk): 'scent'},
            use_admin_answer_keys=True,
        )
        result_row = result_sections[0]['questions'][2]
        self.assertEqual(result_row['correct_answer'], 'smell')
        self.assertTrue(result_row['is_correct'])

    def test_score_detail_uses_admin_answer_keys(self):
        from portals.utils.notifications import get_score_detail_for_student

        quiz = self._create_reading_quiz()
        questions = list(
            ReadingQuestion.objects.filter(passage__quiz=quiz).order_by('order', 'id'),
        )
        submit_reading_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=quiz.pk,
            given_answers={str(questions[2].pk): 'weather'},
            duration_sec=10,
            session_started_at=timezone.now().isoformat(),
        )
        result = QuizResult.objects.get(student=self.student, quiz=quiz)
        detail = get_score_detail_for_student(self.student.pk, result.pk)
        gap_row = detail['reading_sections'][0]['questions'][2]
        self.assertEqual(gap_row['correct_answer'], 'weather')
        self.assertTrue(gap_row['is_correct'])


class ReadingQuestionAdminFieldConfigTests(QuizReadingTests):
    def test_mcq_shows_answer_options_hides_group_ref(self):
        from portals.utils.quiz_reading_admin import reading_question_admin_field_config

        config = reading_question_admin_field_config(ReadingQuestionType.MCQ)
        self.assertIn('answer_options', config['show_fields'])
        self.assertIn('group_ref', config['hide_fields'])
        self.assertIn('group_ref', config['clear_fields'])

    def test_matching_shows_group_ref_hides_answer_options(self):
        from portals.utils.quiz_reading_admin import reading_question_admin_field_config

        config = reading_question_admin_field_config(ReadingQuestionType.MATCHING_HEADINGS)
        self.assertIn('group_ref', config['show_fields'])
        self.assertIn('answer_options', config['hide_fields'])

    def test_text_shows_answer_fields(self):
        from portals.utils.quiz_reading_admin import reading_question_admin_field_config

        config = reading_question_admin_field_config(ReadingQuestionType.SENTENCE_COMPLETION)
        self.assertIn('question_config', config['show_fields'])
        self.assertIn('accept_alternatives_text', config['show_fields'])
        self.assertIn('word_limit', config['show_fields'])
        self.assertIn('answer_options', config['hide_fields'])

    def test_reading_question_admin_form_stores_alternatives(self):
        from portals.admin.quiz_forms import ReadingQuestionAdminForm

        quiz = self._create_reading_quiz()
        passage = quiz.reading_passages.first()
        form = ReadingQuestionAdminForm(
            data={
                'passage': passage.pk,
                'order': 5,
                'question_type': ReadingQuestionType.SENTENCE_COMPLETION,
                'question': '<p>Some seabirds identify their home colony partly by its ____.</p>',
                'correct_answer': 'smell',
                'word_limit': 1,
                'case_insensitive': True,
                'accept_alternatives_text': 'scent\nodour',
                'answer_options': '[]',
                'question_config': '{}',
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        question = form.save(commit=False)
        question.passage = passage
        question.save()
        question.refresh_from_db()
        self.assertEqual(question.correct_answer, 'smell')
        self.assertEqual(question.question_config['word_limit'], 1)
        self.assertEqual(question.question_config['accept_alternatives'], ['scent', 'odour'])

    def test_question_type_fields_admin_view(self):
        from django.contrib.auth import get_user_model

        quiz = self._create_reading_quiz()
        passage = quiz.reading_passages.first()
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username='readingadmin',
            email='readingadmin@test.com',
            password='testpass123',
        )
        self.client.force_login(admin_user)
        url = reverse('admin:portals_readingpassage_question_type_fields')
        response = self.client.post(url, {'question_type': ReadingQuestionType.TFNG})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['question_type'], ReadingQuestionType.TFNG)
        self.assertIn('answer_options', payload['hide_fields'])
        change_url = reverse('admin:portals_readingpassage_change', args=[passage.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
