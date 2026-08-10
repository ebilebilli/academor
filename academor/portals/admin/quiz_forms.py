import json

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from portals.admin.widgets import AnswerOptionsFormField, AnswerOptionsWidget
from portals.models import ListeningQuestion, Quiz, QuizCategory, QuizQuestion
from portals.models.reading_models import (
    GROUP_QUESTION_TYPES,
    MATCHING_QUESTION_TYPES,
    ReadingQuestion,
    ReadingQuestionGroup,
    ReadingQuestionType,
    TEXT_QUESTION_TYPES,
)
from portals.models.speaking_models import SpeakingPart
from portals.utils.sat_spr_validation import plain_spr_text


class ListeningQuestionAdminForm(forms.ModelForm):
    answer_options = AnswerOptionsFormField()

    class Meta:
        model = ListeningQuestion
        fields = ('order', 'question', 'answer_options', 'correct_answer')
        widgets = {
            'question': CKEditorUploadingWidget(),
            'correct_answer': forms.TextInput(attrs={'class': 'vTextField'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer_options'].required = False
        self.fields['correct_answer'].required = False
        self.fields['answer_options'].help_text = _(
            'Optional: Add answer choices using the + button. Each option can contain rich text. '
            'Leave empty for a free-text answer.',
        )
        self.fields['correct_answer'].help_text = _(
            'Required only when at least two answer options are set.',
        )
        if self.instance and self.instance.pk:
            options = self.instance.answer_options or []
            if isinstance(options, list):
                self.initial['answer_options'] = options

    class Media:
        css = {'all': ('portals/css/answer-options-widget.css',)}
        js = ('portals/admin/js/answer-options-widget.js',)

    def clean_answer_options(self):
        raw = self.cleaned_data.get('answer_options')
        if raw in (None, '', []):
            return []
        # The AnswerOptionsWidget returns a list directly
        if isinstance(raw, list):
            parsed = raw
        elif isinstance(raw, str):
            try:
                parsed = json.loads(raw or '[]')
            except json.JSONDecodeError as exc:
                raise ValidationError(_('Enter a valid JSON list of answer options.')) from exc
        else:
            raise ValidationError(_('Enter a valid JSON list of answer options.'))

        if not isinstance(parsed, list):
            raise ValidationError(_('Answer options must be a JSON list.'))

        # Filter out empty options but keep HTML content
        options = [item if item and str(item).strip() else '' for item in parsed]
        # Remove completely empty options
        options = [item for item in options if item and str(item).strip()]
        
        if len(options) < 2:
            return []
        return options

    def clean(self):
        cleaned = super().clean()
        options = cleaned.get('answer_options') or []
        correct = (cleaned.get('correct_answer') or '').strip()
        if len(options) < 2:
            cleaned['answer_options'] = []
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
    answer_options = AnswerOptionsFormField()
    # Visible 1-based selector — scoring source of truth for MCQ (avoids CKEditor HTML mismatch).
    correct_option_number = forms.IntegerField(
        label=_('Correct option'),
        required=False,
        min_value=1,
        help_text=_(
            'Enter 1 for Option 1, 2 for Option 2, 3 for Option 3, 4 for Option 4. '
            'This is what auto-scoring uses.',
        ),
        widget=forms.NumberInput(attrs={'class': 'vIntegerField', 'style': 'max-width: 6rem;'}),
    )
    spr_correct_answers = AnswerOptionsFormField(
        widget=AnswerOptionsWidget(
            item_label='Answer',
            add_button_label='Add correct answer',
            remove_title='Remove answer',
        ),
    )
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
            'question_type',
            'question',
            'media_file',
            'media_url',
            'answer_options',
            'correct_answer',
            'correct_option_index',
            'spr_correct_answers',
            'spr_max_length',
            'student_response_preview',
        )
        widgets = {
            'prompt_type': forms.Select(attrs={'class': 'quiz-prompt-type', 'data-quiz-prompt-type': ''}),
            'question_type': forms.Select(attrs={'class': 'quiz-question-type', 'data-quiz-question-type': ''}),
            'question': CKEditorUploadingWidget(),
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
            # Stored from correct_option_number; do not edit as free HTML (silent revert bug).
            'correct_answer': forms.HiddenInput(),
            'correct_option_index': forms.HiddenInput(),
            'spr_max_length': forms.NumberInput(attrs={'class': 'vIntegerField'}),
        }

    class Media:
        css = {'all': ('portals/css/quiz-question-admin.css', 'portals/css/answer-options-widget.css',)}
        js = (
            'portals/admin/js/quiz-question-admin.js',
            'portals/admin/js/answer-options-widget.js',
            'portals/admin/js/quiz-question-type-toggle.js',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prompt_type'].label = _('Question type')
        if 'question_type' in self.fields:
            self.fields['question_type'].label = _('Answer type')
        if 'answer_options' in self.fields:
            self.fields['answer_options'].help_text = _(
                'Add answer choices using the + button. Each option can contain rich text.',
            )
        if 'correct_option_number' in self.fields:
            self.fields['correct_option_number'].required = False
        if 'correct_answer' in self.fields:
            self.fields['correct_answer'].required = False
        if 'correct_option_index' in self.fields:
            self.fields['correct_option_index'].required = False
        if 'answer_options' in self.fields:
            self.fields['answer_options'].required = False
        if 'question' in self.fields:
            self.fields['question'].required = False
        if 'spr_correct_answers' in self.fields:
            self.fields['spr_correct_answers'].help_text = _(
                'Add one or more accepted correct answers. Each answer can use rich text '
                '(numbers like 7/2 or 3.5, or equations like y = -x + 19).',
            )
        if 'spr_max_length' in self.fields:
            self.fields['spr_max_length'].required = False
            self.fields['spr_max_length'].help_text = _(
                'Optional. Limits how many characters the student may type. '
                'Leave blank for equations / free-text answers.',
            )

        manual = self._quiz_is_manual()
        essay = self._quiz_is_essay()
        if 'student_response_preview' in self.fields:
            self.fields['student_response_preview'].initial = ''
        if essay:
            if 'answer_options' in self.fields:
                self.fields['answer_options'].required = False
            if 'correct_answer' in self.fields:
                self.fields['correct_answer'].required = False
            if 'correct_option_number' in self.fields:
                self.fields['correct_option_number'].required = False
        elif manual:
            if 'answer_options' in self.fields:
                self.fields['answer_options'].required = False
                self.fields['answer_options'].help_text = _(
                    'Not used for Listening / Speaking quizzes.',
                )
            if 'correct_answer' in self.fields:
                self.fields['correct_answer'].required = False
                self.fields['correct_answer'].help_text = _(
                    'Not used for Listening / Speaking quizzes.',
                )
            if 'correct_option_number' in self.fields:
                self.fields['correct_option_number'].required = False

        if self.instance and self.instance.pk:
            if 'answer_options' in self.fields:
                options = self.instance.answer_options or []
                if isinstance(options, list):
                    self.initial['answer_options'] = options
            if 'spr_correct_answers' in self.fields:
                spr_answers = self.instance.spr_correct_answers or []
                if isinstance(spr_answers, list):
                    self.initial['spr_correct_answers'] = spr_answers
            if 'correct_option_number' in self.fields:
                idx = getattr(self.instance, 'correct_option_index', None)
                if idx is not None:
                    try:
                        self.initial['correct_option_number'] = int(idx) + 1
                    except (TypeError, ValueError):
                        pass

    def _field_on_form(self, name):
        return name in self.fields

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
            for flag in ('is_listening', 'is_essay', 'is_speaking', 'is_reading')
        )

    def _quiz_is_essay(self):
        quiz = getattr(self.instance, 'quiz', None)
        if quiz and quiz.is_essay:
            return True
        return self._post_flag('is_essay')

    def clean_answer_options(self):
        if self._quiz_is_manual():
            return []

        question_type = self.cleaned_data.get('question_type') or self.data.get('question_type')
        if question_type == QuizQuestion.QuestionType.SPR:
            return []

        raw = self.cleaned_data.get('answer_options')
        if isinstance(raw, list):
            parsed = raw
        elif isinstance(raw, str):
            try:
                parsed = json.loads(raw or '[]')
            except json.JSONDecodeError as exc:
                raise ValidationError(_('Enter a valid JSON list of answer options.')) from exc
        elif raw in (None, ''):
            parsed = []
        else:
            raise ValidationError(_('Enter a valid JSON list of answer options.'))

        if not isinstance(parsed, list):
            raise ValidationError(_('Answer options must be a JSON list.'))

        options = [item for item in parsed if item and str(item).strip()]

        # Safety net: if the widget posted empty options (CKEditor sync race),
        # keep the existing saved options instead of wiping the question.
        if len(options) < 2 and self.instance and self.instance.pk:
            existing = [
                item for item in (self.instance.answer_options or [])
                if item and str(item).strip()
            ]
            if len(existing) >= 2:
                return existing

        if len(options) < 2:
            raise ValidationError(_('Add at least two answer options.'))
        return options

    def clean_spr_correct_answers(self):
        raw = self.cleaned_data.get('spr_correct_answers')
        question_type = self.cleaned_data.get('question_type') or self.data.get('question_type')

        if question_type != QuizQuestion.QuestionType.SPR:
            return None

        if isinstance(raw, list):
            parsed = raw
        elif isinstance(raw, str):
            try:
                parsed = json.loads(raw or '[]')
            except json.JSONDecodeError as exc:
                raise ValidationError(_('Enter a valid list of correct answers.')) from exc
        elif raw in (None, ''):
            parsed = []
        else:
            raise ValidationError(_('Enter a valid list of correct answers.'))

        if not isinstance(parsed, list):
            raise ValidationError(_('Correct answers must be a list.'))

        answers = []
        for item in parsed:
            text = str(item or '').strip()
            if not text or not plain_spr_text(text):
                continue
            answers.append(text)

        if not answers and self.instance and self.instance.pk:
            existing = [
                str(item).strip()
                for item in (self.instance.spr_correct_answers or [])
                if str(item).strip() and plain_spr_text(str(item))
            ]
            if existing:
                return existing

        if not answers:
            raise ValidationError(_('Add at least one correct answer.'))

        return answers

    def clean(self):
        cleaned = super().clean()
        question_type = cleaned.get('question_type')
        
        if self._quiz_is_manual():
            cleaned['answer_options'] = []
            cleaned['correct_answer'] = ''
            cleaned['spr_correct_answers'] = None
            cleaned['spr_max_length'] = None
            return cleaned

        if question_type == QuizQuestion.QuestionType.SPR:
            # SPR-specific validation
            cleaned['answer_options'] = []
            cleaned['correct_answer'] = ''
            cleaned['correct_option_index'] = 0

            if not self._field_on_form('spr_correct_answers'):
                return cleaned

            spr_correct_answers = cleaned.get('spr_correct_answers')
            if not spr_correct_answers:
                self.add_error('spr_correct_answers', _('SPR questions must have at least one correct answer.'))
            # spr_max_length is optional (needed only for classic short numeric grid-ins)
        elif question_type == QuizQuestion.QuestionType.MCQ:
            # MCQ-specific validation — correct_option_number is the source of truth.
            cleaned['spr_correct_answers'] = None
            cleaned['spr_max_length'] = None

            answer_options = cleaned.get('answer_options')
            if not answer_options or len(answer_options) < 2:
                self.add_error('answer_options', _('MCQ questions must have at least two answer options.'))
            else:
                option_number = cleaned.get('correct_option_number')
                if option_number in (None, ''):
                    # Keep existing index when the number field was left blank.
                    idx = getattr(self.instance, 'correct_option_index', None)
                    if idx is not None and 0 <= int(idx) < len(answer_options):
                        cleaned['correct_option_index'] = int(idx)
                        cleaned['correct_answer'] = answer_options[int(idx)]
                        cleaned['correct_option_number'] = int(idx) + 1
                    else:
                        self.add_error(
                            'correct_option_number',
                            _('Enter which option is correct (1 = Option 1, 2 = Option 2, …).'),
                        )
                else:
                    try:
                        idx = int(option_number) - 1
                    except (TypeError, ValueError):
                        idx = -1
                    if not (0 <= idx < len(answer_options)):
                        self.add_error(
                            'correct_option_number',
                            _('Enter a number from 1 to %(count)s.') % {'count': len(answer_options)},
                        )
                    else:
                        cleaned['correct_option_index'] = idx
                        cleaned['correct_answer'] = answer_options[idx]
        else:
            # Default case (no specific question type)
            cleaned['spr_correct_answers'] = None
            cleaned['spr_max_length'] = None

            options = cleaned.get('answer_options') or []
            option_number = cleaned.get('correct_option_number')
            if options:
                if option_number in (None, ''):
                    self.add_error(
                        'correct_option_number',
                        _('Enter which option is correct (1 = Option 1, 2 = Option 2, …).'),
                    )
                else:
                    try:
                        idx = int(option_number) - 1
                    except (TypeError, ValueError):
                        idx = -1
                    if not (0 <= idx < len(options)):
                        self.add_error(
                            'correct_option_number',
                            _('Enter a number from 1 to %(count)s.') % {'count': len(options)},
                        )
                    else:
                        cleaned['correct_option_index'] = idx
                        cleaned['correct_answer'] = options[idx]

        prompt_type = cleaned.get('prompt_type')
        question = (cleaned.get('question') or '').strip()
        if not question and self.instance and self.instance.pk:
            # CKEditor sometimes posts an empty textarea if sync races submit.
            existing_question = (self.instance.question or '').strip()
            if existing_question:
                cleaned['question'] = self.instance.question
                question = existing_question

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

        return cleaned


class ReadingQuestionGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ReadingQuestionGroup
        fields = ('order', 'title', 'instructions', 'question_type', 'option_pool')
        widgets = {
            'instructions': CKEditorUploadingWidget(),
            'option_pool': forms.Textarea(
                attrs={'rows': 5, 'class': 'vLargeTextField portal-quiz-json-field'},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['question_type'].choices = [
            (value, label)
            for value, label in ReadingQuestionType.choices
            if value in GROUP_QUESTION_TYPES
        ]
        self.fields['option_pool'].required = False
        if self.instance and self.instance.pk:
            pool = self.instance.option_pool or []
            if isinstance(pool, list):
                self.initial['option_pool'] = json.dumps(pool, ensure_ascii=False, indent=2)

    def clean(self):
        cleaned = super().clean()
        question_type = cleaned.get('question_type')
        if question_type not in MATCHING_QUESTION_TYPES:
            cleaned['option_pool'] = []
        return cleaned

    def clean_option_pool(self):
        question_type = self.cleaned_data.get('question_type') or getattr(self.instance, 'question_type', None)
        if question_type not in MATCHING_QUESTION_TYPES:
            return []
        raw = self.cleaned_data.get('option_pool')
        if raw in (None, '', []):
            return []
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw or '[]')
            except json.JSONDecodeError as exc:
                raise ValidationError(_('Enter a valid JSON list of options.')) from exc
        elif isinstance(raw, list):
            parsed = raw
        else:
            raise ValidationError(_('Enter a valid JSON list of options.'))
        if not isinstance(parsed, list):
            raise ValidationError(_('Option pool must be a JSON list.'))
        options = [str(item).strip() for item in parsed if str(item).strip()]
        if len(options) < 2:
            raise ValidationError(_('Add at least two options to the pool.'))
        return options


class ReadingQuestionAdminForm(forms.ModelForm):
    group_ref = forms.ChoiceField(
        required=False,
        label=_('Question group'),
        choices=[('', '---------')],
        help_text=_(
            'Choose a matching group. New groups appear here as soon as you enter a title below.',
        ),
    )
    word_limit = forms.IntegerField(
        required=False,
        min_value=1,
        label=_('Word limit'),
        help_text=_('Maximum words accepted from the student. Leave empty for no limit.'),
    )
    case_insensitive = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Case insensitive'),
        help_text=_('Ignore letter case when auto-scoring text answers.'),
    )
    accept_alternatives_text = forms.CharField(
        required=False,
        label=_('Alternative acceptable answers'),
        help_text=_('One answer per line. Also counted as correct during auto-scoring.'),
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'vLargeTextField'}),
    )

    class Meta:
        model = ReadingQuestion
        fields = (
            'order',
            'group',
            'question_type',
            'question',
            'answer_options',
            'correct_answer',
            'question_config',
        )
        widgets = {
            'question': CKEditorUploadingWidget(),
            'answer_options': forms.Textarea(
                attrs={'rows': 4, 'class': 'vLargeTextField portal-quiz-json-field'},
            ),
            'question_config': forms.Textarea(
                attrs={'rows': 4, 'class': 'vLargeTextField portal-quiz-json-field'},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_group_index = None
        # Inline admin lists group_ref only; empty_form still instantiates this form.
        if 'group' in self.fields:
            self.fields['group'].required = False
            self.fields['group'].widget = forms.HiddenInput()
        if 'group_ref' in self.fields:
            self.fields['group_ref'].widget.attrs.update({'class': 'reading-question-group-ref'})
        self.fields['answer_options'].required = False
        self.fields['question_config'].required = False
        self.fields['answer_options'].help_text = _(
            'JSON list for multiple choice only. Leave empty for fixed or group options.',
        )
        self.fields['question_config'].help_text = _(
            'Advanced JSON only. Prefer the fields below for word limits and alternatives.',
        )
        config = {}
        if self.instance and self.instance.pk:
            options = self.instance.answer_options or []
            if isinstance(options, list):
                self.initial['answer_options'] = json.dumps(options, ensure_ascii=False, indent=2)
            config = self.instance.question_config or {}
            if isinstance(config, dict):
                self.initial['question_config'] = json.dumps(config, ensure_ascii=False, indent=2)
            if self.instance.group_id:
                self.initial['group_ref'] = f'id:{self.instance.group_id}'
        if isinstance(config, dict):
            if config.get('word_limit') not in (None, ''):
                self.initial['word_limit'] = config.get('word_limit')
            if 'case_insensitive' in config:
                self.initial['case_insensitive'] = bool(config.get('case_insensitive', True))
            alternatives = config.get('accept_alternatives') or []
            if isinstance(alternatives, list) and alternatives:
                self.initial['accept_alternatives_text'] = '\n'.join(
                    str(item).strip()
                    for item in alternatives
                    if str(item).strip()
                )

    def _resolve_passage_id(self):
        if self.instance and self.instance.passage_id:
            return self.instance.passage_id
        passage_field = self.fields.get('passage')
        if passage_field and getattr(passage_field, 'initial', None):
            return passage_field.initial
        raw = ''
        if self.data:
            raw = (
                self.data.get(self.add_prefix('passage'))
                or self.data.get('passage')
                or ''
            )
        try:
            return int(raw) if raw else None
        except (TypeError, ValueError):
            return None

    def clean_group_ref(self):
        return (self.cleaned_data.get('group_ref') or '').strip()

    def clean_accept_alternatives_text(self):
        raw = (self.cleaned_data.get('accept_alternatives_text') or '').strip()
        if not raw:
            return []
        alternatives = []
        for line in raw.replace(',', '\n').splitlines():
            value = line.strip()
            if value and value not in alternatives:
                alternatives.append(value)
        return alternatives

    def clean(self):
        cleaned = super().clean()
        question_type = cleaned.get('question_type')
        if question_type in {ReadingQuestionType.TFNG, ReadingQuestionType.YNNG}:
            cleaned['answer_options'] = []
        if question_type in TEXT_QUESTION_TYPES:
            cleaned['answer_options'] = []
            config = cleaned.get('question_config') or {}
            if not isinstance(config, dict):
                config = {}
            word_limit = cleaned.get('word_limit')
            if word_limit in (None, ''):
                config.pop('word_limit', None)
            else:
                config['word_limit'] = int(word_limit)
            if cleaned.get('case_insensitive', True):
                config['case_insensitive'] = True
            else:
                config['case_insensitive'] = False
            alternatives = cleaned.get('accept_alternatives_text') or []
            if alternatives:
                config['accept_alternatives'] = alternatives
            else:
                config.pop('accept_alternatives', None)
            cleaned['question_config'] = config

        cleaned.pop('word_limit', None)
        cleaned.pop('case_insensitive', None)
        cleaned.pop('accept_alternatives_text', None)

        self._pending_group_index = None
        group_ref = (cleaned.pop('group_ref', '') or '').strip()
        passage_id = self._resolve_passage_id()

        if not group_ref:
            cleaned['group'] = None
            self.instance.group = None
            return cleaned

        if group_ref.startswith('id:'):
            try:
                group_pk = int(group_ref[3:])
            except (TypeError, ValueError):
                self.add_error('group_ref', _('Invalid question group.'))
                cleaned['group'] = None
                self.instance.group = None
                return cleaned
            group_qs = ReadingQuestionGroup.objects.filter(pk=group_pk)
            if passage_id:
                group_qs = group_qs.filter(passage_id=passage_id)
            group = group_qs.first()
            if not group:
                self.add_error('group_ref', _('Selected question group was not found.'))
                cleaned['group'] = None
                self.instance.group = None
                return cleaned
            cleaned['group'] = group
            self.instance.group = group
            return cleaned

        if group_ref.startswith('idx:'):
            try:
                self._pending_group_index = int(group_ref[4:])
            except (TypeError, ValueError):
                self.add_error('group_ref', _('Invalid question group.'))
            cleaned['group'] = None
            self.instance.group = None
            return cleaned

        self.add_error('group_ref', _('Invalid question group.'))
        cleaned['group'] = None
        self.instance.group = None
        return cleaned

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
        return [str(item).strip() for item in parsed if str(item).strip()]

    def clean_question_config(self):
        raw = self.cleaned_data.get('question_config')
        if raw in (None, '', {}):
            return {}
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw or '{}')
            except json.JSONDecodeError as exc:
                raise ValidationError(_('Enter a valid JSON object for question config.')) from exc
        elif isinstance(raw, dict):
            parsed = raw
        else:
            raise ValidationError(_('Question config must be a JSON object.'))
        if not isinstance(parsed, dict):
            raise ValidationError(_('Question config must be a JSON object.'))
        return parsed

    class Media:
        css = {'all': ('portals/css/quiz-question-admin.css',)}
        js = ('portals/admin/js/reading-passage-admin.js',)


class SpeakingPartAdminForm(forms.ModelForm):
    new_quiz_topic = forms.CharField(
        required=False,
        label=_('New quiz topic'),
        help_text=_('Required when no speaking quiz is selected — a new speaking quiz will be created.'),
        widget=forms.TextInput(attrs={'class': 'vTextField'}),
    )
    new_quiz_category = forms.ModelChoiceField(
        required=False,
        label=_('New quiz category'),
        queryset=QuizCategory.objects.prefetch_related('services').order_by('order', 'name', 'id'),
        help_text=_('Category for the new speaking quiz.'),
    )

    class Meta:
        model = SpeakingPart
        fields = (
            'quiz',
            'order',
            'part_type',
            'title',
            'instructions',
            'cue_card_topic',
            'cue_card_bullets',
            'preparation_seconds',
            'default_answer_seconds',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quiz'].required = False
        self.fields['quiz'].queryset = Quiz.objects.filter(is_speaking=True).select_related('category')
        if self.instance and self.instance.pk:
            self.fields['new_quiz_topic'].widget = forms.HiddenInput()
            self.fields['new_quiz_category'].widget = forms.HiddenInput()
            self.fields['quiz'].required = True
        else:
            self.fields['quiz'].help_text = _(
                'Select an existing speaking quiz, or leave empty and fill in new quiz topic and category below.',
            )

    def clean(self):
        cleaned = super().clean()
        quiz = cleaned.get('quiz')
        topic = (cleaned.get('new_quiz_topic') or '').strip()
        category = cleaned.get('new_quiz_category')

        if self.instance and self.instance.pk:
            if not quiz:
                raise ValidationError({'quiz': _('Select the speaking quiz this part belongs to.')})
            if not quiz.is_speaking:
                raise ValidationError({'quiz': _('Select a speaking quiz.')})
            return cleaned

        if quiz:
            if not quiz.is_speaking:
                raise ValidationError({'quiz': _('Select a speaking quiz.')})
            return cleaned

        if not topic:
            self.add_error('new_quiz_topic', _('Enter a topic for the new speaking quiz.'))
        if not category:
            self.add_error('new_quiz_category', _('Select a category for the new speaking quiz.'))
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.quiz_id:
            quiz = Quiz.objects.create(
                category=self.cleaned_data['new_quiz_category'],
                topic=self.cleaned_data['new_quiz_topic'].strip(),
                is_speaking=True,
                is_listening=False,
                is_essay=False,
                is_reading=False,
                is_time_limited=False,
                time_limit_minutes=None,
            )
            quiz.full_clean()
            instance.quiz = quiz
        if commit:
            instance.save()
            self.save_m2m()
        return instance

