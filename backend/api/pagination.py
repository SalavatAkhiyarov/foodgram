from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


class RecipePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


class LimitPagination(LimitOffsetPagination):
    default_limit = 6
    limit_query_param = 'limit'
