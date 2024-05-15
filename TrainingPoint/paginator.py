from rest_framework.pagination import PageNumberPagination

class ActivityPaginator(PageNumberPagination):
    page_size = 4

class NewsPaginator(PageNumberPagination):
    page_size = 4

class MissingPointReportPaginator(PageNumberPagination):
    page_size = 5

class ClassificationPaginator(PageNumberPagination):
    page_size = 4