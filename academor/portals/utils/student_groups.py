"""Student study-group context for multi-group portal filtering."""

from urllib.parse import urlencode

from portals.models import StudyGroup
from portals.utils.group_services import study_group_portal_codes


def get_student_study_groups(student_id):
    if not student_id:
        return []
    return list(
        StudyGroup.objects.filter(students__pk=student_id, is_active=True)
        .order_by('name')
        .values('id', 'name')
    )


def build_student_group_maps(student_id):
    """Return (groups, by_teacher_id, by_service_code) for a student."""
    groups = list(
        StudyGroup.objects.filter(students__pk=student_id, is_active=True)
        .prefetch_related('courses')
        .order_by('name')
    )
    by_teacher = {}
    by_service = {}
    serialized = []
    for group in groups:
        serialized.append({'id': group.pk, 'name': group.name})
        by_teacher.setdefault(group.teacher_id, []).append(group.pk)
        for code in study_group_portal_codes(group):
            by_service.setdefault(code, []).append(group.pk)
    return serialized, by_teacher, by_service


def resolve_student_group(request, groups):
    """Selected group id when the student belongs to multiple groups."""
    if not groups or len(groups) <= 1:
        return None
    raw = (request.GET.get('group') or '').strip()
    valid = {str(group['id']) for group in groups}
    if raw and raw in valid:
        return int(raw)
    return groups[0]['id']


def build_portal_query(*, student_id=None, group_id=None, extra=None):
    params = {}
    if student_id is not None:
        params['student'] = student_id
    if group_id is not None:
        params['group'] = group_id
    if extra:
        params.update(extra)
    if not params:
        return ''
    return '?' + urlencode(params)


def enrich_score_group_counts(score_groups, items, *, group_id_key='group_id', replace=False):
    """Add per-group item counts. By default accumulates across multiple calls."""
    if not score_groups:
        return score_groups
    counts = {}
    for item in items or []:
        group_id = item.get(group_id_key)
        if group_id:
            counts[group_id] = counts.get(group_id, 0) + 1
    for group in score_groups:
        base = 0 if replace else group.get('total_count', 0) or 0
        group['total_count'] = base + counts.get(group['id'], 0)
    return score_groups


def student_group_context(request, student_id):
    groups = get_student_study_groups(student_id)
    active_group_id = resolve_student_group(request, groups)
    score_groups = []
    if len(groups) > 1:
        score_groups = [
            {
                'id': group['id'],
                'name': group['name'],
                'total_count': 0,
            }
            for group in groups
        ]
    week_prefix_parts = []
    if active_group_id:
        week_prefix_parts.append(f'group={active_group_id}')
    week_nav_prefix = '&'.join(week_prefix_parts)
    if week_nav_prefix:
        week_nav_prefix += '&'
    return {
        'student_groups': groups,
        'score_groups': score_groups,
        'active_score_group': str(active_group_id) if active_group_id else None,
        'group_query': build_portal_query(group_id=active_group_id),
        'week_nav_prefix': week_nav_prefix,
    }


def merge_parent_group_context(child_ctx, student_id, request):
    """Attach group tabs/query params to parent child context."""
    group_ctx = student_group_context(request, student_id)
    student_query = build_portal_query(
        student_id=student_id if len(child_ctx.get('children', [])) > 1 else None,
        group_id=group_ctx.get('active_score_group'),
    )
    week_prefix_parts = []
    if student_id and len(child_ctx.get('children', [])) > 1:
        week_prefix_parts.append(f'student={student_id}')
    if group_ctx.get('active_score_group'):
        week_prefix_parts.append(f'group={group_ctx["active_score_group"]}')
    child_ctx.update(group_ctx)
    child_ctx['student_query'] = student_query
    child_ctx['week_nav_prefix'] = '&'.join(week_prefix_parts)
    if child_ctx['week_nav_prefix']:
        child_ctx['week_nav_prefix'] += '&'
    return child_ctx
