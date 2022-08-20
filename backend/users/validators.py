from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError('Имя ''me'' недопустимо', params={'value': value})
