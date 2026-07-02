import json

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from portals.models import ListeningQuestion, QuizQuestion


class ListeningQuestionAdminForm(forms.ModelForm):
    class Meta:
        model = ListeningQuestion
        fields = ('order', 'question', 'answer_options', 'correct_answer')
        widgets = {
            'question': CKEditorWidget(),
            'answer_options': forms.Textarea(
                attrs={'rows': 4, 'class': 'vLargeTextField portal-quiz-json-field'},
            ),
            'correct_answer': forms.TextInput(attrs={'class': 'vTextField'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer_options'].required = False
        self.fields['correct_answer'].required = False
        self.fields['answer_options'].help_text = _(
            'Optional JSON list of choices, e.g. ["Option A", "Option B", "Option C"]. '
            'Leave empty for a free-text answer.',
        )
        self.fields['correct_answer'].help_text = _(
            'Required only when at least two answer options are set.',
        )
        if self.instance and self.instance.pk:
            options = self.instance.answer_options or []
            if isinstance(options, list):
                self.initial['answer_options'] = json.dumps(
                    options,
                    ensure_ascii=False,
                    indent=2,
                )

    def clean_answer_options(self):
        raw = self.cleaned_data.get('answer_options')
        if raw in (None, '', []):
            return []
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw or '[]')
            except json.JSONDecodeError as exc:
                raise ValidationError(_('Enter a valid JSON list of answer options.')) from exc
        elif isinstance(raw, list):
            parsed = raw
        else:
            raise ValidationError(_('Enter a valid JSON list of answer options.'))

        if not isinstance(parsed, list):
            raise ValidationError(_('Answer options must be a JSON list.'))

        options = [str(item).strip() for item in parsed if str(item).strip()]
        if len(options) < 2:
            return []
        return options

    def clean(self):
        cleaned = super().clean()
        options = cleaned.get('answer_options') or []
        correct = (cleaned.get('correct_answer') or '').strip()
        if len(options) < 2:
            cleaned['answer_options'] = []
            cleaned['correct_answer'] = ''
            return cleaned
        if not correct:
            self.add_error('correct_answer', _('Enter the correct answer.'))
        elif correct not in options:
            self.add_error(
                'correct_answer',
                _('Correct answer must exactly match one of the options.'),
            )
        else:
            cleaned['correct_option_index'] = options.index(correct)
        return cleaned


class QuizQuestionAdminForm(forms.ModelForm):
    student_response_preview = forms.CharField(
        required=False,
        label=_('Student response'),
        help_text=_(
            'Students write their essay here during the quiz. '
            'This preview is empty and is not saved.',
        ),
        widget=forms.Textarea(
            attrs={
                'rows': 6,
                'class': 'vLargeTextField quiz-student-response-preview',
                'placeholder': _('Write your response here…'),
                'readonly': 'readonly',
                'tabindex': '-1',
            },
        ),
    )

    class Meta:
        model = QuizQuestion
        fields = (
            'order',
            'prompt_type',
            'question',
            'media_file',
            'media_url',
            'answer_options',
            'correct_answer',
            'student_response_preview',
        )
        widgets = {
            'prompt_type': forms.Select(attrs={'class': 'quiz-prompt-type', 'data-quiz-prompt-type': ''}),
            'question': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'vLargeTextField quiz-question-input',
                    'data-quiz-field': 'question',
                },
            ),
            'media_file': forms.FileInput(
                attrs={
                    'class': 'quiz-media-file-input',
                    'data-quiz-field': 'media_file',
                },
            ),
            'media_url': forms.URLInput(
                attrs={
                    'class': 'vTextField quiz-media-url-input',
                    'data-quiz-field': 'media_url',
                    'placeholder': 'https://',
                },
            ),
            'answer_options': forms.Textarea(
                attrs={'rows': 4, 'class': 'vLargeTextField portal-quiz-json-field'},
            ),
            'correct_answer': forms.TextInput(attrs={'class': 'vTextField'}),
        }

    class Media:
        css = {'all': ('portals/css/quiz-question-admin.css',)}
        js = ('portals/admin/js/quiz-question-admin.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prompt_type'].label = _('Question type')
        self.fields['answer_options'].help_text = _(
            'JSON list of choices, e.g. ["Option A", "Option B", "Option C"]',
        )
        self.fields['correct_answer'].help_text = _(
            'Must exactly match one of the options in the list above.',
        )

        manual = self._quiz_is_manual()
        essay = self._quiz_is_essay()
        self.fields['student_response_preview'].initial = ''
        if essay:
            self.fields['answer_options'].required = False
            self.fields['correct_answer'].required = False
        elif manual:
            self.fields['answer_options'].required = False
            self.fields['correct_answer'].required = False
            self.fields['answer_options'].help_text = _(
                'Not used for Listening / Speaking quizzes.',
            )
            self.fields['correct_answer'].help_text = _(
                'Not used for Listening / Speaking quizzes.',
            )

        if self.instance and self.instance.pk:
            options = self.instance.answer_options or []
            if isinstance(options, list):
                self.initial['answer_options'] = json.dumps(
                    options,
                    ensure_ascii=False,
                    indent=2,
                )

    def _post_flag(self, name):
        if not self.data:
            return False
        return self.data.get(name) in ('on', 'true', 'True', '1')

    def _quiz_is_manual(self):
        quiz = getattr(self.instance, 'quiz', None)
        if quiz and quiz.is_manual_grading:
            return True
        return any(
            self._post_flag(flag)
            for flag in ('is_listening', 'is_essay', 'is_speaking')
        )

    def _quiz_is_essay(self):
        quiz = getattr(self.instance, 'quiz', None)
        if quiz and quiz.is_essay:
            return True
        return self._post_flag('is_essay')

    def clean_answer_options(self):
        if self._quiz_is_manual():
            return []

        raw = self.cleaned_data.get('answer_options')
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw or '[]')
            except json.JSONDecodeError as exc:
                raise ValidationError(_('Enter a valid JSON list of answer options.')) from exc
        elif isinstance(raw, list):
            parsed = raw
        else:
            raise ValidationError(_('Enter a valid JSON list of answer options.'))

        if not isinstance(parsed, list):
            raise ValidationError(_('Answer options must be a JSON list.'))

        options = [str(item).strip() for item in parsed if str(item).strip()]
        if len(options) < 2:
            raise ValidationError(_('Add at least two answer options.'))
        return options

    def clean(self):
        cleaned = super().clean()
        if self._quiz_is_manual():
            cleaned['answer_options'] = []
            cleaned['correct_answer'] = ''
            return cleaned

        options = cleaned.get('answer_options') or []
        correct = (cleaned.get('correct_answer') or '').strip()
        if options:
            if not correct:
                self.add_error('correct_answer', _('Enter the correct answer.'))
            elif correct not in options:
                self.add_error(
                    'correct_answer',
                    _('Correct answer must exactly match one of the options.'),
                )

        prompt_type = cleaned.get('prompt_type')
        question = (cleaned.get('question') or '').strip()
        media_file = cleaned.get('media_file') or getattr(self.instance, 'media_file', None)
        media_url = (cleaned.get('media_url') or '').strip()

        if prompt_type == QuizQuestion.PromptType.TEXT:
            if not question:
                self.add_error('question', _('Enter the question text.'))
        elif not media_file and not media_url:
            self.add_error(
                'media_file',
                _('Upload a file or provide a media URL for this question type.'),
            )

        if options and correct in options:
            cleaned['correct_option_index'] = options.index(correct)

        return cleaned
