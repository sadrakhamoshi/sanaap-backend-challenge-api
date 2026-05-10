from rest_framework import viewsets
from documents.models import Document
from documents.serializers import DocumentSerializer
from rest_framework.permissions import IsAuthenticated
from documents.permissions import DocumentRolePermission


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    permission_classes = [IsAuthenticated, DocumentRolePermission]