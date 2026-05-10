from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from documents.models import Document
from documents.serializers import DocumentSerializer
from documents.permissions import DocumentRolePermission
from documents.paginations import DocumentPagination
from documents.filters import DocumentFilter

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-id') 
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, DocumentRolePermission]
    
    pagination_class = DocumentPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_class = DocumentFilter
    
    search_fields = ['original_name', 'content_type']