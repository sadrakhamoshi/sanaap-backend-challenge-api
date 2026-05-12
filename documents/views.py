from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils.decorators import method_decorator

from documents.decorators import custom_cache_decorator
from documents.models import Document
from documents.serializers import DocumentSerializer
from documents.permissions import DocumentRolePermission
from documents.paginations import DocumentPagination
from documents.filters import DocumentFilter

from documents.services import DocumentService
from documents.tasks import transfer_to_object_storage


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-id') 
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, DocumentRolePermission]
    
    pagination_class = DocumentPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_class = DocumentFilter
    
    search_fields = ['original_name', 'content_type']

    @custom_cache_decorator(timeout=60 * 15)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = DocumentService()

        document = service.stage_document(
            user=request.user,
            file=serializer.validated_data['content']
        )

        transfer_to_object_storage.delay(document.id)

        response_serializer = self.get_serializer(document)
        return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)