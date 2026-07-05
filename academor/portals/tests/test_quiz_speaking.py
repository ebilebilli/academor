from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from portals.models import (
    Quiz,
    QuizCategory,
    QuizResult,
    SpeakingPart,
    SpeakingPartType,
    SpeakingQuestion,
    SpeakingRecording,
)
from portals.tests.test_quiz_visibility import QuizVisibilityTests
from portals.utils.queries import get_student_speaking_quiz_take_data, serialize_quiz
from portals.utils.quiz_submit import submit_speaking_quiz_attempt, submit_teacher_quiz_review


class QuizSpeakingTests(QuizVisibilityTests):
    def _create_speaking_quiz(self, *, topic='IELTS Speaking Test'):
        quiz = Quiz.objects.create(
            category=self.ielts_category,
            topic=topic,
            is_speaking=True,
            is_time_limited=True,
            time_limit_minutes=14,
        )
        part1 = SpeakingPart.objects.create(
            quiz=quiz,
            part_type=SpeakingPartType.PART_1,
            order=1,
            title='Part 1',
            instructions='<p>Answer the questions about yourself.</p>',
        )
        SpeakingQuestion.objects.create(
            part=part1,
            order=1,
            question='<p>Do you work or are you a student?</p>',
        )
        SpeakingQuestion.objects.create(
            part=part1,
            order=2,
            question='<p>What do you like about your hometown?</p>',
        )
        part2 = SpeakingPart.objects.create(
            quiz=quiz,
            part_type=SpeakingPartType.PART_2,
            order=2,
            title='Part 2',
            cue_card_topic='<p>Describe a place you like to visit.</p>',
            cue_card_bullets=['where it is', 'how often you go there', 'why you like it'],
        )
        SpeakingQuestion.objects.create(part=part2, order=1, question='')
        part3 = SpeakingPart.objects.create(
            quiz=quiz,
            part_type=SpeakingPartType.PART_3,
            order=3,
            title='Part 3',
            instructions='<p>Discuss the topic in more detail.</p>',
        )
        SpeakingQuestion.objects.create(
            part=part3,
            order=1,
            question='<p>Why do people like travelling to new places?</p>',
        )
        return quiz

    def _audio_file(self, name='answer.webm'):
        return SimpleUploadedFile(name, b'fake-audio-bytes', content_type='audio/webm')

    def test_serialize_quiz_counts_speaking_questions(self):
        quiz = self._create_speaking_quiz()
        data = serialize_quiz(quiz)
        self.assertTrue(data['is_speaking'])
        self.assertEqual(data['question_count'], 4)

    def test_get_student_speaking_quiz_take_data(self):
        quiz = self._create_speaking_quiz()
        data = get_student_speaking_quiz_take_data(self.student.pk, quiz.pk)
        self.assertIsNotNone(data)
        self.assertEqual(len(data['speaking_sections']), 3)
        self.assertEqual(data['response_question_count'], 4)
        self.assertEqual(data['speaking_sections'][1]['part']['part_type'], SpeakingPartType.PART_2)
        self.assertFalse(data['view_only'])

    def test_submit_speaking_quiz_attempt(self):
        quiz = self._create_speaking_quiz()
        take_data = get_student_speaking_quiz_take_data(self.student.pk, quiz.pk)
        question_ids = take_data['response_question_ids']
        files = {str(qid): self._audio_file(f'answer-{qid}.webm') for qid in question_ids}

        outcome = submit_speaking_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=quiz.pk,
            recording_files=files,
            recording_durations={str(qid): 25 for qid in question_ids},
            duration_sec=600,
        )
        self.assertTrue(outcome['success'])
        result = QuizResult.objects.get(pk=outcome['result_id'])
        self.assertEqual(SpeakingRecording.objects.filter(result=result).count(), 4)
        self.assertEqual(len(result.given_answers), 4)

    def test_speaking_quiz_pending_review_blocks_retake(self):
        quiz = self._create_speaking_quiz()
        take_data = get_student_speaking_quiz_take_data(self.student.pk, quiz.pk)
        question_ids = take_data['response_question_ids']
        submit_speaking_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=quiz.pk,
            recording_files={str(qid): self._audio_file() for qid in question_ids},
        )
        pending = get_student_speaking_quiz_take_data(self.student.pk, quiz.pk)
        self.assertTrue(pending['view_only'])
        self.assertTrue(pending['is_pending_review'])

    def test_teacher_review_speaking_score(self):
        quiz = self._create_speaking_quiz()
        take_data = get_student_speaking_quiz_take_data(self.student.pk, quiz.pk)
        question_ids = take_data['response_question_ids']
        outcome = submit_speaking_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=quiz.pk,
            recording_files={str(qid): self._audio_file() for qid in question_ids},
        )
        review = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=outcome['result_id'],
            total_score=7.5,
            teacher_feedback='Good fluency and pronunciation.',
        )
        self.assertTrue(review['success'])
        result = QuizResult.objects.get(pk=outcome['result_id'])
        self.assertEqual(result.total_score, 7.5)
        self.assertIsNotNone(result.reviewed_at)

    def test_teacher_review_speaking_page_renders(self):
        quiz = self._create_speaking_quiz()
        take_data = get_student_speaking_quiz_take_data(self.student.pk, quiz.pk)
        question_ids = take_data['response_question_ids']
        outcome = submit_speaking_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=quiz.pk,
            recording_files={str(qid): self._audio_file() for qid in question_ids},
        )
        self.client.force_login(self.teacher_user)
        url = reverse(
            'portals:teacher-quiz-result-review',
            kwargs={'result_pk': outcome['result_id']},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IELTS Speaking Test')
        self.assertContains(response, 'Speaking tasks')

    def test_speaking_take_view_renders(self):
        quiz = self._create_speaking_quiz()
        self.client.force_login(self.student_user)
        url = reverse('portals:student-speaking-quiz-take', kwargs={'pk': quiz.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IELTS Speaking Test')
        self.assertContains(response, 'data-quiz-speaking-take')

    def test_manual_take_data_excludes_speaking_quiz(self):
        from portals.utils.queries import get_student_manual_quiz_take_data

        quiz = self._create_speaking_quiz()
        self.assertIsNone(get_student_manual_quiz_take_data(self.student.pk, quiz.pk))

    def test_part_two_requires_cue_card(self):
        quiz = Quiz.objects.create(
            category=self.ielts_category,
            topic='Invalid speaking',
            is_speaking=True,
        )
        part = SpeakingPart(
            quiz=quiz,
            part_type=SpeakingPartType.PART_2,
            order=1,
        )
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            part.full_clean()


class QuizSpeakingResourceLoaderTests(QuizVisibilityTests):
    def test_parse_speaking_resource_file(self):
        from pathlib import Path

        from portals.utils.quiz_speaking_resource_loader import (
            RESOURCES_DIR,
            parse_speaking_resource_file,
        )

        path = RESOURCES_DIR / 'ielts_speaking_test_1.json'
        parsed = parse_speaking_resource_file(path)
        self.assertEqual(parsed['resource_slug'], 'ielts_speaking_test_1')
        self.assertEqual(parsed['category_name'], 'Speaking')
        self.assertEqual(len(parsed['parts']), 3)
        self.assertEqual(parsed['parts'][1]['part_type'], SpeakingPartType.PART_2)
        self.assertEqual(len(parsed['parts'][1]['cue_card_bullets']), 4)

    def test_load_speaking_resource_file(self):
        from pathlib import Path

        from portals.utils.quiz_speaking_resource_loader import (
            RESOURCES_DIR,
            load_speaking_resource_file,
        )

        path = RESOURCES_DIR / 'ielts_speaking_test_1.json'
        result = load_speaking_resource_file(path)
        self.assertTrue(result['quiz_id'])
        self.assertEqual(result['parts'], 3)
        self.assertEqual(result['questions'], 11)
        quiz = Quiz.objects.get(pk=result['quiz_id'])
        self.assertTrue(quiz.is_speaking)
        self.assertFalse(quiz.is_time_limited)

    def test_speaking_part_admin_form_creates_quiz(self):
        from portals.admin.quiz_forms import SpeakingPartAdminForm

        form = SpeakingPartAdminForm(
            data={
                'quiz': '',
                'new_quiz_topic': 'IELTS Speaking — Auto Quiz',
                'new_quiz_category': self.ielts_category.pk,
                'order': 1,
                'part_type': SpeakingPartType.PART_1,
                'title': 'Part 1',
                'instructions': '',
                'cue_card_topic': '',
                'cue_card_bullets': '[]',
                'preparation_seconds': '',
                'default_answer_seconds': '',
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        part = form.save()
        self.assertTrue(part.quiz.is_speaking)
        self.assertEqual(part.quiz.topic, 'IELTS Speaking — Auto Quiz')
