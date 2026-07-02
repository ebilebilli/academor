from django.core.exceptions import ValidationError
from django.utils import timezone

from portals.models import Quiz, QuizCategory, QuizQuestion, QuizResult
from portals.tests.test_quiz_visibility import QuizVisibilityTests


class QuizManualGradingTests(QuizVisibilityTests):
    def test_only_one_manual_mode_allowed(self):
        self.ielts_quiz.is_listening = True
        self.ielts_quiz.is_essay = True
        with self.assertRaises(ValidationError):
            self.ielts_quiz.full_clean()

    def test_manual_quiz_question_skips_variant_validation(self):
        category = QuizCategory.objects.create(service='ielts', name='Essay cat')
        quiz = Quiz.objects.create(
            category=category,
            topic='Essay task',
            is_essay=True,
        )
        question = QuizQuestion(
            quiz=quiz,
            order=1,
            prompt_type=QuizQuestion.PromptType.TEXT,
            question='Write about your hometown.',
            answer_options=[],
            correct_answer='',
        )
        question.full_clean()
        question.save()
        question.refresh_from_db()
        self.assertEqual(question.answer_options, [])
        self.assertEqual(question.correct_answer, '')

    def test_quiz_result_pending_until_reviewed(self):
        self.ielts_quiz.is_essay = True
        self.ielts_quiz.save(update_fields=['is_essay'])
        result = QuizResult.objects.create(
            student=self.student,
            quiz=self.ielts_quiz,
            student_submission='My essay text.',
            total_score=None,
        )
        self.assertTrue(result.is_pending_review)

        result.reviewed_at = timezone.now()
        result.teacher_feedback = 'Good structure; fix article errors.'
        result.total_score = 7.5
        result.save()
        self.assertFalse(result.is_pending_review)

    def test_serialize_quiz_includes_grading_mode(self):
        from portals.utils.queries import serialize_quiz

        self.ielts_quiz.is_listening = True
        self.ielts_quiz.save(update_fields=['is_listening'])
        data = serialize_quiz(self.ielts_quiz)
        self.assertTrue(data['is_manual_grading'])
        self.assertEqual(data['grading_mode'], 'listening')

    def test_manual_quiz_result_max_value_is_ten(self):
        from portals.utils.queries import serialize_quiz_result

        self.ielts_quiz.is_essay = True
        self.ielts_quiz.save(update_fields=['is_essay'])
        QuizQuestion.objects.create(
            quiz=self.ielts_quiz,
            order=1,
            question='Prompt one',
            answer_options=[],
            correct_answer='',
        )
        QuizQuestion.objects.create(
            quiz=self.ielts_quiz,
            order=2,
            question='Prompt two',
            answer_options=[],
            correct_answer='',
        )
        result = QuizResult.objects.create(
            student=self.student,
            quiz=self.ielts_quiz,
            student_submission='Answer text.',
            total_score=8,
            reviewed_at=timezone.now(),
        )
        data = serialize_quiz_result(result)
        self.assertEqual(data['max_value'], 10)

    def test_teacher_review_accepts_decimal_score(self):
        from portals.utils.quiz_submit import submit_teacher_quiz_review

        self.ielts_quiz.is_speaking = True
        self.ielts_quiz.save(update_fields=['is_speaking'])
        result = QuizResult.objects.create(
            student=self.student,
            quiz=self.ielts_quiz,
            student_submission='Speaking notes.',
        )
        outcome = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=result.pk,
            total_score='7.25',
            teacher_feedback='Good pronunciation.',
        )
        self.assertTrue(outcome['success'])
        result.refresh_from_db()
        self.assertEqual(result.total_score, 7.25)

    def test_teacher_review_rejects_score_above_ten(self):
        from portals.utils.quiz_submit import submit_teacher_quiz_review

        self.ielts_quiz.is_speaking = True
        self.ielts_quiz.save(update_fields=['is_speaking'])
        result = QuizResult.objects.create(
            student=self.student,
            quiz=self.ielts_quiz,
            student_submission='Speaking notes.',
        )
        outcome = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=result.pk,
            total_score=11,
            teacher_feedback='Too high.',
        )
        self.assertFalse(outcome['success'])

        outcome = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=result.pk,
            total_score=8.5,
            teacher_feedback='Good fluency.',
        )
        self.assertTrue(outcome['success'])
        result.refresh_from_db()
        self.assertEqual(result.total_score, 8.5)

    def test_teacher_cannot_review_twice(self):
        from portals.utils.quiz_submit import submit_teacher_quiz_review

        self.ielts_quiz.is_essay = True
        self.ielts_quiz.save(update_fields=['is_essay'])
        result = QuizResult.objects.create(
            student=self.student,
            quiz=self.ielts_quiz,
            student_submission='Essay text.',
        )
        first = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=result.pk,
            total_score=7,
            teacher_feedback='First review.',
        )
        self.assertTrue(first['success'])

        second = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=result.pk,
            total_score=9,
            teacher_feedback='Changed review.',
        )
        self.assertFalse(second['success'])
        result.refresh_from_db()
        self.assertEqual(result.total_score, 7)
        self.assertEqual(result.teacher_feedback, 'First review.')

    def test_student_cannot_edit_pending_manual_submission(self):
        from portals.utils.queries import get_student_manual_quiz_take_data
        from portals.utils.quiz_submit import (
            student_can_take_manual_quiz,
            submit_manual_quiz_attempt,
        )

        self.ielts_quiz.is_essay = True
        self.ielts_quiz.save(update_fields=['is_essay'])
        question = QuizQuestion.objects.create(
            quiz=self.ielts_quiz,
            order=1,
            question='Write your essay.',
        )
        submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.ielts_quiz.pk,
            given_answers={str(question.pk): 'First draft.'},
        )

        self.assertFalse(student_can_take_manual_quiz(self.student.pk, self.ielts_quiz.pk))
        data = get_student_manual_quiz_take_data(self.student.pk, self.ielts_quiz.pk)
        self.assertIsNotNone(data)
        self.assertTrue(data['view_only'])
        self.assertTrue(data['is_pending_review'])
        self.assertEqual(data['questions'][0]['student_answer'], 'First draft.')

        retry = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.ielts_quiz.pk,
            given_answers={str(question.pk): 'Edited draft.'},
        )
        self.assertFalse(retry['success'])
        result = QuizResult.objects.get(student=self.student, quiz=self.ielts_quiz)
        self.assertEqual(result.given_answers.get(str(question.pk)), 'First draft.')

    def test_student_can_retake_manual_quiz_after_teacher_review(self):
        from portals.utils.queries import get_student_manual_quiz_take_data
        from portals.utils.quiz_submit import (
            student_can_take_manual_quiz,
            submit_manual_quiz_attempt,
            submit_teacher_quiz_review,
        )

        self.ielts_quiz.is_essay = True
        self.ielts_quiz.save(update_fields=['is_essay'])
        question = QuizQuestion.objects.create(
            quiz=self.ielts_quiz,
            order=1,
            question='Write your essay.',
        )
        submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.ielts_quiz.pk,
            given_answers={str(question.pk): 'First draft.'},
        )

        result = QuizResult.objects.get(student=self.student, quiz=self.ielts_quiz)
        submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=result.pk,
            total_score=8,
            teacher_feedback='Reviewed.',
        )

        self.assertTrue(student_can_take_manual_quiz(self.student.pk, self.ielts_quiz.pk))
        self.assertIsNotNone(get_student_manual_quiz_take_data(self.student.pk, self.ielts_quiz.pk))

        retake = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.ielts_quiz.pk,
            given_answers={str(question.pk): 'Retake attempt.'},
        )
        self.assertTrue(retake['success'])
        result.refresh_from_db()
        self.assertEqual(result.given_answers.get(str(question.pk)), 'Retake attempt.')
        self.assertIsNone(result.reviewed_at)
        self.assertIsNone(result.total_score)
        self.assertEqual(result.teacher_feedback, '')
        self.assertTrue(result.is_pending_review)

    def test_essay_quiz_stores_separate_answer_per_question(self):
        from portals.utils.quiz_submit import build_essay_question_responses, submit_manual_quiz_attempt

        self.ielts_quiz.is_essay = True
        self.ielts_quiz.save(update_fields=['is_essay'])
        question_one = QuizQuestion.objects.create(
            quiz=self.ielts_quiz,
            order=1,
            question='Task one',
        )
        question_two = QuizQuestion.objects.create(
            quiz=self.ielts_quiz,
            order=2,
            question='Task two',
        )
        outcome = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.ielts_quiz.pk,
            given_answers={
                str(question_one.pk): 'Answer for task one.',
                str(question_two.pk): 'Answer for task two.',
            },
        )
        self.assertTrue(outcome['success'])
        result = QuizResult.objects.get(student=self.student, quiz=self.ielts_quiz)
        self.assertEqual(result.given_answers[str(question_one.pk)], 'Answer for task one.')
        self.assertEqual(result.given_answers[str(question_two.pk)], 'Answer for task two.')
        self.assertEqual(result.student_submission, '')

        responses = build_essay_question_responses(result)
        self.assertEqual(len(responses), 2)
        self.assertEqual(responses[0]['student_answer'], 'Answer for task one.')
        self.assertEqual(responses[1]['student_answer'], 'Answer for task two.')

    def test_essay_quiz_accepts_ordered_answers_without_question_ids(self):
        from portals.utils.quiz_submit import submit_manual_quiz_attempt

        self.ielts_quiz.is_essay = True
        self.ielts_quiz.save(update_fields=['is_essay'])
        QuizQuestion.objects.create(
            quiz=self.ielts_quiz,
            order=1,
            question='Task one',
        )
        QuizQuestion.objects.create(
            quiz=self.ielts_quiz,
            order=2,
            question='Task two',
        )
        outcome = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.ielts_quiz.pk,
            ordered_answers=['Answer for task one.', 'Answer for task two.'],
        )
        self.assertTrue(outcome['success'])
        result = QuizResult.objects.get(student=self.student, quiz=self.ielts_quiz)
        self.assertEqual(len(result.given_answers), 2)

    def test_listening_quiz_audio_and_text_questions(self):
        from portals.models import ListeningAudio, ListeningQuestion
        from portals.utils.queries import get_student_manual_quiz_take_data
        from portals.utils.quiz_submit import build_essay_question_responses, submit_manual_quiz_attempt

        self.ielts_quiz.is_listening = True
        self.ielts_quiz.save(update_fields=['is_listening'])
        audio = ListeningAudio.objects.create(
            quiz=self.ielts_quiz,
            order=1,
            title='Section 1 — conversation',
            audio_url='https://example.com/audio.mp3',
        )
        q1 = ListeningQuestion.objects.create(
            audio=audio, order=1, question='What is the customer name?',
        )
        q2 = ListeningQuestion.objects.create(
            audio=audio, order=2, question='What time is the appointment?',
        )
        children = [q1, q2]

        data = get_student_manual_quiz_take_data(self.student.pk, self.ielts_quiz.pk)
        self.assertIsNotNone(data)
        self.assertEqual(len(data['listening_sections']), 1)
        self.assertEqual(len(data['listening_sections'][0]['questions']), 2)
        self.assertEqual(data['response_question_count'], 2)

        given_answers = {
            str(children[0].pk): 'Anna',
            str(children[1].pk): '3:30 pm',
        }

        outcome = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.ielts_quiz.pk,
            given_answers=given_answers,
        )
        self.assertTrue(outcome['success'])
        result = QuizResult.objects.get(student=self.student, quiz=self.ielts_quiz)
        self.assertEqual(result.given_answers[str(children[0].pk)], 'Anna')
        self.assertEqual(result.given_answers[str(children[1].pk)], '3:30 pm')

        responses = build_essay_question_responses(result)
        self.assertEqual(len(responses), 2)
        self.assertEqual(responses[0]['student_answer'], 'Anna')

    def test_listening_quiz_multiple_audio_sections(self):
        from portals.models import ListeningAudio, ListeningQuestion
        from portals.utils.queries import get_student_manual_quiz_take_data

        self.ielts_quiz.is_listening = True
        self.ielts_quiz.save(update_fields=['is_listening'])
        audio_one = ListeningAudio.objects.create(
            quiz=self.ielts_quiz,
            order=1,
            title='Section 1',
            audio_url='https://example.com/audio1.mp3',
        )
        audio_two = ListeningAudio.objects.create(
            quiz=self.ielts_quiz,
            order=2,
            title='Section 2',
            audio_url='https://example.com/audio2.mp3',
        )
        ListeningQuestion.objects.create(
            audio=audio_one, order=1, question='Section 1 question',
        )
        ListeningQuestion.objects.create(
            audio=audio_two, order=1, question='Section 2 question',
        )

        data = get_student_manual_quiz_take_data(self.student.pk, self.ielts_quiz.pk)
        self.assertIsNotNone(data)
        self.assertEqual(len(data['listening_sections']), 2)
        self.assertEqual(data['listening_sections'][0]['audio']['id'], audio_one.pk)
        self.assertEqual(data['listening_sections'][1]['audio']['id'], audio_two.pk)
        self.assertEqual(len(data['listening_sections'][0]['questions']), 1)
        self.assertEqual(len(data['listening_sections'][1]['questions']), 1)
        self.assertEqual(data['response_question_count'], 2)

    def test_listening_quiz_variant_answer_index_zero(self):
        from portals.models import ListeningAudio, ListeningQuestion
        from portals.utils.quiz_submit import submit_manual_quiz_attempt

        self.ielts_quiz.is_listening = True
        self.ielts_quiz.save(update_fields=['is_listening'])
        audio = ListeningAudio.objects.create(
            quiz=self.ielts_quiz,
            order=1,
            title='Section 1',
            audio_url='https://example.com/audio.mp3',
        )
        question = ListeningQuestion.objects.create(
            audio=audio,
            order=1,
            question='Choose the correct option.',
            answer_options=['First option', 'Second option'],
            correct_answer='First option',
        )

        outcome = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.ielts_quiz.pk,
            given_answers={str(question.pk): '0'},
        )
        self.assertTrue(outcome['success'])
        result = QuizResult.objects.get(student=self.student, quiz=self.ielts_quiz)
        self.assertEqual(result.given_answers[str(question.pk)], '0')

    def test_listening_pending_submission_is_view_only(self):
        from portals.models import ListeningAudio, ListeningQuestion
        from portals.utils.queries import get_student_manual_quiz_take_data
        from portals.utils.quiz_submit import submit_manual_quiz_attempt

        self.ielts_quiz.is_listening = True
        self.ielts_quiz.save(update_fields=['is_listening'])
        audio = ListeningAudio.objects.create(
            quiz=self.ielts_quiz,
            order=1,
            title='Section 1',
            audio_url='https://example.com/audio.mp3',
        )
        question = ListeningQuestion.objects.create(
            audio=audio,
            order=1,
            question='What is the answer?',
        )

        submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.ielts_quiz.pk,
            given_answers={str(question.pk): 'My answer'},
        )

        data = get_student_manual_quiz_take_data(self.student.pk, self.ielts_quiz.pk)
        self.assertIsNotNone(data)
        self.assertTrue(data['view_only'])
        self.assertTrue(data['is_pending_review'])
        self.assertEqual(len(data['listening_sections']), 1)
        self.assertEqual(data['listening_sections'][0]['questions'][0]['student_answer'], 'My answer')

    def test_writing_category_manual_quiz_uses_text_responses(self):
        from portals.utils.quiz_submit import submit_manual_quiz_attempt

        writing_category = QuizCategory.objects.create(service='ielts', name='Writing')
        quiz = Quiz.objects.create(
            category=writing_category,
            topic='Writing tasks',
            is_essay=True,
        )
        QuizQuestion.objects.create(quiz=quiz, order=1, question='Task one')
        QuizQuestion.objects.create(quiz=quiz, order=2, question='Task two')
        self.assertTrue(quiz.uses_per_question_text_responses)

        outcome = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=quiz.pk,
            ordered_answers=['Answer for task one.', 'Answer for task two.'],
        )
        self.assertTrue(outcome['success'])
        result = QuizResult.objects.get(student=self.student, quiz=quiz)
        self.assertEqual(len(result.given_answers), 2)
        self.assertEqual(result.student_submission, '')
