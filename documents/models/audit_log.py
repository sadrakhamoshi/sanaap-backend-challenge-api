from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    CREATED = "CREATED", "Created"
    UPDATED = "UPDATED", "Updated"
    DELETED = "DELETED", "Deleted"


class AuditLog(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True,)
    document = models.ForeignKey("documents.Document", on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=AuditAction.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["document", "action"]),
        ]

    def __str__(self):
        return f"{self.user} {self.action} Document {self.document_id} at {self.timestamp}"
