from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from documents.models import AuditAction, AuditLog, Document
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()

class AuditLoggerService:
    @classmethod
    def log_action(cls, user: User, document: "Document", action: str, metadata: Optional[Dict[str, Any]] = None):
        if metadata is None:
            metadata = {}

        AuditLog.objects.create(
            user=user,
            document=document,
            action=action,
            metadata=metadata
        )
        if action == AuditAction.CREATED.value:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "admin_notifications",
                {
                    "type": "send_notification", 
                    "payload": {
                        "event": "DOCUMENT_UPLOADED",
                        "document_id": document.id,
                        "document_name": document.original_name,
                        "uploaded_by": user.username if user else "System",
                        "size": document.size
                    }
                }
            )