import html as html_lib
import json
from html import unescape

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def option_has_text(value):
    """True when an MCQ/SPR option has visible text (empty CKEditor HTML does not count)."""
    if value in (None, ''):
        return False
    text = unescape(strip_tags(str(value))).replace('\xa0', ' ').strip()
    return bool(text)


def nonempty_options(values):
    if not isinstance(values, list):
        return []
    return [item for item in values if option_has_text(item)]


def _coerce_json_list(value, *, empty=None):
    if value in (None, ''):
        return empty if empty is not None else []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value or '[]')
        except json.JSONDecodeError as exc:
            raise ValidationError(_('Enter a valid JSON list.')) from exc
        if not isinstance(parsed, list):
            raise ValidationError(_('Value must be a JSON list.'))
        return parsed
    raise ValidationError(_('Enter a valid JSON list.'))


class AnswerOptionsWidget(forms.Widget):
    """
    Dynamic list of rich-text entries (CKEditor per row).
    Used for MCQ answer options and SPR correct answers.
    """

    template_name = 'portals/admin/widgets/answer_options_widget.html'

    class Media:
        js = ('portals/admin/js/answer-options-widget.js',)
        css = {'all': ('portals/css/answer-options-widget.css',)}

    def __init__(
        self,
        attrs=None,
        *,
        item_label='Option',
        add_button_label='Add option',
        remove_title='Remove option',
    ):
        default_attrs = {'class': 'answer-options-widget'}
        if attrs:
            default_attrs.update(attrs)
        self.item_label = item_label
        self.add_button_label = add_button_label
        self.remove_title = remove_title
        super().__init__(default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if value in (None, ''):
            value = []
        elif isinstance(value, list):
            pass
        elif isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = []
        else:
            value = []

        if not isinstance(value, list):
            value = []

        context = {
            'name': name,
            'options': value,
            'widget': self,
            'attrs': attrs or {},
        }

        return mark_safe(self._render_template(context))

    def _render_template(self, context):
        name = context['name']
        options = context['options']
        item_label = self.item_label
        add_label = self.add_button_label
        remove_title = self.remove_title

        chunks = [
            f'''
        <div class="answer-options-container" data-field-name="{html_lib.escape(name)}"
             data-item-label="{html_lib.escape(item_label)}" data-add-label="{html_lib.escape(add_label)}">
            <div class="answer-options-list">
        '''
        ]

        for i, option in enumerate(options):
            # Textarea content is raw text (not HTML-parsed), but entities are
            # decoded by the browser — escape so "</textarea>" cannot break markup.
            option_html = html_lib.escape(str(option or ''), quote=False)
            chunks.append(f'''
                <div class="answer-option-item" data-index="{i}">
                    <div class="answer-option-header">
                        <span class="answer-option-label">{html_lib.escape(item_label)} {i + 1}</span>
                        <button type="button" class="answer-option-remove-btn" title="{html_lib.escape(remove_title)}">×</button>
                    </div>
                    <textarea class="answer-option-textarea ckeditor-enabled" name="{html_lib.escape(name)}_item_{i}" rows="2" data-index="{i}">{option_html}</textarea>
                </div>
            ''')

        hidden_json = html_lib.escape(json.dumps(options, ensure_ascii=False), quote=False)
        chunks.append(f'''
            </div>
            <button type="button" class="answer-option-add-btn">{html_lib.escape(add_label)}</button>
            <textarea name="{html_lib.escape(name)}" class="answer-options-hidden" style="display:none;">{hidden_json}</textarea>
        </div>
        ''')

        return ''.join(chunks)

    def _posted_item_options(self, data, name):
        items = []
        for index in range(50):
            key = f'{name}_item_{index}'
            if key not in data:
                break
            items.append(data.get(key) or '')
        return items

    def _parse_hidden_list(self, hidden_value):
        if isinstance(hidden_value, list):
            return hidden_value
        if hidden_value in (None, ''):
            return []
        try:
            parsed = json.loads(hidden_value)
        except (json.JSONDecodeError, TypeError):
            return []
        return parsed if isinstance(parsed, list) else []

    def value_from_datadict(self, data, files, name):
        hidden = self._parse_hidden_list(data.get(name))
        items = self._posted_item_options(data, name)
        hidden_filled = nonempty_options(hidden)
        item_filled = nonempty_options(items)
        # CKEditor often updates the named item textareas even when the hidden
        # JSON payload is still [] (submit race). Prefer the richer payload.
        if len(item_filled) > len(hidden_filled):
            return items
        if hidden_filled:
            return hidden
        return items or hidden

    def value_omitted_from_data(self, data, files, name):
        if name in data:
            return False
        return f'{name}_item_0' not in data


class AnswerOptionsFormField(forms.JSONField):
    """JSON list field for answer options — accepts widget output (list) or JSON text."""

    def __init__(self, *args, widget=None, **kwargs):
        kwargs.setdefault('required', False)
        if widget is None:
            widget = AnswerOptionsWidget()
        kwargs['widget'] = widget
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        if value in (None, ''):
            return '[]'
        if isinstance(value, list):
            return json.dumps(value, ensure_ascii=False)
        return value

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value in self.empty_values:
            return []
        if isinstance(value, str) and not value.strip():
            return []
        return _coerce_json_list(value, empty=[])

    def bound_data(self, data, initial):
        if data is not None:
            return data
        return initial

    def has_changed(self, initial, data):
        initial_list = nonempty_options(
            initial if isinstance(initial, list) else self.to_python(initial),
        )
        data_list = nonempty_options(
            data if isinstance(data, list) else self.to_python(data),
        )
        return initial_list != data_list