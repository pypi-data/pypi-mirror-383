# coding: utf-8
from m3_django_compatibility import get_request_params


def get_is_filter_params(request):
    u"""
    Возврашет признак наличия фильтров в запросе.

    Включая колоночные фильтры, filter_{n}, n-порядковый номер фильтра
    """

    for key in get_request_params(request):
        if key.startswith('filter'):
            return True
    return False
