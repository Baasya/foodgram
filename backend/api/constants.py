# Файл для хранения констант, используемых в приложениях.

USERNAME_MAX_LENGHT = 150
EMAIL_MAX_LENGHT = 254
FIRST_NAME_MAX_LENGHT = 150
LAST_NAME_MAX_LENGHT = 150
PASSWORD_MAX_LENGHT = 150
TAG_NAME_MAX_LENGTH = 32
TAG_SLUG_MAX_LENGTH = 32
INGREDIENT_NAME_MAX_LENGTH = 128
MEASUREMENT_UNIT_MAX_LENGTH = 64
RECIPE_NAME_MAX_LENGTH = 256
COOKING_TIME_MIN_VALUE = 1
INGREDIENTS_MIN_AMOUNT = 1
PAGE_SIZE = 6
PAGE_SIZE_MAX = 60

LOGIN_ERROR_MESSAGE = (
    'Логин может содержать только английские '
    'буквы, цифры или символы "@", ".", "_", "+", "-".'
)
SLUG_ERROR_MESSAGE = (
    'Slug может содержать только английские '
    'буквы, цифры или символ "_".'
)
COOKING_TIME_ERROR_MESSAGE = (
    'Время приготовления не может быть'
    'менее 1 минуты.'
)
INGREDIENTS_AMOUNT_ERROR_MESSAGE = (
    'Рецепт должен содержать хотя бы 1 ингредиент.'
)
SUBSCRIBE_ER_MESSAGE = (
    'Вы не можете подписаться на себя.'
)
SUBSCRIBE_EXIST_ER_MESSAGE = (
    'Вы уже подписаны на этого пользователя.'
)
SUBSCRIBE_NOT_EXIST_ER_MESSAGE = (
    'Вы не подписаны на этого пользователя.'
)
