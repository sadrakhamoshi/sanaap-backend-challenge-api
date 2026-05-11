from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


def _upload_to(instance, filename):
    import datetime
    now = datetime.datetime.now()
    return f'documents/{now:%Y/%m/%d}/{filename}'

class Document(models.Model):
    content = models.FileField(upload_to=_upload_to, storage=S3Boto3Storage())
    original_name = models.CharField(max_length=255, blank=True)
    size = models.PositiveIntegerField(editable=False, default=0)
    content_type = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if self.content:
            self.original_name = self.content.name.split('/')[-1]
            self.content_type = getattr(self.content.file, 'content_type', 'application/octet-stream')
        super().save(*args, **kwargs)

        if self.content and not self.size:
            self.size = self.content.size
            super().save(update_fields=['size'])

    def __str__(self):
        return self.original_name or f"Document {self.id}"