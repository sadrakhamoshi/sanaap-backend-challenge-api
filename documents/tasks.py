import logging
from celery import shared_task
from .services import DocumentService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def transfer_to_object_storage(self, document_id: int):
    logger.info(f"Background task started for document {document_id}")
    
    service = DocumentService()
    try:
        service.process_to_minio(document_id)
    except Exception as exc:
        logger.error(f"Task failed, retrying... {exc}")
        raise self.retry(exc=exc)