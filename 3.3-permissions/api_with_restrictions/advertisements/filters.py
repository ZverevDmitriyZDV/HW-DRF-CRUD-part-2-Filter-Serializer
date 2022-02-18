import django_filters
from django_filters import rest_framework as filters, DateFromToRangeFilter

from advertisements.models import Advertisement


class CharFilterInFilter(filters.BaseInFilter,filters.CharFilter):
    pass


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""
    created_at = DateFromToRangeFilter()
    status = filters.CharFilter()
    creator = CharFilterInFilter(field_name='creator_id')

    class Meta:
        model = Advertisement
        fields = ['created_at', 'status','creator']
