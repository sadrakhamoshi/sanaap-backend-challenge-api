from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'download_url', 'original_name', 'size', 'content_type']
        read_only_fields = ['original_name', 'size', 'content_type']

    def get_download_url(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            return obj.file.url
        return None