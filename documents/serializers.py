from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'content', 'original_name', 'size', 'content_type']
        read_only_fields = ['original_name', 'size', 'content_type']