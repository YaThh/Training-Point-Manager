from rest_framework.pagination import PageNumberPagination

class ActivityPaginator(PageNumberPagination):
    page_size = 4

class NewsPaginator(PageNumberPagination):
    page_size = 4