from google.cloud import storage
from config.settings import GOOGLE_CLOUD_STORAGE_BUCKET
import uuid

class CloudStorageService:
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(GOOGLE_CLOUD_STORAGE_BUCKET)

    def upload_file(self, file_content, content_type):
        file_id = str(uuid.uuid4())
        blob = self.bucket.blob(file_id)
        blob.upload_from_string(file_content, content_type=content_type)
        return file_id

    def get_file(self, file_id):
        blob = self.bucket.blob(file_id)
        return blob.download_as_bytes()