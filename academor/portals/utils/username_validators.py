"""Username validation — allow spaces in display/login names."""

import re

from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# Same as Django's UnicodeUsernameValidator, plus spaces.
PORTAL_USERNAME_PATTERN = re.compile(r'^[\w.@+\- ]+\Z')

portal_username_validator = RegexValidator(
    PORTAL_USERNAME_PATTERN,
    message=_(
        'Enter a valid username. This value may contain letters, digits, spaces, '
        'and @/./+/-/_ characters only.'
    ),
    code='invalid',
)


def apply_portal_username_validators():
    """Replace default User.username validators (no spaces) project-wide."""
    from django.contrib.auth import get_user_model

    field = get_user_model()._meta.get_field('username')
    field.validators = [portal_username_validator]
