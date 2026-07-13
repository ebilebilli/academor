"""Reusable admin order dropdown: 0 = first, 1 = next, …"""

from django import forms


def _position_label(position: int) -> str:
    """Human label for a 0-based sort position (0 = first)."""
    if position == 0:
        return '0 — First'
    if position == 1:
        return '1 — Next'
    if position == 2:
        return '2 — 3rd'
    if position == 3:
        return '3 — 4th'
    if position == 4:
        return '4 — 5th'
    return f'{position} — {position + 1}th'


def build_order_choices(queryset, instance=None, *, extra_last=False):
    """
    Build (value, label) pairs for an order dropdown.

    ``extra_last`` adds one slot at the end (useful when creating a new row).
    """
    count = queryset.count()
    if instance is not None and instance.pk:
        upper = max(count - 1, getattr(instance, 'order', 0) or 0)
    else:
        upper = count if extra_last else max(count - 1, 0)

    return [(i, _position_label(i)) for i in range(upper + 1)]


def apply_order_choice_field(form, *, model, instance=None, field_name='order'):
    """Replace a numeric order field with a position dropdown on admin forms."""
    if field_name not in form.fields:
        return

    field = form.fields[field_name]
    is_new = instance is None or not instance.pk
    choices = build_order_choices(
        model.objects.all(),
        instance=instance,
        extra_last=is_new,
    )
    initial = 0
    if instance is not None and instance.pk:
        initial = getattr(instance, field_name, 0) or 0
    elif is_new:
        initial = model.objects.count()

    form.fields[field_name] = forms.TypedChoiceField(
        choices=choices,
        coerce=int,
        label=field.label,
        help_text=getattr(field, 'help_text', '') or (
            '0 = first, 1 = next, 2 = following, and so on. '
            'On save, the site, admin list, and navigation dropdown update.'
        ),
        initial=initial,
        required=field.required,
    )


class OrderChoiceModelForm(forms.ModelForm):
    """
    ModelForm mixin-style base: subclasses set ``order_model`` or use ``Meta.model``.
    """

    order_field_name = 'order'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = getattr(self, 'order_model', None) or self._meta.model
        apply_order_choice_field(
            self,
            model=model,
            instance=self.instance,
            field_name=self.order_field_name,
        )
