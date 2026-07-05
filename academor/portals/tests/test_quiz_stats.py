from django.test import SimpleTestCase

from portals.utils.quiz_stats import compute_quiz_average_stats, compute_weekly_average_stats, quiz_score_percent


class QuizAverageStatsTests(SimpleTestCase):
    def test_normalizes_mixed_scales(self):
        rows = [
            {'total_score': 8, 'max_value': 10, 'is_pending_review': False},
            {'total_score': 70, 'max_value': 100, 'is_pending_review': False},
        ]
        stats = compute_quiz_average_stats(rows)
        self.assertEqual(stats['avg_score_pct'], 75.0)
        self.assertEqual(stats['graded_count'], 2)

    def test_excludes_pending_review(self):
        rows = [
            {'total_score': 10, 'max_value': 10, 'is_pending_review': False},
            {'total_score': None, 'max_value': 10, 'is_pending_review': True},
        ]
        stats = compute_quiz_average_stats(rows)
        self.assertEqual(stats['avg_score_pct'], 100.0)
        self.assertEqual(stats['pending_count'], 1)
        self.assertEqual(stats['graded_count'], 1)

    def test_quiz_score_percent_clamps(self):
        self.assertEqual(quiz_score_percent(11, 10), 100.0)
        self.assertEqual(quiz_score_percent(-1, 10), 0.0)

    def test_weekly_average_stats(self):
        rows = [
            {'score': 8, 'max_score': 10},
            {'score': 7, 'max_score': 10},
        ]
        stats = compute_weekly_average_stats(rows)
        self.assertEqual(stats['avg_score_pct'], 75.0)
        self.assertEqual(stats['graded_count'], 2)
