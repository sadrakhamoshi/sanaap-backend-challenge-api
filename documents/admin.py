from django.contrib import admin
from .models import Document


from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'original_name', 'content_type', 'size_display',]
    readonly_fields = ['size']

    def size_display(self, obj):
        """Human-readable file size."""
        if obj.size < 1024:
            return f"{obj.size} B"
        elif obj.size < 1024 * 1024:
            return f"{obj.size / 1024:.1f} KB"
        elif obj.size < 1024 * 1024 * 1024:
            return f"{obj.size / (1024 * 1024):.1f} MB"
        else:
            return f"{obj.size / (1024 * 1024 * 1024):.1f} GB"

    size_display.short_description = "Size"

from .models import AuditLog  # Assuming the model is named AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AuditLog._meta.fields]
    readonly_fields = [field.name for field in AuditLog._meta.fields]
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False