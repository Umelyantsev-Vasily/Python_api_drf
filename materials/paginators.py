from rest_framework.pagination import PageNumberPagination

class MaterialsPaginator(PageNumberPagination):
    """
    Универсальный пагинатор для уроков и курсов
    """
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения количества элементов на странице
    max_page_size = 15  # Максимальное количество элементов на странице
