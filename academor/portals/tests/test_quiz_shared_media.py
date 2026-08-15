from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.test import TestCase

from portals.models import Quiz, QuizCategory
from portals.utils.queries import serialize_quiz


class QuizSharedMediaTests(TestCase):
    def setUp(self):
        self.category = QuizCategory.objects.create(name='Shared media')

    def _quiz(self, **overrides):
        values = {
            'category': self.category,
            'topic': 'Media quiz',
            'has_shared_passage': True,
            'shared_passage': '<p>Read or listen before answering.</p>',
        }
        values.update(overrides)
        return Quiz(**values)

    def test_shared_passage_accepts_audio_and_serializes_its_url(self):
        quiz = self._quiz(shared_audio_file='passage.mp3')
        quiz.full_clean()
        quiz.save()

        data = serialize_quiz(quiz)

        self.assertTrue(data['shared_audio_file_url'].endswith('passage.mp3'))
        self.assertEqual(data['shared_youtube_url'], '')

    def test_shared_passage_rejects_audio_and_youtube_together(self):
        quiz = self._quiz(
            shared_audio_file='passage.mp3',
            shared_youtube_url='https://youtu.be/dQw4w9WgXcQ',
        )

        with self.assertRaises(ValidationError):
            quiz.full_clean()

    def test_shared_passage_rejects_non_youtube_video_url(self):
        quiz = self._quiz(shared_youtube_url='https://example.com/video')

        with self.assertRaises(ValidationError) as context:
            quiz.full_clean()

        self.assertIn('shared_youtube_url', context.exception.message_dict)

    def test_youtube_media_renders_as_embed(self):
        html = render_to_string(
            'portals/includes/quiz_shared_passage_media.html',
            {
                'source': {
                    'shared_audio_file_url': '',
                    'shared_youtube_url': 'https://youtu.be/dQw4w9WgXcQ',
                },
            },
        )

        self.assertIn('https://www.youtube.com/embed/dQw4w9WgXcQ', html)
        self.assertIn('<iframe', html)
