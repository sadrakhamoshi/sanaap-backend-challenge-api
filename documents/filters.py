import django_filters
from documents.models import Document

class DocumentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='original_name', lookup_expr='icontains')
    content_type = django_filters.CharFilter(field_name='content_type', lookup_expr='exact')
    min_size = django_filters.NumberFilter(field_name='size', lookup_expr='gte')
    max_size = django_filters.NumberFilter(field_name='size', lookup_expr='lte')

    class Meta:
        model = Document
        fields = ['name', 'content_type', 'min_size', 'max_size']
   