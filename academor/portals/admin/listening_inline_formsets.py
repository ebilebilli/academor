"""Listening audio admin inlines — link questions to unsaved group rows via inline index."""

from __future__ import annotations

from django.forms.models import BaseInlineFormSet

from portals.models import ListeningQuestion, ListeningQuestionGroup


class ListeningQuestionGroupInlineFormSet(BaseInlineFormSet):
    pass


class ListeningQuestionInlineFormSet(BaseInlineFormSet):
    pass


def link_pending_listening_question_groups(
    group_formset: ListeningQuestionGroupInlineFormSet | None,
    question_formset: ListeningQuestionInlineFormSet | None,
) -> None:
    """After save_related, attach questions that referenced an unsaved group inline row."""
    if not question_formset:
        return

    saved_groups_in_form_order: list[ListeningQuestionGroup] = []
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
            question = question_form.instance
            update_fields = []
            if question.group_id != group.pk:
                question.group = group
                update_fields.append('group')
            # Options live on the group for map/plan tasks.
            if question.answer_options:
                question.answer_options = []
                update_fields.append('answer_options')
            if question.spr_correct_answers:
                question.spr_correct_answers = None
                update_fields.append('spr_correct_answers')
            if update_fields:
                question.save(update_fields=update_fields)
