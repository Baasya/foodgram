from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_SIZE, PAGE_SIZE_MAX


class CustomPagination(PageNumberPagination):
    """Пагинатор для управления количеством элементов на странице."""
    page_size = PAGE_SIZE
    max_page_size = PAGE_SIZE_MAX
    page_size_query_param = 'limit'
    page_query_param = 'page'
