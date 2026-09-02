from django.test import TestCase
from django.urls import reverse

from projects.models import Option, Question, Test, UserResult


class TestTakeFormValidationTests(TestCase):
    def setUp(self):
        self.test = Test.objects.create(title_az='Səviyyə testi', is_active=True)
        self.question = Question.objects.create(
            test=self.test,
            text='She ___ to school every day.',
            order=1,
        )
        self.option_a = Option.objects.create(
            question=self.question,
            text='go',
            is_correct=False,
        )
        self.option_b = Option.objects.create(
            question=self.question,
            text='goes',
            is_correct=True,
        )
        self.url = reverse('projects:test-take', kwargs={'test_id': self.test.pk})

    def test_invalid_contact_fields_keep_selected_answers(self):
        response = self.client.post(self.url, {
            'first_name': '',
            'number': '12',
            f'q_{self.question.id}': str(self.option_b.id),
            'test_current_step': '0',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserResult.objects.count(), 0)
        content = response.content.decode()
        self.assertRegex(
            content,
            rf'id="q{self.question.id}o{self.option_b.id}"[^>]*\bchecked\b',
        )
        self.assertNotRegex(
            content,
            rf'id="q{self.question.id}o{self.option_a.id}"[^>]*\bchecked\b',
        )
