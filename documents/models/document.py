from django.db import models, transaction

from documents.models.audit_log import AuditAction, AuditLog
import os
import uuid
import datetime

def _upload_to(instance, filename):

    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    now = datetime.datetime.now()
    
    return f"documents/{now:%Y/%m/%d}/{unique_filename}"


class UploadStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending in Staging'
    PROCESSING = 'PROCESSING', 'Uploading to MinIO'
    COMPLETED = 'COMPLETED', 'Available in MinIO'
    FAILED = 'FAILED', 'Upload Failed'


class Document(models.Model):
    content = models.FileField(upload_to=_upload_to, blank=True, null=True)
    original_name = models.CharField(max_length=255, blank=True)
    size = models.PositiveIntegerField(editable=False, default=0)
    content_type = models.CharField(max_length=100, blank=True)

    staging_path = models.CharField(max_length=512, blank=True)
    
    upload_status = models.CharField(
        max_length=31, 
        choices=UploadStatus.choices, 
        default=UploadStatus.PENDING
    )

    def save(self, user=None, *args, **kwargs):
        is_new = self.pk is None
        action = AuditAction.CREATED if is_new else AuditAction.UPDATED
        
        if self.content:
            if not self.original_name:
                self.original_name = self.content.name.split("/")[-1]
            if not self.content_type:
                self.content_type = getattr(
                    self.content.file, "content_type", "application/octet-stream"
                )
            if not self.size:
                self.size = self.content.size

        with transaction.atomic():
            super().save(*args, **kwargs)

            # Import lazily to avoid circular import during app initialization.
            from documents.services import AuditLoggerService

            transaction.on_commit(
                lambda: AuditLoggerService.log_action(
                    user=user,
                    document=self,
                    action=action,
                    metadata={"note": "System generated"} if not user else {},
                )
            )

    def __str__(self):
        return self.original_name or f"Document {self.id}"
