from django.db.models import Q

from .models import Product


def process_search_products(keyword):
    queryset = Product.objects.all()

    if keyword:
        keyword = keyword.strip()
        filters = Q(name__icontains=keyword)

        code_value = keyword.upper().removeprefix("VAI-").removeprefix("VAI")
        if code_value.isdigit():
            filters |= Q(pk=int(code_value))

        queryset = queryset.filter(filters)

    return queryset.order_by("name")