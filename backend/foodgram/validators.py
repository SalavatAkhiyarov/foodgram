import re

from django.core.exceptions import ValidationError


def validate_username(value):
    allowed_pattern = r'^[\w.@+-]+\Z'
    allowed_characters = 'буквы латинского алфавита, цифры и символы _/./@/+/-'
    if not re.match(allowed_pattern, value):
        invalid_characters = re.sub(r'[\w.@+-]', '', value)
        unique_characters = ''.join(sorted(set(invalid_characters)))
        raise ValidationError(
            f'Username содержит недопустимые символы: {unique_characters}. '
            f'Допустимые символы: {allowed_characters}.'
        )
    return value
