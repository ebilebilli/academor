"""Parse and validate teacher portal schedule bulk-create forms."""

from datetime import datetime

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from portals.models import Schedule
from portals.utils.teacher_courses import teacher_groups_queryset

DEFAULT_DURATION_MIN = 90
MIN_DURATION_MIN = 15

TIME_24H_INPUT_ATTRS = {
    'class': 'form-control portal-time-24h',
    'inputmode': 'numeric',
    'pattern': r'([01][0-9]|2[0-3]):[0-5][0-9]',
    'placeholder': '14:30',
    'maxlength': '5',
    'autocomplete': 'off',
}


def _parse_time(raw):
    raw = (raw or '').strip()
    if not raw:
        return None
    for fmt in ('%H:%M', '%H:%M:%S'):
        try:
            return datetime.strptime(raw, fmt).time()
        except ValueError:
            continue
    return None


def _parse_duration(raw):
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    if value < MIN_DURATION_MIN:
        return None
    return value


def schedule_slot_field_names(index):
    prefix = f'slots-{index}'
    return {
        'weekday': f'{prefix}-weekday',
        'start_time': f'{prefix}-start_time',
        'duration_min': f'{prefix}-duration_min',
    }


def schedule_slot_count_from_post(post):
    raw = post.get('slot_count')
    try:
        count = int(raw)
    except (TypeError, ValueError):
        count = 0
    return max(count, 0)


def parse_schedule_slots_from_post(post):
    """Return list of slot dicts from POST (may include empty rows)."""
    slots = []
    for index in range(schedule_slot_count_from_post(post)):
        names = schedule_slot_field_names(index)
        slots.append({
            'index': index,
            'weekday': (post.get(names['weekday']) or '').strip(),
            'start_time': (post.get(names['start_time']) or '').strip(),
            'duration_min': (post.get(names['duration_min']) or '').strip(),
        })
    return slots


def validate_schedule_slots(slots):
    """
    Validate slot rows. Returns (cleaned_rows, errors).
    errors: list of {'index': int, 'message': str}
    """
    cleaned = []
    errors = []
    seen_keys = set()

    for row in slots:
        index = row['index']
        weekday_raw = row['weekday']
        time_raw = row['start_time']
        duration_raw = row['duration_min']

        if not weekday_raw and not time_raw and not duration_raw:
            continue

        if not weekday_raw:
            errors.append({'index': index, 'message': str(_('Select a weekday.'))})
            continue
        try:
            weekday = int(weekday_raw)
        except (TypeError, ValueError):
            errors.append({'index': index, 'message': str(_('Select a weekday.'))})
            continue
        if weekday not in dict(Schedule.Weekday.choices):
            errors.append({'index': index, 'message': str(_('Select a weekday.'))})
            continue

        start_time = _parse_time(time_raw)
        if not start_time:
            errors.append({'index': index, 'message': str(_('Enter a valid time (HH:MM, 24-hour format).'))})
            continue

        duration_min = _parse_duration(duration_raw) if duration_raw else DEFAULT_DURATION_MIN
        if duration_min is None:
            errors.append({
                'index': index,
                'message': str(_('Duration must be at least %(min)s minutes.') % {'min': MIN_DURATION_MIN}),
            })
            continue

        slot_key = (weekday, start_time)
        if slot_key in seen_keys:
            errors.append({
                'index': index,
                'message': str(_('This day and time is duplicated in the form.')),
            })
            continue
        seen_keys.add(slot_key)

        cleaned.append({
            'weekday': weekday,
            'start_time': start_time,
            'duration_min': duration_min,
        })

    if not cleaned and not errors:
        errors.append({'index': 0, 'message': str(_('Add at least one schedule slot.'))})

    return cleaned, errors


def create_schedule_slots(group, slots):
    """Create Schedule rows for a group; returns created instances."""
    effective_from = timezone.localdate()
    created = []
    for slot in slots:
        created.append(
            Schedule.objects.create(
                group=group,
                weekday=slot['weekday'],
                start_time=slot['start_time'],
                duration_min=slot['duration_min'],
                room_or_link='',
                effective_from=effective_from,
            )
        )
    return created


def build_schedule_bulk_form_context(
    *,
    teacher_id,
    group=None,
    post=None,
    slot_errors=None,
    initial_rows=None,
):
    """Template context for bulk schedule create form."""
    weekday_choices = list(Schedule.Weekday.choices)
    if post is not None:
        slot_count = schedule_slot_count_from_post(post)
        rows = parse_schedule_slots_from_post(post)
    elif initial_rows:
        rows = []
        for index, row in enumerate(initial_rows):
            rows.append({
                'index': row.get('index', index),
                'weekday': row.get('weekday', ''),
                'start_time': row.get('start_time', ''),
                'duration_min': row.get('duration_min', str(DEFAULT_DURATION_MIN)),
            })
        slot_count = len(rows)
    else:
        slot_count = 1
        rows = [{'index': 0, 'weekday': '', 'start_time': '', 'duration_min': str(DEFAULT_DURATION_MIN)}]

    error_by_index = {}
    for item in slot_errors or []:
        error_by_index.setdefault(item['index'], []).append(item['message'])

    slot_rows = []
    for row in rows:
        index = row['index']
        slot_rows.append({
            'index': index,
            'fields': schedule_slot_field_names(index),
            'weekday': row.get('weekday', ''),
            'start_time': row.get('start_time', ''),
            'duration_min': row.get('duration_min') or str(DEFAULT_DURATION_MIN),
            'errors': error_by_index.get(index, []),
        })

    groups = teacher_groups_queryset(teacher_id, active_only=True).order_by('name')
    return {
        'weekday_choices': weekday_choices,
        'slot_rows': slot_rows,
        'slot_count': max(slot_count, len(slot_rows), 1),
        'default_duration_min': DEFAULT_DURATION_MIN,
        'group': group,
        'groups': groups,
        'group_fixed': group is not None,
        'selected_group_id': (
            str(group.pk)
            if group
            else (post.get('group') if post is not None else '')
        ),
    }


class TeacherScheduleEditForm(forms.ModelForm):
    """Single-slot edit form for teachers (no room / active-from fields)."""

    start_time = forms.CharField(
        label=_('Time'),
        help_text=_('Enter time in 24-hour HH:MM format (Baku).'),
        widget=forms.TextInput(attrs=TIME_24H_INPUT_ATTRS),
    )

    class Meta:
        model = Schedule
        fields = ('group', 'weekday', 'duration_min')
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control'}),
            'weekday': forms.Select(attrs={'class': 'form-control'}),
            'duration_min': forms.NumberInput(attrs={'class': 'form-control', 'min': MIN_DURATION_MIN, 'step': 5}),
        }

    def __init__(self, teacher_id, *args, group_fixed=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_id = teacher_id
        groups = teacher_groups_queryset(teacher_id, active_only=True).order_by('name')
        if group_fixed:
            self.fields.pop('group', None)
        else:
            self.fields['group'].queryset = groups
            self.fields['group'].label = _('Group')
        self.fields['weekday'].label = _('Weekday')
        self.fields['duration_min'].label = _('Duration (minutes)')
        if self.instance and self.instance.pk and self.instance.start_time and not self.data:
            self.initial['start_time'] = self.instance.start_time.strftime('%H:%M')
        if not self.initial.get('duration_min') and not self.data:
            self.initial.setdefault('duration_min', DEFAULT_DURATION_MIN)

    def clean_start_time(self):
        parsed = _parse_time(self.cleaned_data.get('start_time'))
        if not parsed:
            raise forms.ValidationError(_('Enter a valid time (HH:MM, 24-hour format).'))
        return parsed

    def clean_group(self):
        group = self.cleaned_data.get('group')
        if group and not teacher_groups_queryset(self.teacher_id, active_only=True).filter(pk=group.pk).exists():
            raise forms.ValidationError(_('You can only schedule slots for your own groups.'))
        return group
