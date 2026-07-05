"""Reading passage admin inlines — link questions to unsaved group rows via inline index."""

from __future__ import annotations

from django.forms.models import BaseInlineFormSet

from portals.models import ReadingQuestion, ReadingQuestionGroup


class ReadingQuestionGroupInlineFormSet(BaseInlineFormSet):
    pass


class ReadingQuestionInlineFormSet(BaseInlineFormSet):
    pass


def link_pending_reading_question_groups(
    group_formset: ReadingQuestionGroupInlineFormSet | None,
    question_formset: ReadingQuestionInlineFormSet | None,
) -> None:
    """After save_related, attach questions that referenced an unsaved group inline row."""
    if not question_formset:
        return

    saved_groups_in_form_order: list[ReadingQuestionGroup] = []
    if group_formset is not None:
        for group_form in group_formset.forms:
            if not group_form.cleaned_data or group_form.cleaned_data.get('DELETE'):
                continue
            if group_form.instance.pk:
                saved_groups_in_form_order.append(group_form.instance)

    for question_form in question_formset.forms:
        if not question_form.cleaned_data or question_form.cleaned_data.get('DELETE'):
            continue
        if not question_form.instance.pk:
            continue

        pending_index = getattr(question_form, '_pending_group_index', None)
        if pending_index is None:
            continue
        if 0 <= pending_index < len(saved_groups_in_form_order):
            group = saved_groups_in_form_order[pending_index]
            if question_form.instance.group_id != group.pk:
                question_form.instance.group = group
                question_form.instance.save(update_fields=['group'])
