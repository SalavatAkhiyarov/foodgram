from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


class RecipePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'

    def paginate_queryset(self, queryset, request, view=None):
        print("DEBUG! Pagination called, limit param:",
              request.query_params.get('limit'))
        return super().paginate_queryset(queryset, request, view)


class LimitPagination(LimitOffsetPagination):
    default_limit = 6
    limit_query_param = 'limit'
    max_limit = 100
