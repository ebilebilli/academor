from datetime import date

from django.test import SimpleTestCase

from portals.utils.attendance_stats import attendance_rate_tier, compute_attendance_stats
from portals.utils.teacher_attendance_register import month_key, parse_register_month, shift_month


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


class RegisterMonthHelperTests(SimpleTestCase):
    def test_parse_register_month_valid(self):
        self.assertEqual(parse_register_month('2026-02', today=date(2026, 10, 5)), (2026, 2))

    def test_parse_register_month_falls_back_to_today(self):
        self.assertEqual(parse_register_month('nope', today=date(2026, 10, 5)), (2026, 10))
        self.assertEqual(parse_register_month(None, today=date(2026, 3, 1)), (2026, 3))

    def test_shift_month_wraps_year(self):
        self.assertEqual(shift_month(2026, 1, -1), (2025, 12))
        self.assertEqual(shift_month(2026, 12, 1), (2027, 1))
        self.assertEqual(month_key(2026, 9), '2026-09')
