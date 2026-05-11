from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from documents.models import AuditLog, Document

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