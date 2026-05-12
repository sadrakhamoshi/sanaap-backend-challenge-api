import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# Ensure the staging directory exists on the local disk
STAGING_DIR = os.path.join(settings.BASE_DIR, 'staging')
os.makedirs(STAGING_DIR, exist_ok=True)

# Fast local storage used strictly as a spooling area
tmp_storage = FileSystemStorage(location=STAGING_DIR)