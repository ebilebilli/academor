from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase, TestCase

from portals.admin.admin_v1 import QuizQuestionInline
from portals.admin.quiz_option_debug import collect_field_snapshot, log_quiz_options_post
from portals.admin.widgets import AnswerOptionsFormField, AnswerOptionsWidget, option_has_text
from portals.models import Quiz, QuizCategory
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
