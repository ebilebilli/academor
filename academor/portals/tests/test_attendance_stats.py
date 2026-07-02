from django.test import SimpleTestCase

from portals.utils.attendance_stats import attendance_rate_tier, compute_attendance_stats


class AttendanceStatsTests(SimpleTestCase):
    def test_compute_from_detail(self):
        detail = {
            'summary': {'present': 8, 'absent': 1, 'late': 1, 'total': 10},
            'attendance_rate': 80.0,
        }
        stats = compute_attendance_stats(detail)
        self.assertEqual(stats['present'], 8)
        self.assertEqual(stats['attendance_rate'], 80.0)
        self.assertEqual(stats['tier'], 'good')

    def test_empty_detail(self):
        stats = compute_attendance_stats(None)
        self.assertEqual(stats['total'], 0)
        self.assertIsNone(stats['attendance_rate'])
        self.assertEqual(stats['tier'], 'empty')

    def test_rate_tiers(self):
        self.assertEqual(attendance_rate_tier(95), 'excellent')
        self.assertEqual(attendance_rate_tier(80), 'good')
        self.assertEqual(attendance_rate_tier(60), 'fair')
        self.assertEqual(attendance_rate_tier(40), 'low')
        self.assertEqual(attendance_rate_tier(None), 'empty')
