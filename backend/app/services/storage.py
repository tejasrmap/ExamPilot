import os
import logging
import httpx
from typing import Dict, Any, Optional
from backend.app.core.config import settings

logger = logging.getLogger("exampilot.storage")

class BaseStorageService:
    def save_file(self, user_id: str, document_id: str, filename: str, content_bytes: bytes, content_type: str = "application/pdf") -> Dict[str, str]:
        raise NotImplementedError

    def delete_file(self, storage_provider: str, storage_key: Optional[str], storage_path: Optional[str]) -> bool:
        raise NotImplementedError

    def get_download_url(self, storage_provider: str, storage_key: Optional[str], storage_path: Optional[str], expires_in: int = 3600) -> str:
        raise NotImplementedError

class LocalStorageService(BaseStorageService):
    """
    Local filesystem storage provider for development, tests, and self-hosted persistent hosts.
    Ensures safe user-isolated pathing.
    """
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or settings.STORAGE_LOCAL_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    def save_file(self, user_id: str, document_id: str, filename: str, content_bytes: bytes, content_type: str = "application/pdf") -> Dict[str, str]:
        # User-isolated directory
        user_dir = os.path.join(self.base_dir, user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        # Safe deterministic filename
        safe_ext = os.path.splitext(filename)[1].lower() or ".pdf"
        storage_key = f"documents/{user_id}/{document_id}{safe_ext}"
        storage_path = os.path.join(user_dir, f"{document_id}{safe_ext}")

        with open(storage_path, "wb") as f:
            f.write(content_bytes)

        return {
            "storage_provider": "local",
            "storage_key": storage_key,
            "storage_path": storage_path
        }

    def delete_file(self, storage_provider: str, storage_key: Optional[str], storage_path: Optional[str]) -> bool:
        if storage_path and os.path.exists(storage_path):
            try:
                os.remove(storage_path)
                return True
            except Exception as e:
                logger.error(f"Failed to delete local document {storage_path}: {str(e)}")
                return False
        return True

    def get_download_url(self, storage_provider: str, storage_key: Optional[str], storage_path: Optional[str], expires_in: int = 3600) -> str:
        # Returns local API download path
        return f"/api/documents/download?key={storage_key}"

class SupabaseStorageService(BaseStorageService):
    """
    Production durable storage provider leveraging Supabase Storage private buckets.
    Enforces user tenant isolation and signed URL access.
    """
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL.rstrip("/")
        self.bucket = settings.SUPABASE_STORAGE_BUCKET
        self.auth_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY

    def save_file(self, user_id: str, document_id: str, filename: str, content_bytes: bytes, content_type: str = "application/pdf") -> Dict[str, str]:
        safe_ext = os.path.splitext(filename)[1].lower() or ".pdf"
        storage_key = f"documents/{user_id}/{document_id}{safe_ext}"
        upload_url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{storage_key}"

        headers = {
            "Authorization": f"Bearer {self.auth_key}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(upload_url, headers=headers, content=content_bytes)
                if res.status_code not in (200, 201):
                    logger.error(f"Supabase storage upload failed ({res.status_code}): {res.text}")
                    # Fallback to local on connection refusal in non-production environments
                    if getattr(settings, "ENVIRONMENT", "development").lower() != "production":
                        return LocalStorageService().save_file(user_id, document_id, filename, content_bytes, content_type)
                    raise RuntimeError(f"Storage upload failed: {res.text}")
        except Exception as e:
            logger.error(f"Supabase storage exception: {str(e)}")
            if getattr(settings, "ENVIRONMENT", "development").lower() != "production":
                return LocalStorageService().save_file(user_id, document_id, filename, content_bytes, content_type)
            raise RuntimeError(f"Failed to upload document to storage: {str(e)}")

        return {
            "storage_provider": "supabase",
            "storage_key": storage_key,
            "storage_path": upload_url
        }

    def delete_file(self, storage_provider: str, storage_key: Optional[str], storage_path: Optional[str]) -> bool:
        if not storage_key:
            return True
        delete_url = f"{self.supabase_url}/storage/v1/object/{self.bucket}"
        headers = {
            "Authorization": f"Bearer {self.auth_key}",
            "Content-Type": "application/json"
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.request("DELETE", delete_url, headers=headers, json={"prefixes": [storage_key]})
                return res.status_code == 200
        except Exception as e:
            logger.error(f"Failed to delete Supabase storage object {storage_key}: {str(e)}")
            return False

    def get_download_url(self, storage_provider: str, storage_key: Optional[str], storage_path: Optional[str], expires_in: int = 3600) -> str:
        if not storage_key:
            return ""
        sign_url = f"{self.supabase_url}/storage/v1/object/sign/{self.bucket}/{storage_key}"
        headers = {
            "Authorization": f"Bearer {self.auth_key}",
            "Content-Type": "application/json"
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(sign_url, headers=headers, json={"expiresIn": expires_in})
                if res.status_code == 200:
                    signed_path = res.json().get("signedURL", "")
                    return f"{self.supabase_url}/storage/v1{signed_path}"
        except Exception as e:
            logger.error(f"Failed to create signed URL for {storage_key}: {str(e)}")
        return ""

def get_storage_service() -> BaseStorageService:
    prov = getattr(settings, "STORAGE_PROVIDER", "local").lower()
    if prov == "supabase":
        return SupabaseStorageService()
    return LocalStorageService()

storage_service = get_storage_service()

