"""Attendance aggregates for profile and dashboard views."""


def attendance_rate_tier(attendance_rate):
    if attendance_rate is None:
        return 'empty'
    if attendance_rate >= 90:
        return 'excellent'
    if attendance_rate >= 75:
        return 'good'
    if attendance_rate >= 50:
        return 'fair'
    return 'low'


def compute_attendance_stats(attendance_detail):
    """Summarize attendance records for profile showcase."""
    if not attendance_detail:
        return {
            'present': 0,
            'absent': 0,
            'late': 0,
            'total': 0,
            'attendance_rate': None,
            'tier': 'empty',
        }

    summary = attendance_detail.get('summary') or {}
    present = int(summary.get('present') or 0)
    absent = int(summary.get('absent') or 0)
    late = int(summary.get('late') or 0)
    total = int(summary.get('total') or 0)
    attendance_rate = attendance_detail.get('attendance_rate')
    if attendance_rate is None and total:
        attendance_rate = round(100 * present / total, 1)

    return {
        'present': present,
        'absent': absent,
        'late': late,
        'total': total,
        'attendance_rate': attendance_rate,
        'tier': attendance_rate_tier(attendance_rate if total else None),
    }
