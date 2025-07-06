from django.core.exceptions import ValidationError


def validate_username(username):
    """Функция проверяет, что введенный логин не запрещен для использованию."""
    # Список запрещенных логинов.
    UNALLOWED_LOGINS = (
        'me',
    )

    if username.lower() in UNALLOWED_LOGINS:
        error_message = f'Логин {username} запрещен! Придумайте другой логин.'
        raise ValidationError(error_message)

    return username
