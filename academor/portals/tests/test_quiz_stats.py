from django.test import SimpleTestCase

from portals.utils.quiz_stats import (
    build_mock_stats_list,
    compute_mock_average_stats,
    compute_quiz_average_stats,
    compute_weekly_average_stats,
    quiz_average_score_tier,
    quiz_score_percent,
)


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

    def test_quiz_average_score_tier_bands(self):
        self.assertEqual(quiz_average_score_tier(None), 'empty')
        self.assertEqual(quiz_average_score_tier(95), 'excellent')
        self.assertEqual(quiz_average_score_tier(85), 'excellent')
        self.assertEqual(quiz_average_score_tier(70), 'good')
        self.assertEqual(quiz_average_score_tier(50), 'fair')
        self.assertEqual(quiz_average_score_tier(49.9), 'low')

    def test_weekly_average_stats(self):
        rows = [
            {'score': 8, 'max_score': 10},
            {'score': 7, 'max_score': 10},
        ]
        stats = compute_weekly_average_stats(rows)
        self.assertEqual(stats['avg_score_pct'], 75.0)
        self.assertEqual(stats['avg_score_ten'], 7.5)
        self.assertEqual(stats['graded_count'], 2)

    def test_mock_average_stats(self):
        attempts = [
            {'overall_band': 7.0, 'is_fully_graded': True},
            {'overall_band': 8.0, 'is_fully_graded': True},
            {'overall_band': None, 'is_fully_graded': False},
        ]
        stats = compute_mock_average_stats(attempts)
        self.assertEqual(stats['avg_band'], 7.5)
        self.assertEqual(stats['avg_score_pct'], 83.3)
        self.assertEqual(stats['graded_count'], 2)
        self.assertEqual(stats['pending_count'], 1)
        self.assertEqual(stats['tier'], 'good')

    def test_mock_average_stats_sat_scaled(self):
        attempts = [
            {
                'scoring_mode': 'sat_scaled',
                'overall_score': 1200,
                'is_fully_graded': True,
            },
            {
                'scoring_mode': 'sat_scaled',
                'overall_score': 1400,
                'is_fully_graded': True,
            },
        ]
        stats = compute_mock_average_stats(attempts)
        self.assertIsNone(stats['avg_band'])
        self.assertEqual(stats['avg_total_score'], 1300)
        self.assertEqual(stats['avg_score_pct'], 81.2)
        self.assertEqual(stats['graded_count'], 2)

    def test_build_mock_stats_list_splits_by_exam_program(self):
        attempts = [
            {
                'exam_program': 'ielts',
                'scoring_mode': 'ielts_band',
                'overall_band': 7.0,
                'is_fully_graded': True,
            },
            {
                'exam_program': 'ielts',
                'scoring_mode': 'ielts_band',
                'overall_band': 8.0,
                'is_fully_graded': True,
            },
            {
                'exam_program': 'sat',
                'scoring_mode': 'sat_scaled',
                'overall_score': 1200,
                'is_fully_graded': True,
            },
            {
                'exam_program': 'sat',
                'scoring_mode': 'sat_scaled',
                'overall_score': 1400,
                'is_fully_graded': True,
            },
        ]
        cards = build_mock_stats_list(attempts)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]['exam_program'], 'ielts')
        self.assertEqual(cards[0]['avg_band'], 7.5)
        self.assertEqual(cards[1]['exam_program'], 'sat')
        self.assertEqual(cards[1]['avg_total_score'], 1300)
