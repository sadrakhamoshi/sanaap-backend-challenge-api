from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ['id', 'content', 'original_name', 'size', 'content_type']
        read_only_fields = ['original_name', 'size', 'content_type']

    
    def create(self, validated_data):
        user = self.context['request'].user
        instance = Document(**validated_data)
        instance.save(user=user)
        
        return instance

    def update(self, instance, validated_data):
        user = self.context['request'].user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save(user=user)
        
        return instance