import logging
from pathlib import Path
from uuid import uuid4
from django.core.files.base import ContentFile
from documents.models import Document, UploadStatus
from documents.storage import tmp_storage

logger = logging.getLogger(__name__)

class DocumentService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DocumentService, cls).__new__(cls)
        return cls._instance

    def stage_document(self, user, file) -> Document:
        suffix = Path(file.name).suffix.lower()
        unique_name = f"stage_{uuid4().hex}{suffix}"
        tmp_path = tmp_storage.save(unique_name, ContentFile(file.read()))
        
        original_name = file.name
        size = file.size
        content_type = getattr(file, "content_type", "application/octet-stream")

        document = Document(
            original_name=original_name,
            size=size,
            content_type=content_type,
            staging_path=tmp_path,
            upload_status=UploadStatus.PENDING,
        )
        document.save(user=user)

        logger.info(f"Document {document.id} staged successfully at {tmp_path}")
        return document

    def process_to_minio(self, document_id: int) -> None:
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            logger.error(f"Document {document_id} not found, skipping MinIO upload.")
            return

        document.upload_status = UploadStatus.PROCESSING
        document.save(update_fields=['upload_status'])

        try:
            with tmp_storage.open(document.staging_path, 'rb') as f:
                dest_name = f"documents/{Path(document.staging_path).name}"
                document.content.save(dest_name, f, save=False)
            
            document.upload_status = UploadStatus.COMPLETED
            old_staging_path = document.staging_path
            document.save(update_fields=["upload_status", "content", "staging_path"])

            if tmp_storage.exists(old_staging_path):
                tmp_storage.delete(old_staging_path)
                
            logger.info(f"Document {document_id} successfully uploaded to MinIO.")

        except Exception as e:
            document.upload_status = UploadStatus.FAILED
            document.save(update_fields=["upload_status"])
            logger.exception(f"Failed to upload document {document_id} to MinIO: {e}")
            raise e