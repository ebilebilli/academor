from pathlib import Path

from django import forms
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _

from portals.models import LessonHomework

HOMEWORK_MAX_FILE_BYTES = 10 * 1024 * 1024
HOMEWORK_ALLOWED_EXTENSIONS = frozenset({'pdf', 'doc', 'docx', 'txt'})
HOMEWORK_EXTENSION_TO_KIND = {
    'pdf': LessonHomework.FileKind.PDF,
    'doc': LessonHomework.FileKind.WORD,
    'docx': LessonHomework.FileKind.WORD,
    'txt': LessonHomework.FileKind.TXT,
}


def homework_file_extension(filename: str) -> str:
    return Path(filename or '').suffix.lower().lstrip('.')


def homework_file_kind_for_name(filename: str) -> str:
    return HOMEWORK_EXTENSION_TO_KIND.get(homework_file_extension(filename), '')


class StudentLessonHomeworkForm(forms.Form):
    text = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Ev tapşırığınızı buraya yazın…'),
            }
        ),
        label=_('Ev tapşırığı mətni'),
    )
    file = forms.FileField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,application/pdf,'
                'application/msword,'
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                'text/plain',
            }
        ),
        label=_('Ev tapşırığı faylı'),
        help_text=_('PDF, Word (.doc, .docx) və ya mətn (.txt). Maks. 10 MB.'),
    )

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        super().__init__(*args, **kwargs)
        if instance and instance.text:
            self.fields['text'].initial = instance.text

    def clean_text(self):
        return (self.cleaned_data.get('text') or '').strip()

    def clean_file(self):
        uploaded = self.cleaned_data.get('file')
        if not uploaded:
            return None
        name = getattr(uploaded, 'name', '') or ''
        ext = homework_file_extension(name)
        if ext not in HOMEWORK_ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                _('PDF, Word və ya mətn faylı yükləyin (.pdf, .doc, .docx, .txt).')
            )
        size = getattr(uploaded, 'size', None)
        if size is not None and size > HOMEWORK_MAX_FILE_BYTES:
            raise forms.ValidationError(_('Fayl 10 MB-dan kiçik olmalıdır.'))
        return uploaded

    def clean(self):
        cleaned = super().clean()
        text = cleaned.get('text') or ''
        uploaded = cleaned.get('file')
        has_existing_file = bool(
            self.instance and self.instance.file and self.instance.file.name
        )
        if not text and not uploaded and not has_existing_file:
            raise forms.ValidationError(
                _('Ev tapşırığı mətni yazın və ya PDF, Word və ya mətn faylı yükləyin.')
            )
        return cleaned

    def save(self, *, lesson, student):
        text = self.cleaned_data.get('text') or ''
        uploaded = self.cleaned_data.get('file')
        homework = self.instance
        if homework is None:
            homework = LessonHomework(lesson=lesson, student=student)

        homework.text = text

        if uploaded:
            if homework.pk and homework.file and homework.file.name:
                homework.file.delete(save=False)
            raw = uploaded.read()
            filename = Path(getattr(uploaded, 'name', '') or 'homework').name
            homework.original_filename = filename
            homework.file_kind = homework_file_kind_for_name(filename)
            homework.file.save(filename, ContentFile(raw), save=False)
        elif not homework.file or not homework.file.name:
            homework.original_filename = ''
            homework.file_kind = ''

        homework.save()
        return homework
