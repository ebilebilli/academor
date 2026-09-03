from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase, TestCase

from portals.admin.admin_v1 import QuizQuestionInline
from portals.admin.quiz_forms import QuizQuestionAdminForm
from portals.admin.quiz_option_debug import collect_field_snapshot, log_quiz_options_post
from portals.admin.widgets import AnswerOptionsFormField, AnswerOptionsWidget, option_has_text
from portals.models import Quiz, QuizCategory, QuizQuestion
from portals.tests.portal_helpers import ensure_active_portal_services

User = get_user_model()


class AnswerOptionsWidgetTests(SimpleTestCase):
    def test_reads_item_textareas_when_hidden_json_is_empty(self):
        widget = AnswerOptionsWidget()
        value = widget.value_from_datadict(
            {
                'answer_options': '[]',
                'answer_options_item_0': '<p>Choice A</p>',
                'answer_options_item_1': '<p>Choice B</p>',
                'answer_options_item_2': '<p>Choice C</p>',
                'answer_options_item_3': '<p>Choice D</p>',
            },
            {},
            'answer_options',
        )
        self.assertEqual(value[0], '<p>Choice A</p>')
        self.assertEqual(len(value), 4)

    def test_reads_inline_prefixed_item_textareas(self):
        widget = AnswerOptionsWidget()
        value = widget.value_from_datadict(
            {
                'questions-0-answer_options': '[]',
                'questions-0-answer_options_item_0': '<p>A</p>',
                'questions-0-answer_options_item_1': '<p>B</p>',
            },
            {},
            'questions-0-answer_options',
        )
        self.assertEqual(value, ['<p>A</p>', '<p>B</p>'])

    def test_empty_ckeditor_html_does_not_count_as_text(self):
        self.assertFalse(option_has_text('<p></p>'))
        self.assertFalse(option_has_text('<p>&nbsp;</p>'))
        self.assertTrue(option_has_text('<p>However</p>'))

    def test_empty_payload_is_not_a_change(self):
        field = AnswerOptionsFormField()
        self.assertFalse(field.has_changed(None, []))
        self.assertFalse(field.has_changed([], ['<p></p>', '<p>&nbsp;</p>']))
        self.assertTrue(field.has_changed([], ['<p>A</p>', '<p>B</p>']))


class QuizOptionDebugTests(SimpleTestCase):
    def test_snapshot_counts_item_textareas_when_hidden_json_empty(self):
        snap = collect_field_snapshot(
            {
                'answer_options': '[]',
                'answer_options_item_0': '<p>A</p>',
                'answer_options_item_1': '<p>B</p>',
            },
            'answer_options',
        )
        self.assertEqual(snap['hidden_filled'], 0)
        self.assertEqual(snap['item_filled'], 2)
        self.assertEqual(snap['item_count'], 2)

    def test_save_post_writes_warning_log(self):
        request = RequestFactory().post('/admin/portals/quizquestion/1/change/', {
            'answer_options': '[]',
            'answer_options_item_0': '<p>A</p>',
            'quiz_options_client_debug': '[{"field":"answer_options","hiddenLen":2}]',
        })
        request.user = 'admin'
        with self.assertLogs('portals.admin.quiz_options', level='WARNING') as captured:
            log_quiz_options_post(request, source='QuizQuestionAdmin', object_id='1')
        self.assertTrue(any('QUIZ_OPTIONS_SAVE_POST' in line for line in captured.output))
        self.assertTrue(any('answer_options_item_0' in line for line in captured.output))


class QuizQuestionInlineAdminTests(TestCase):
    def setUp(self):
        ensure_active_portal_services('ielts')
        self.factory = RequestFactory()
        self.inline = QuizQuestionInline(Quiz, admin_site=None)
        self.category = QuizCategory.objects.create(name='Grammar')
        self.quiz = Quiz.objects.create(category=self.category, topic='Variant quiz')

    def test_inline_always_includes_spr_answer_fields(self):
        request = self.factory.get('/')
        fields = self.inline.get_fields(request, obj=self.quiz)

        self.assertIn('question_type', fields)
        self.assertIn('spr_correct_answers', fields)
        self.assertIn('spr_max_length', fields)


class QuizQuestionAdminFormSatReadingTests(TestCase):
    def setUp(self):
        ensure_active_portal_services('sat')
        self.category = QuizCategory.objects.create(name='SAT')
        self.quiz = Quiz.objects.create(
            category=self.category,
            topic='SAT Practice Test 4 Reading and Writing',
            is_sat=True,
            sat_section=Quiz.SatSection.READING,
            is_reading=False,
        )
        self.question = QuizQuestion.objects.create(
            quiz=self.quiz,
            order=1,
            question='<p>Which choice completes the text?</p>',
            question_type=QuizQuestion.QuestionType.MCQ,
            answer_options=['<p>A</p>', '<p>B</p>', '<p>C</p>', '<p>D</p>'],
            correct_answer='<p>A</p>',
            correct_option_index=0,
        )

    def test_parent_is_reading_flag_does_not_clear_mcq_options(self):
        prefix = 'questions-40'
        options = [
            '<p>On average, participants perceived commentators as more knowledgeable</p>',
            '<p>On average, participants perceived commentators as less biased</p>',
            '<p>On average, participants who watched the panel discussion</p>',
            '<p>On average, participants who watched the single commentator</p>',
        ]
        data = {
            'is_sat': 'on',
            'sat_section': Quiz.SatSection.READING,
            'is_reading': 'on',
            f'{prefix}-id': str(self.question.pk),
            f'{prefix}-quiz': str(self.quiz.pk),
            f'{prefix}-order': '1',
            f'{prefix}-prompt_type': QuizQuestion.PromptType.TEXT,
            f'{prefix}-question_type': QuizQuestion.QuestionType.MCQ,
            f'{prefix}-question': self.question.question,
            f'{prefix}-answer_options': '[]',
            f'{prefix}-answer_options_item_0': options[0],
            f'{prefix}-answer_options_item_1': options[1],
            f'{prefix}-answer_options_item_2': options[2],
            f'{prefix}-answer_options_item_3': options[3],
            f'{prefix}-correct_option_number': '1',
            f'{prefix}-correct_option_index': '0',
            f'{prefix}-correct_answer': options[0],
            f'{prefix}-spr_correct_answers': '[]',
        }
        form = QuizQuestionAdminForm(data, prefix=prefix, instance=self.question)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        self.assertEqual(len(form.cleaned_data['answer_options']), 4)
        self.assertNotIn('answer_options', form.errors)

    def test_sat_reading_quiz_with_mcq_rows_stays_variant(self):
        self.quiz.is_sat = True
        self.quiz.sat_section = Quiz.SatSection.READING
        self.quiz.apply_sat_section_format()
        self.assertFalse(self.quiz.is_reading)
