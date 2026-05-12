from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model

from documents.models import Document, UploadStatus
from documents.models.audit_log import AuditLog, AuditAction
from documents.services import AuditLoggerService, DocumentService
from documents.models import Document, UploadStatus

User = get_user_model()

@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class DocumentAPITests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pw1', role='ADMIN')
        self.viewer = User.objects.create_user(username='viewer', password='pw2', role='VIEWER')

        self.doc1 = Document.objects.create(
            original_name="Q1_Report.pdf",
            size=1024,
            upload_status=UploadStatus.COMPLETED
        )

        self.list_url = reverse('document-list')

    def test_viewer_can_read_but_cannot_create(self):
        self.client.force_authenticate(user=self.viewer)

        response_get = self.client.get(self.list_url)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)

        fake_file = SimpleUploadedFile("test.pdf", b"dummy_content", content_type="application/pdf")
        response_post = self.client.post(self.list_url, {'content': fake_file}, format='multipart')
        
        self.assertEqual(response_post.status_code, status.HTTP_403_FORBIDDEN)

    @patch('documents.views.transfer_to_object_storage.delay')
    @patch('documents.storage.tmp_storage.save')
    def test_admin_upload_triggers_celery_and_returns_202(self, mock_storage_save, mock_celery_delay):
        self.client.force_authenticate(user=self.admin)
        
        mock_storage_save.return_value = "stage_mocked_uuid.pdf"

        fake_file = SimpleUploadedFile("new_architecture.pdf", b"heavy_file_data", content_type="application/pdf")
        
        response = self.client.post(self.list_url, {'content': fake_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        
        new_doc = Document.objects.get(original_name="new_architecture.pdf")
        self.assertEqual(new_doc.upload_status, UploadStatus.PENDING)

        mock_celery_delay.assert_called_once_with(new_doc.id)

    def test_document_list_is_cached(self):
        """Ensure the custom decorator caches the JSON response."""
        self.client.force_authenticate(user=self.admin)

        response1 = self.client.get(self.list_url)
        self.assertEqual(len(response1.data['results']), 1) 

        Document.objects.create(original_name="Invisible.pdf", size=500, upload_status=UploadStatus.COMPLETED)
        response2 = self.client.get(self.list_url)
        self.assertEqual(len(response2.data['results']), 1)

        from django.core.cache import cache
        cache.clear()
        
        response3 = self.client.get(self.list_url)
        self.assertEqual(len(response3.data['results']), 2)


class AuditLoggerServiceTests(TestCase):
    def setUp(self):
        self.system_admin = User.objects.create_user(
            username='admin_logger', 
            password='pw', 
            role='ADMIN'
        )
        self.document = Document.objects.create(
            original_name="audit_test.pdf",
            size=500,
            upload_status=UploadStatus.COMPLETED
        )

    @patch('documents.services.audit_log_services.async_to_sync')
    @patch('documents.services.audit_log_services.get_channel_layer')
    def test_log_action_creates_db_record_and_broadcasts_websocket(self, mock_get_channel, mock_async_to_sync):
        """Ensure logging creates a DB entry and triggers a real-time notification."""
        
        mock_layer = MagicMock()
        mock_get_channel.return_value = mock_layer

        AuditLoggerService.log_action(
            user=self.system_admin,
            document=self.document,
            action=AuditAction.CREATED.value,
            metadata={"note": "Test upload"}
        )

        self.assertEqual(AuditLog.objects.count(), 1)
        log = AuditLog.objects.first()
        self.assertEqual(log.user, self.system_admin)
        self.assertEqual(log.document, self.document)
        self.assertEqual(log.action, AuditAction.CREATED.value)
        self.assertEqual(log.metadata, {"note": "Test upload"})

        mock_async_to_sync.assert_called_once()


class DocumentServiceTests(TestCase):
    def setUp(self):
        self.uploader = User.objects.create_user(
            username='uploader', 
            password='pw', 
            role='ADMIN'
        )
        
        DocumentService._instance = None
        self.service = DocumentService()

    @patch('documents.storage.tmp_storage.save')
    def test_stage_document_extracts_metadata_and_spools_file(self, mock_tmp_save):
        
        mock_tmp_save.return_value = "stage_fake_uuid.pdf"
        
        fake_file = SimpleUploadedFile("financials.pdf", b"fake_binary_data", content_type="application/pdf")

        document = self.service.stage_document(user=self.uploader, file=fake_file)

        self.assertEqual(document.original_name, "financials.pdf")
        self.assertEqual(document.size, len(b"fake_binary_data"))
        self.assertEqual(document.staging_path, "stage_fake_uuid.pdf")
        self.assertEqual(document.upload_status, UploadStatus.PENDING)
        self.assertIsNotNone(document.id)

    @patch('documents.storage.tmp_storage.delete')
    @patch('documents.storage.tmp_storage.exists')
    @patch('documents.storage.tmp_storage.open')
    @patch('django.db.models.fields.files.FieldFile.save') 
    def test_process_to_minio_uploads_and_cleans_up(self, mock_minio_save, mock_tmp_open, mock_tmp_exists, mock_tmp_delete):
        """Ensure the background processor moves the file to MinIO and deletes the local copy."""
        
        pending_doc = Document.objects.create(
            original_name="stuck.pdf",
            staging_path="stage_stuck.pdf",
            upload_status=UploadStatus.PENDING
        )

        mock_tmp_exists.return_value = True
        mock_file_context = MagicMock()
        mock_tmp_open.return_value.__enter__.return_value = mock_file_context

        self.service.process_to_minio(pending_doc.id)

        pending_doc.refresh_from_db()

        mock_minio_save.assert_called_once()

        self.assertEqual(pending_doc.upload_status, UploadStatus.COMPLETED)
        

        mock_tmp_delete.assert_called_once_with("stage_stuck.pdf")