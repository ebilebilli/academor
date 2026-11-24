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

    def test_result_lists_each_answer_with_the_right_one(self):
        q2 = Question.objects.create(test=self.test, text='They ___ happy.', order=2)
        Option.objects.create(question=q2, text='is', is_correct=False)
        Option.objects.create(question=q2, text='are', is_correct=True)
        q3 = Question.objects.create(test=self.test, text='I ___ tea.', order=3)
        Option.objects.create(question=q3, text='like', is_correct=True)

        response = self.client.post(self.url, {
            'first_name': 'Aysel',
            'last_name': 'Məmmədova',
            'number': '+994501234567',
            f'q_{self.question.id}': str(self.option_a.id),
            f'q_{q2.id}': str(q2.options.get(is_correct=True).id),
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'level-test-result.html')
        result = UserResult.objects.get()
        self.assertEqual(result.score, 1)
        self.assertEqual(
            [row['status'] for row in response.context['review']],
            ['wrong', 'correct', 'blank'],
        )
        first = response.context['review'][0]
        self.assertEqual((first['chosen'], first['right']), ('go', 'goes'))
        self.assertContains(response, 'class="lxa-item is-wrong"')
        self.assertContains(response, 'id="lxa-mistakes"')
