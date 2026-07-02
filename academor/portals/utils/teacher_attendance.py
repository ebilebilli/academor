"""Teacher attendance marking helpers."""

from __future__ import annotations

from portals.models import Attendance


def parse_student_ids(raw_value) -> list[int]:
    if not raw_value:
        return []
    if isinstance(raw_value, (list, tuple)):
        parts = []
        for item in raw_value:
            parts.extend(str(item).split(','))
    else:
        parts = str(raw_value).split(',')
    ids = []
    for part in parts:
        part = str(part).strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except (TypeError, ValueError):
            continue
    return ids


def save_session_attendance(schedule, session_date, student_status_map):
    """Bulk create/update attendance for one session. Returns count saved."""
    saved = 0
    for student_id, status in student_status_map.items():
        Attendance.objects.update_or_create(
            schedule=schedule,
            student_id=student_id,
            session_date=session_date,
            defaults={'status': status},
        )
        saved += 1
    return saved


def selected_student_ids_from_post(post_data) -> list[int]:
    return parse_student_ids(post_data.getlist('selected_students'))
